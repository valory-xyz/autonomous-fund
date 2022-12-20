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

"""This package contains round behaviours of PoolManagerAbciApp."""
import json
from typing import Any, Dict, Generator, List, Optional, Set, Tuple, Type, cast

from packages.balancer.contracts.managed_pool.contract import ManagedPoolContract
from packages.balancer.contracts.managed_pool_controller.contract import (
    ManagedPoolControllerContract,
)
from packages.balancer.skills.pool_manager_abci.models import Params, SharedState
from packages.balancer.skills.pool_manager_abci.payloads import (
    DecisionMakingPayload,
    UpdatePoolTxPayload,
)
from packages.balancer.skills.pool_manager_abci.rounds import (
    DecisionMakingRound,
    PoolManagerAbciApp,
    SynchronizedData,
    UpdatePoolTxRound,
)
from packages.valory.contracts.gnosis_safe.contract import GnosisSafeContract
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


class PoolManagerBaseBehaviour(BaseBehaviour):
    """Base behaviour for the common apps' skill."""

    @property
    def synchronized_data(self) -> SynchronizedData:
        """Return the synchronized data."""
        return cast(SynchronizedData, super().synchronized_data)

    @property
    def params(self) -> Params:
        """Return the params."""
        return cast(Params, super().params)

    @property
    def last_synced_timestamp(self) -> int:
        """
        Get last synced timestamp.

        This is the last timestamp guaranteed to be the same by 2/3 of the agents.
        :returns: the last synced timestamp.
        """
        state = cast(SharedState, self.context.state)
        last_timestamp = (
            state.round_sequence.last_round_transition_timestamp.timestamp()
        )
        return int(last_timestamp)


