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

"""This package contains the rounds of FearAndGreedOracleAbciApp."""

from enum import Enum
from typing import List, Optional, Set, Tuple

from packages.valory.skills.abstract_round_abci.base import (
    AbciApp,
    AbciAppTransitionFunction,
    AbstractRound,
    AppState,
    BaseSynchronizedData,
    BaseTxPayload,
    DegenerateRound,
    EventToTimeout,
    TransactionType, CollectSameUntilThresholdRound
)


class Event(Enum):
    """Defines the events for this abci."""

    NO_MAJORITY = "no_majority"
    DONE = "done"


class SynchronizedData(BaseSynchronizedData):
    """
    Class to represent the synchronized data.

    This data is replicated by the tendermint application.
    """


class ObservationRound(AbstractRound):
    """A round that in which the data processing logic is done."""

    round_id: str = "observation_round"
    allowed_tx_type: Optional[TransactionType]
    payload_attribute: str

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Enum]]:
        """Process the end of the block."""
        raise NotImplementedError

    def check_payload(self, payload: BaseTxPayload) -> None:
        """Check payload."""
        raise NotImplementedError

    def process_payload(self, payload: BaseTxPayload) -> None:
        """Process payload."""
        raise NotImplementedError


class EstimationRound(CollectSameUntilThresholdRound):
    """A round that in which the data processing logic is done."""

    round_id: str = "estimation_round"
    allowed_tx_type: Optional[TransactionType]
    payload_attribute: str

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Enum]]:
        """Process the end of the block."""
        raise NotImplementedError

    def check_payload(self, payload: BaseTxPayload) -> None:
        """Check payload."""
        raise NotImplementedError

    def process_payload(self, payload: BaseTxPayload) -> None:
        """Process payload."""
        raise NotImplementedError


class FinishedDataCollectionRound(DegenerateRound):
    """A degenerate round that acts as the terminal state of FearAndGreedOracleAbciApp."""

    round_id: str = "finished_data_collection_round"


class FearAndGreedOracleAbciApp(AbciApp[Event]):
    """A class that defines the transition between rounds in this abci app."""

    initial_round_cls: AppState = ObservationRound
    initial_states: Set[AppState] = {ObservationRound}
    transition_function: AbciAppTransitionFunction = {ObservationRound: {Event.DONE: EstimationRound, Event.NO_MAJORITY: ObservationRound}, EstimationRound: {Event.DONE: FinishedDataCollectionRound, Event.NO_MAJORITY: ObservationRound}, FinishedDataCollectionRound: {}}
    final_states: Set[AppState] = {FinishedDataCollectionRound}
    event_to_timeout: EventToTimeout = {}
    cross_period_persisted_keys: List[str] = []
