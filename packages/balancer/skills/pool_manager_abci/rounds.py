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

"""This package contains the rounds of PoolManagerAbciApp."""
import json
from enum import Enum
from typing import Dict, FrozenSet, Optional, Set, Tuple, cast

from packages.balancer.skills.pool_manager_abci.payloads import (
    DecisionMakingPayload,
    UpdatePoolTxPayload,
)
from packages.valory.skills.abstract_round_abci.base import (
    AbciApp,
    AbciAppTransitionFunction,
    AppState,
    BaseSynchronizedData,
    CollectSameUntilThresholdRound,
    DegenerateRound,
    EventToTimeout,
    get_name,
)


class Event(Enum):
    """PoolManagerAbciApp Events"""

    ROUND_TIMEOUT = "round_timeout"
    DONE = "done"
    NO_MAJORITY = "no_majority"
    NO_ACTION = "no_action"


class SynchronizedData(BaseSynchronizedData):
    """
    Class to represent the synchronized data.

    This data is replicated by the tendermint application.
    """

    @property
    def safe_contract_address(self) -> str:
        """Get the safe contract address."""
        return cast(str, self.db.get_strict("safe_contract_address"))

    @property
    def participant_to_decision(self) -> Dict:
        """Get the participant_to_decision."""
        return cast(Dict, self.db.get_strict("participant_to_decision"))

    @property
    def most_voted_weights(self) -> Dict:
        """Get the most_voted_weights."""
        return cast(Dict, self.db.get_strict("most_voted_weights"))

    @property
    def participant_to_tx(self) -> Dict:
        """Get the participant_to_tx."""
        return cast(Dict, self.db.get_strict("participant_to_tx"))

    @property
    def most_voted_tx_hash(self) -> Dict:
        """Get the most_voted_tx_hash."""
        return cast(Dict, self.db.get_strict("most_voted_tx_hash"))

    @property
    def most_voted_estimates(self) -> str:
        """Get the most_voted_tx."""
        return cast(str, self.db.get_strict("most_voted_estimates"))

    @property
    def tx_submitter(self) -> str:
        """Get the round that submitted a tx to transaction_settlement_abci."""
        return cast(str, self.db.get_strict("tx_submitter"))


class DecisionMakingRound(CollectSameUntilThresholdRound):
    """This class defines the round in which the agents decide whether to update the weights or not."""

    payload_class = DecisionMakingPayload
    payload_attribute = "decision_making"
    synchronized_data_class = SynchronizedData

    # used for cases when we don't need to update
    # in case we need to update the payload would contain
    # the actual weights in the form of a serialized json string
    NO_UPDATE_PAYLOAD = "no_update"

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Event]]:
        """Process the end of the block."""
        if self.threshold_reached:
            if self.most_voted_payload == self.NO_UPDATE_PAYLOAD:
                return self.synchronized_data, Event.NO_ACTION

            payload = json.loads(self.most_voted_payload)
            state = self.synchronized_data.update(
                synchronized_data_class=self.synchronized_data_class,
                participant_to_decision=self.serialize_collection(self.collection),
                most_voted_weights=payload.get("weights"),
            )
            return state, Event.DONE
        if not self.is_majority_possible(
            self.collection, self.synchronized_data.nb_participants
        ):
            return self.synchronized_data, Event.NO_MAJORITY

        return None


class UpdatePoolTxRound(CollectSameUntilThresholdRound):
    """This class defines the round in which the agents prepare a tx to update the pool."""

    payload_class = UpdatePoolTxPayload
    payload_attribute = "update_pool_tx"
    synchronized_data_class = SynchronizedData

    ERROR_PAYLOAD = "{}"

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Event]]:
        """Process the end of the block."""
        if self.threshold_reached:
            if self.most_voted_payload == self.ERROR_PAYLOAD:
                return self.synchronized_data, Event.NO_ACTION

            state = self.synchronized_data.update(
                synchronized_data_class=self.synchronized_data_class,
                **{
                    get_name(
                        SynchronizedData.participant_to_tx
                    ): self.serialize_collection(self.collection),
                    get_name(
                        SynchronizedData.most_voted_tx_hash
                    ): self.most_voted_payload,
                    get_name(SynchronizedData.tx_submitter): self.auto_round_id(),
                },
            )
            return state, Event.DONE
        if not self.is_majority_possible(
            self.collection, self.synchronized_data.nb_participants
        ):
            return self.synchronized_data, Event.NO_MAJORITY

        return None


class FinishedWithoutTxRound(DegenerateRound):
    """FinishedWithoutTxRound"""


class FinishedTxPreparationRound(DegenerateRound):
    """FinishedTxPreparationRound"""


class PoolManagerAbciApp(AbciApp[Event]):
    """PoolManagerAbciApp

    Initial round: DecisionMakingRound

    Initial states: {DecisionMakingRound}

    Transition states:
        0. DecisionMakingRound
            - done: 1.
            - round timeout: 0.
            - no majority: 0.
            - no action: 2.
        1. UpdatePoolTxRound
            - done: 3.
            - round timeout: 1.
            - no majority: 1.
            - no action: 1.
        2. FinishedWithoutTxRound
        3. FinishedTxPreparationRound

    Final states: {FinishedTxPreparationRound, FinishedWithoutTxRound}

    Timeouts:
        round timeout: 30.0
    """

    initial_round_cls: AppState = DecisionMakingRound
    initial_states: Set[AppState] = {DecisionMakingRound}
    transition_function: AbciAppTransitionFunction = {
        DecisionMakingRound: {
            Event.DONE: UpdatePoolTxRound,
            Event.ROUND_TIMEOUT: DecisionMakingRound,
            Event.NO_MAJORITY: DecisionMakingRound,
            Event.NO_ACTION: FinishedWithoutTxRound,
        },
        UpdatePoolTxRound: {
            Event.DONE: FinishedTxPreparationRound,
            Event.ROUND_TIMEOUT: UpdatePoolTxRound,
            Event.NO_MAJORITY: UpdatePoolTxRound,
            Event.NO_ACTION: UpdatePoolTxRound,
        },
        FinishedWithoutTxRound: {},
        FinishedTxPreparationRound: {},
    }
    final_states: Set[AppState] = {FinishedWithoutTxRound, FinishedTxPreparationRound}
    event_to_timeout: EventToTimeout = {
        Event.ROUND_TIMEOUT: 30.0,
    }
    cross_period_persisted_keys: FrozenSet[str] = frozenset()
    db_pre_conditions: Dict[AppState, Set[str]] = {
        DecisionMakingRound: {
            get_name(SynchronizedData.most_voted_estimates),
        },
    }
    db_post_conditions: Dict[AppState, Set[str]] = {
        FinishedTxPreparationRound: {
            get_name(SynchronizedData.most_voted_tx_hash),
            get_name(SynchronizedData.tx_submitter),
        },
        FinishedWithoutTxRound: set(),
    }