class DecisionMakingBehaviour(PoolManagerBaseBehaviour):
    """DecisionMakingBehaviour"""

    matching_round: Type[AbstractRound] = DecisionMakingRound

    def async_act(self) -> Generator:
        """Do the act, supporting asynchronous execution."""
        with self.context.benchmark_tool.measure(
            self.behaviour_id,
        ).local():
            decision = yield from self.get_decision()
            self.context.logger.info(f"Updated weights decision: {decision}")

        # at this point the agent has the data,
        # and shares it with the other agents (peers)
        with self.context.benchmark_tool.measure(
            self.behaviour_id,
        ).consensus():
            payload = DecisionMakingPayload(
                self.context.agent_address,
                decision,
            )
            yield from self.send_a2a_transaction(payload)
            yield from self.wait_until_round_end()

        self.set_done()

    def get_decision(self) -> Generator[None, None, str]:
        """
        Checks the weight in the pool, and decides whether an update is necessary or not.

        We only update in case the required change in the weights is greater than the configured tolerance AND
        there isn't an ongoing update with matching target weights.

        :return: the new weights in case they are needed, or a payload that defines the opposite.
        """
        new_weights = self._get_new_pool_weights()
        current_weights = yield from self._get_current_pool_weights()
        if current_weights is None:
            # we couldn't retrieve the current weights
            # we don't update the weights
            return DecisionMakingRound.NO_UPDATE_PAYLOAD

        num_tokens = len(current_weights)
        within_tolerance = all(
            abs(new_weights[i] - current_weights[i]) < self.params.weight_tolerance
            for i in range(num_tokens)
        )
        if within_tolerance:
            # the new weights were within the tolerance amount different from
            # what they currently are, so we don't update.
            return DecisionMakingRound.NO_UPDATE_PAYLOAD

        # the current weights are not what we want them to be, so we check whether there's
        # already an ongoing update aiming to set the weights that we need.
        params = yield from self._get_weight_update_params()
        if params is None:
            # we couldn't retrieve the params
            # we don't update the weights
            return DecisionMakingRound.NO_UPDATE_PAYLOAD

        # although we have access to the start time and weights, we only care about
        # the end result. We are interested to see whether the update is headed to
        # where we want it to go, we are not interested in the starting params.
        update_end_time = cast(int, params.get("end_time"))
        update_end_weights = cast(List[float], params.get("end_weights"))
        within_tolerance = all(
            abs(new_weights[i] - update_end_weights[i]) < self.params.weight_tolerance
            for i in range(num_tokens)
        )
        if update_end_time > self.last_synced_timestamp and within_tolerance:
            # there is an ongoing update, and its end weights are within
            # the tolerance amount different to the ones we want to set
            # so, we don't need to send an update tx
            return DecisionMakingRound.NO_UPDATE_PAYLOAD

        # the current weights need to be updated
        serialized_weights = json.dumps(dict(weights=new_weights), sort_keys=True)
        return serialized_weights

    def _get_new_pool_weights(self) -> List[int]:
        """Gets the pool weights from the latest estimation. We use these to update the pool with."""
        _, latest_value = json.loads(self.synchronized_data.most_voted_estimates)[
            "value_estimates"
        ]

        # we index intervals by their lower bound
        # given an interval [a, b], it's lower bound is a
        interval_lower_bounds = self.params.pool_weights.keys()
        interval_to_use = 0

        # we find the interval in which the node belongs to by checking
        # which is the greatest lower bound of the available intervals
        # that the latest estimation surpasses
        for point in interval_lower_bounds:
            if latest_value >= point:
                interval_to_use = max(interval_to_use, point)

        return self.params.pool_weights[interval_to_use]

    def _get_current_pool_weights(self) -> Generator[None, None, Optional[List[float]]]:
        """Returns the current weights the pool is using."""
        response = yield from self.get_contract_api_response(
            performative=ContractApiMessage.Performative.GET_STATE,  # type: ignore
            contract_id=str(ManagedPoolContract.contract_id),
            contract_callable="get_normalized_weights",
            contract_address=self.params.managed_pool_address,
        )

        if response.performative != ContractApiMessage.Performative.STATE:
            self.context.logger.error(
                f"Couldn't get weights from IManagedPool.get_normalized_weights. "
                f"Expected response performative {ContractApiMessage.Performative.STATE.value}, "  # type: ignore
                f"received {response.performative.value}."
            )
            return None

        current_weights = cast(
            Optional[List[float]], response.state.body.get("weights", None)
        )
        return current_weights

    def _get_weight_update_params(
        self,
    ) -> Generator[None, None, Optional[Dict[str, Any]]]:
        """Returns the current gradual weight change update parameters."""
        response = yield from self.get_contract_api_response(
            performative=ContractApiMessage.Performative.GET_STATE,  # type: ignore
            contract_id=str(ManagedPoolContract.contract_id),
            contract_callable="get_gradual_weight_update_params",
            contract_address=self.params.managed_pool_address,
        )

        if response.performative != ContractApiMessage.Performative.STATE:
            self.context.logger.error(
                f"Couldn't get weight update params from IManagedPool.get_gradual_weight_update_params. "
                f"Expected response performative {ContractApiMessage.Performative.STATE.value}, "  # type: ignore
                f"received {response.performative.value}."
            )
            return None

        params = cast(Optional[Dict[str, Any]], response.state.body)
        return params


