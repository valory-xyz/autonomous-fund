# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2022 Valory AG
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

from typing import Generator, Set, Type, cast, Optional, List, Dict

from packages.balancer.contracts.managed_pool.contract import ManagedPoolContract
from packages.valory.protocols.contract_api import ContractApiMessage
from packages.valory.skills.abstract_round_abci.base import AbstractRound
from packages.valory.skills.abstract_round_abci.behaviours import (
    AbstractRoundBehaviour,
    BaseBehaviour,
)

from packages.balancer.skills.liquidity_provision_abci.models import Params
from packages.balancer.skills.liquidity_provision_abci.rounds import (
    SynchronizedData,
    LiquidityProvisionAbciApp,
    AllowListUpdateRound,
)
from packages.balancer.skills.liquidity_provision_abci.rounds import (
    AllowListUpdatePayload,
)

# setting the safe gas to 0 means that all available gas will be used
# which is what we want in most cases
# more info here: https://safe-docs.dev.gnosisdev.com/safe/docs/contracts_tx_execution/
SAFE_GAS = 0

class LiquidityProvisionBaseBehaviour(BaseBehaviour):
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
            payload = AllowListUpdatePayload(sender=self.context.agent_address, allow_list_update=update_payload)

        with self.context.benchmark_tool.measure(self.behaviour_id).consensus():
            yield from self.send_a2a_transaction(payload)
            yield from self.wait_until_round_end()

        self.set_done()

    def get_allow_list_update(self) -> Generator[None, None, str]:
        """
        Checks whether the pool is running with the correct LP allowlist params, if not it prepares a (multisend) tx to update it.

        There are two parameters we need to take into consideration.
        1.  Whether an allowlist for LPs should be enforced.
        2.  Whether the allowlist is the same as the local one.

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

        required_updates = yield from self._get_required_update_txs(current_allowlist, is_allowlist_enforced)
        if required_updates is None:
            # an error was encountered while checking and preparing txs for the required updates
            return AllowListUpdateRound.NoUpdatePayloads.ERROR_PAYLOAD.value

        if len(required_updates) == 0:
            # no updates are required
            self.context.logger.info("No updates to the allowlist are required.")
            return AllowListUpdateRound.NoUpdatePayloads.NO_UPDATE_PAYLOAD.value



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
                f"Couldn't whether the pool is configured to enforce an allowlist from IManagedPool.get_must_allowlist_lps. "
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
                f"Couldn't get weight update params from IManagedPool.get_allowlist. "
                f"Expected response performative {ContractApiMessage.Performative.STATE.value}, "  # type: ignore
                f"received {response.performative.value}."
            )
            return None

        params = cast(Optional[List[str]], response.state.body.get("allowlist", None))
        return params

    def _get_required_update_txs(self, current_allowlist: List[str], is_allowlist_currently_enforced: bool) -> Generator[None, None, Optional[List[Dict]]]:
        """Returns the required update txs to be made."""
        # TODO: add docstring about multisend

        if self.params.enforce_allowlist != is_allowlist_currently_enforced:
            ...

        current_set, required_set = set(current_allowlist), set(self.params.allowed_lp_addresses)
        members_to_be_removed = current_set - required_set
        members_to_be_added = required_set - current_set

        for member in members_to_be_removed:
            # TODO: convert set to list and sort it
            ...

        for member in members_to_be_added:
            # TODO: convert set to list and sort it
            ...
        return None
        yield
class LiquidityProvisionRoundBehaviour(AbstractRoundBehaviour):
    """LiquidityProvisionRoundBehaviour"""

    initial_behaviour_cls = AllowListUpdateBehaviour
    abci_app_cls = LiquidityProvisionAbciApp  # type: ignore
    behaviours: Set[Type[BaseBehaviour]] = [AllowListUpdateBehaviour]
