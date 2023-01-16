# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2022-2023 Valory AG
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""This package contains round behaviours of LiquidityProvisionAbciApp."""
from abc import ABC
from typing import Any, Dict, Generator, List, Optional, Set, Type, cast

from hexbytes import HexBytes

from packages.balancer.contracts.managed_pool.contract import ManagedPoolContract
from packages.balancer.skills.liquidity_provision_abci.models import Params
from packages.balancer.skills.liquidity_provision_abci.rounds import (
    AllowListUpdatePayload,
    AllowListUpdateRound,
    LiquidityProvisionAbciApp,
    SynchronizedData,
)
from packages.valory.contracts.gnosis_safe.contract import (
    GnosisSafeContract,
    SafeOperation,
)
from packages.valory.contracts.multisend.contract import (
    MultiSendContract,
    MultiSendOperation,
)
from packages.valory.protocols.contract_api import ContractApiMessage
from packages.valory.skills.abstract_round_abci.base import AbstractRound
from packages.valory.skills.abstract_round_abci.behaviours import (
    AbstractRoundBehaviour,
    BaseBehaviour,
)
from packages.valory.skills.transaction_settlement_abci.payload_tools import (
    hash_payload_to_hex,
)


# setting the safe gas to 0 means that all available gas will be used
# which is what we want in most cases
# more info here: https://safe-docs.dev.gnosisdev.com/safe/docs/contracts_tx_execution/
SAFE_GAS = 0

# hardcoded to 0 because we don't need to send any ETH when performing txs in this behaviour
ETHER_VALUE = 0


class LiquidityProvisionBaseBehaviour(BaseBehaviour, ABC):
    """Base behaviour for the common apps' skill."""

    @property
    def synchronized_data(self) -> SynchronizedData:
        """Return the synchronized data."""
        return cast(SynchronizedData, super().synchronized_data)

    @property
    def params(self) -> Params:
        """Return the params."""
        return cast(Params, super().params)