class UpdatePoolTxBehaviour(PoolManagerBaseBehaviour):
    """UpdatePoolTxBehaviour"""

    matching_round: Type[AbstractRound] = UpdatePoolTxRound

    # hardcoded to 0 because we don't need to send any ETH
    # when updating the weights
    ETHER_VALUE = 0

    def async_act(self) -> Generator:
        """Do the act, supporting asynchronous execution."""
        with self.context.benchmark_tool.measure(
            self.behaviour_id,
        ).local():
            safe_tx = yield from self.get_tx()
            self.context.logger.info(f"Prepared safe tx: {safe_tx}")

        # at this point the agent has the data,
        # and shares it with the other agents (peers)
        with self.context.benchmark_tool.measure(
            self.behaviour_id,
        ).consensus():
            payload = UpdatePoolTxPayload(
                self.context.agent_address,
                safe_tx,
            )
            yield from self.send_a2a_transaction(payload)
            yield from self.wait_until_round_end()

        self.set_done()

    def get_tx(self) -> Generator[None, None, str]:
        """
        Prepares a safe tx and returns it.

        There are two steps in sending an on-chain transaction in an autonomous service.
        1.  Prepare the tx the safe needs to execute.
            In our case this is the `ManagedPoolControllerContract.updateWeightsGradually()` tx. Note that the invoker
            of this function is the safe, NOT the individual agents. This is handled by `_get_safe_tx_hash()`.

        2.  Prepare the safe tx.
            Step 1. defines the data of the safe tx, here we prepare the actual tx that includes the data prepared in 1.
            Like any other tx we need to sign it, with the difference being that this is a multisig tx, hence a number
            of agents (majority in our case) need to sign it.
            The signing, as well as the submission of this tx is handled by the TransactionSettlementAbci
            (https://github.com/valory-xyz/open-autonomy/tree/main/packages/valory/skills/transaction_settlement_abci).
            We are responsible for simply compiling the right data in the right format, which is what happens in
            this method.

        :return: the prepared safe tx
        """
        update_weights_gradually_tx_data = (
            yield from self._get_update_weights_gradually_tx_data()
        )
        if update_weights_gradually_tx_data is None:
            return UpdatePoolTxRound.ERROR_PAYLOAD

        safe_tx_hash = yield from self._get_safe_tx_hash(
            update_weights_gradually_tx_data
        )
        if safe_tx_hash is None:
            return UpdatePoolTxRound.ERROR_PAYLOAD

        # params here need to match those in _get_safe_tx_hash()
        payload_data = hash_payload_to_hex(
            safe_tx_hash=safe_tx_hash,
            ether_value=self.ETHER_VALUE,  # we don't send any eth
            safe_tx_gas=SAFE_GAS,
            to_address=self.params.managed_pool_controller_address,
            data=update_weights_gradually_tx_data,
        )
        return payload_data

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
            contract_address=self.synchronized_data.safe_contract_address,  # the safe contract address
            contract_id=str(GnosisSafeContract.contract_id),
            contract_callable="get_raw_safe_transaction_hash",
            to_address=self.params.managed_pool_controller_address,  # the contract the safe will invoke
            value=self.ETHER_VALUE,
            data=data,
            safe_tx_gas=SAFE_GAS,
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

    def _get_time_interval(self) -> Tuple[int, int]:
        """Returns start and end time."""
        # note that we cannot use time.now()
        # as that would most likely result in different
        # values across the different agents
        start_datetime = self.last_synced_timestamp
        end_datetime = start_datetime + self.params.weight_update_timespan

        return start_datetime, end_datetime

    def _get_update_weights_gradually_tx_data(
        self,
    ) -> Generator[None, None, Optional[bytes]]:
        """
        This function returns the encoded ManagedPoolControllerContract.updateWeightsGradually() function.

        In the ManagedPoolControllerContract we have defined a method (get_update_weights_gradually_tx) that acts as a
        wrapper and takes care of this encoding for us. Here we are responsible for simply calling it with the right
        arguments.

        :returns: byte encoded updateWeightsGradually() call
        """
        start_datetime, end_datetime = self._get_time_interval()
        end_weights = self.synchronized_data.most_voted_weights
        response = yield from self.get_contract_api_response(
            performative=ContractApiMessage.Performative.GET_STATE,  # type: ignore
            contract_id=str(ManagedPoolControllerContract.contract_id),
            contract_callable="get_update_weights_gradually_tx",
            contract_address=self.params.managed_pool_controller_address,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            tokens=self.params.pool_tokens,
            end_weights=end_weights,
        )

        if response.performative != ContractApiMessage.Performative.STATE:
            self.context.logger.error(
                f"Couldn't get tx data for ManagedPoolControllerContract.update_weights_gradually. "
                f"Expected response performative {ContractApiMessage.Performative.STATE.value}, "  # type: ignore
                f"received {response.performative.value}."
            )
            return None

        # strip "0x" from the response data
        data_str = cast(str, response.state.body["data"])[2:]
        data = bytes.fromhex(data_str)
        return data


class PoolManagerRoundBehaviour(AbstractRoundBehaviour):
    """PoolManagerRoundBehaviour"""

    initial_behaviour_cls = UpdatePoolTxBehaviour
    abci_app_cls = PoolManagerAbciApp  # type: ignore
    behaviours: Set[Type[BaseBehaviour]] = {
        DecisionMakingBehaviour,  # type: ignore
        UpdatePoolTxBehaviour,  # type: ignore
    }