class AllowListUpdateBehaviour(LiquidityProvisionBaseBehaviour):
    """AllowListUpdateBehaviour"""

    matching_round: Type[AbstractRound] = AllowListUpdateRound

    def async_act(self) -> Generator:
        """Do the act, supporting asynchronous execution."""

        with self.context.benchmark_tool.measure(self.behaviour_id).local():
            update_payload = yield from self.get_allow_list_update()
            payload = AllowListUpdatePayload(
                sender=self.context.agent_address, allow_list_update=update_payload
            )

        with self.context.benchmark_tool.measure(self.behaviour_id).consensus():
            yield from self.send_a2a_transaction(payload)
            yield from self.wait_until_round_end()

        self.set_done()

    def get_allow_list_update(self) -> Generator[None, None, str]:
        """
        Checks whether the pool is running with the correct LP allowlist params, if not it prepares a (multisend) tx to update it.

        There are two parameters we need to take into consideration.
        1.  Whether an allowlist for LPs should be enforced.
        2.  Whether the current allowlist in the pool is the same as the one the agent has been configured with.

        Note that if the allowlist is not being enforced, any address will be allowed to provide liqudity, regardless of
        whether they are on the allowlist or not.

        :return: the payload, tx data if an update is required, a "special" payload if otherwise.
        """
        is_allowlist_enforced = yield from self._is_allowlist_enforced()
        if is_allowlist_enforced is None:
            # an error was encountered if this is None
            return AllowListUpdateRound.NoUpdatePayloads.ERROR_PAYLOAD.value

        current_allowlist = yield from self._get_current_allowlist()
        if current_allowlist is None:
            # an error was encountered if the allowlist is None
            return AllowListUpdateRound.NoUpdatePayloads.ERROR_PAYLOAD.value

        required_updates = yield from self._get_required_update_txs(
            current_allowlist, is_allowlist_enforced
        )
        if required_updates is None:
            # an error was encountered while checking and preparing txs for the required updates
            return AllowListUpdateRound.NoUpdatePayloads.ERROR_PAYLOAD.value

        if len(required_updates) == 0:
            # no updates are required
            self.context.logger.info("No updates to the allowlist are required.")
            return AllowListUpdateRound.NoUpdatePayloads.NO_UPDATE_PAYLOAD.value

        payload_data = yield from self._get_multisend_tx(required_updates)
        if payload_data is None:
            # an error was encountered while prepared
            return AllowListUpdateRound.NoUpdatePayloads.ERROR_PAYLOAD.value
        return payload_data

    def _is_allowlist_enforced(self) -> Generator[None, None, Optional[bool]]:
        """Returns whether the pool is configured to enforce an allowlist."""
        response = yield from self.get_contract_api_response(
            performative=ContractApiMessage.Performative.GET_STATE,  # type: ignore
            contract_id=str(ManagedPoolContract.contract_id),
            contract_callable="get_must_allowlist_lps",
            contract_address=self.params.managed_pool_address,
        )

        if response.performative != ContractApiMessage.Performative.STATE:
            self.context.logger.error(
                f"Couldn't check whether the pool is configured to enforce an allowlist via IManagedPool.get_must_allowlist_lps. "
                f"Expected response performative {ContractApiMessage.Performative.STATE.value}, "  # type: ignore
                f"received {response.performative.value}."
            )
            return None

        params = cast(Optional[bool], response.state.body.get("is_enforced", None))
        return params

    def _get_current_allowlist(self) -> Generator[None, None, Optional[List[str]]]:
        """Returns the current allow-list the pool has."""
        response = yield from self.get_contract_api_response(
            performative=ContractApiMessage.Performative.GET_STATE,  # type: ignore
            contract_id=str(ManagedPoolContract.contract_id),
            contract_callable="get_allowlist",
            contract_address=self.params.managed_pool_address,
        )

        if response.performative != ContractApiMessage.Performative.STATE:
            self.context.logger.error(
                f"Couldn't get allowlist from IManagedPool.get_allowlist. "
                f"Expected response performative {ContractApiMessage.Performative.STATE.value}, "  # type: ignore
                f"received {response.performative.value}."
            )
            return None

        params = cast(Optional[List[str]], response.state.body.get("allowlist", None))
        return params

    def _get_required_update_txs(
        self, current_allowlist: List[str], is_allowlist_currently_enforced: bool
    ) -> Generator[None, None, Optional[List[bytes]]]:
        """Returns the required update txs to be made."""

        transactions: List[bytes] = []
        if self.params.enforce_allowlist != is_allowlist_currently_enforced:
            self.context.logger.info(
                "A tx to change the allowlist enforcing should be made."
            )
            tx_data = yield from self._set_must_allowlist_lps_tx(
                self.params.enforce_allowlist
            )
            if tx_data is None:
                # something went wrong,
                # we cancel the whole update
                return None
            transactions.append(tx_data)

        current_set, required_set = set(current_allowlist), set(
            self.params.allowed_lp_addresses
        )
        members_to_be_removed = list(current_set - required_set)
        members_to_be_added = list(required_set - current_set)

        # we sort the addresses to ensure that
        # the resulting tx is the same in all the agents
        # there is no guarantee that simply calling list(set)
        # will result in the same order of elements across the
        # agent instances
        members_to_be_added.sort()
        members_to_be_removed.sort()

        for member in members_to_be_removed:
            self.context.logger.info(
                f"Member with address {member} should be removed from the allowlist."
            )
            tx_data = yield from self._get_remove_allowed_address_tx(member)
            if tx_data is None:
                # something went wrong,
                # we cancel the whole update
                return None
            transactions.append(tx_data)

        for member in members_to_be_added:
            self.context.logger.info(
                f"Member with address {member} should be added to the allowlist."
            )
            tx_data = yield from self._get_add_allowed_address_tx(member)
            if tx_data is None:
                # something went wrong,
                # we cancel the whole update
                return None
            transactions.append(tx_data)

        return transactions

    def _set_must_allowlist_lps_tx(
        self, enforce_allowlist: bool
    ) -> Generator[None, None, Optional[bytes]]:
        """
        A method that prepares a IManagedPool.setMustAllowlistLPs() tx.

        This tx is used to change whether the allowlist is enforced or not. In the ManagedPoolContract we have defined
        a method (get_set_must_allowlist_lps_tx) that acts as a wrapper and takes care of this encoding for us.
        Here we are responsible for simply calling it with the right arguments.

        :returns: byte encoded setMustAllowlistLPs() call
        """
        response = yield from self.get_contract_api_response(
            performative=ContractApiMessage.Performative.GET_STATE,  # type: ignore
            contract_id=str(ManagedPoolContract.contract_id),
            contract_callable="get_set_must_allowlist_lps_tx",
            contract_address=self.params.managed_pool_address,
            must_allowlist_lps=enforce_allowlist,
        )
        if response.performative != ContractApiMessage.Performative.STATE:
            self.context.logger.error(
                f"Couldn't get tx data for IManagedPool.setMustAllowlistLPs(). "
                f"Expected response performative {ContractApiMessage.Performative.STATE.value}, "  # type: ignore
                f"received {response.performative.value}."
            )
            return None

        # strip "0x" from the response data
        data_str = cast(str, response.state.body["data"])[2:]
        data = bytes.fromhex(data_str)
        return data

    def _get_add_allowed_address_tx(
        self, member: str
    ) -> Generator[None, None, Optional[bytes]]:
        """
        A method that prepares a IManagedPool.addAllowedAddress() tx.

        This tx is used to change whether the allowlist is enforced or not. In the ManagedPoolContract we have defined
        a method (get_add_allowed_address_data) that acts as a wrapper and takes care of this encoding for us.
        Here we are responsible for simply calling it with the right arguments.

        :returns: byte encoded addAllowedAddress() call
        """
        response = yield from self.get_contract_api_response(
            performative=ContractApiMessage.Performative.GET_STATE,  # type: ignore
            contract_id=str(ManagedPoolContract.contract_id),
            contract_callable="get_add_allowed_address_data",
            contract_address=self.params.managed_pool_address,
            member=member,
        )
        if response.performative != ContractApiMessage.Performative.STATE:
            self.context.logger.error(
                f"Couldn't get tx data for IManagedPool.addAllowedAddress(). "
                f"Expected response performative {ContractApiMessage.Performative.STATE.value}, "  # type: ignore
                f"received {response.performative.value}."
            )
            return None

        # strip "0x" from the response data
        data_str = cast(str, response.state.body["data"])[2:]
        data = bytes.fromhex(data_str)
        return data

    def _get_remove_allowed_address_tx(
        self, member: str
    ) -> Generator[None, None, Optional[bytes]]:
        """
        A method that prepares a IManagedPool.removeAllowedAddress() tx.

        This tx is used to change whether the allowlist is enforced or not. In the ManagedPoolContract we have defined
        a method (get_remove_allowed_address_data) that acts as a wrapper and takes care of this encoding for us.
        Here we are responsible for simply calling it with the right arguments.

        :returns: byte encoded removeAllowedAddress() call
        """
        response = yield from self.get_contract_api_response(
            performative=ContractApiMessage.Performative.GET_STATE,  # type: ignore
            contract_id=str(ManagedPoolContract.contract_id),
            contract_callable="get_remove_allowed_address_data",
            contract_address=self.params.managed_pool_address,
            member=member,
        )
        if response.performative != ContractApiMessage.Performative.STATE:
            self.context.logger.error(
                f"Couldn't get tx data for IManagedPool.removeAllowedAddress(). "
                f"Expected response performative {ContractApiMessage.Performative.STATE.value}, "  # type: ignore
                f"received {response.performative.value}."
            )
            return None

        # strip "0x" from the response data
        data_str = cast(str, response.state.body["data"])[2:]
        data = bytes.fromhex(data_str)
        return data

    def _get_safe_tx_hash(self, data: bytes) -> Generator[None, None, Optional[str]]:
        """
        Prepares and returns the safe tx hash.

        This hash will be signed later by the agents, and submitted to the safe contract.
        Note that this is the transaction that the safe will execute, with the provided data.

        :param data: the safe tx data. This is the data of the function being called, in this case `updateWeightGradually`.
        :return: the tx hash
        """
        response = yield from self.get_contract_api_response(
            performative=ContractApiMessage.Performative.GET_STATE,  # type: ignore
            contract_address=self.synchronized_data.safe_contract_address,
            contract_id=str(GnosisSafeContract.contract_id),
            contract_callable="get_raw_safe_transaction_hash",
            to_address=self.params.multisend_address,  # we send the tx to the multisend address
            value=ETHER_VALUE,
            data=data,
            safe_tx_gas=SAFE_GAS,
            operation=SafeOperation.DELEGATE_CALL.value,
        )

        if response.performative != ContractApiMessage.Performative.STATE:
            self.context.logger.error(
                f"Couldn't get safe hash. "
                f"Expected response performative {ContractApiMessage.Performative.STATE.value}, "  # type: ignore
                f"received {response.performative.value}."
            )
            return None

        # strip "0x" from the response hash
        tx_hash = cast(str, response.state.body["tx_hash"])[2:]
        return tx_hash

    def _get_multisend_tx(
        self, txs: List[bytes]
    ) -> Generator[None, None, Optional[str]]:
        """Given a list of transactions, bundle them together in a single multisend tx."""
        multi_send_txs = [self._to_multisend_format(tx) for tx in txs]
        response = yield from self.get_contract_api_response(
            performative=ContractApiMessage.Performative.GET_RAW_TRANSACTION,  # type: ignore
            contract_address=self.params.multisend_address,
            contract_id=str(MultiSendContract.contract_id),
            contract_callable="get_tx_data",
            multi_send_txs=multi_send_txs,
        )
        if response.performative != ContractApiMessage.Performative.RAW_TRANSACTION:
            self.context.logger.error(
                f"Couldn't compile the multisend tx. "
                f"Expected response performative {ContractApiMessage.Performative.RAW_TRANSACTION.value}, "  # type: ignore
                f"received {response.performative.value}."
            )
            return None

        # strip "0x" from the response
        multisend_data_str = cast(str, response.raw_transaction.body["data"])[2:]
        tx_data = bytes.fromhex(multisend_data_str)
        tx_hash = yield from self._get_safe_tx_hash(tx_data)
        if tx_hash is None:
            # something went wrong
            return None

        payload_data = hash_payload_to_hex(
            safe_tx_hash=tx_hash,
            ether_value=ETHER_VALUE,
            safe_tx_gas=SAFE_GAS,
            operation=SafeOperation.DELEGATE_CALL.value,
            to_address=self.params.multisend_address,
            data=tx_data,
        )
        return payload_data

    def _to_multisend_format(self, single_tx: bytes) -> Dict[str, Any]:
        """This method puts tx data from a single tx into the multisend format."""
        multisend_format = {
            "operation": MultiSendOperation.CALL,
            "to": self.params.managed_pool_address,
            "value": ETHER_VALUE,
            "data": HexBytes(single_tx),
        }
        return multisend_format


class LiquidityProvisionRoundBehaviour(AbstractRoundBehaviour):
    """LiquidityProvisionRoundBehaviour"""

    initial_behaviour_cls = AllowListUpdateBehaviour
    abci_app_cls = LiquidityProvisionAbciApp  # type: ignore
    behaviours: Set[Type[BaseBehaviour]] = {AllowListUpdateBehaviour}
