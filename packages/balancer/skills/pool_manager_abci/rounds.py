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

"""This package contains the rounds of PoolManagerAbciApp."""

from enum import Enum
from typing import List, Optional, Set, Tuple

from packages.valory.skills.abstract_round_abci.base import (
    AbciApp,
    AbciAppTransitionFunction,
    AbstractRound,
    AppState,
    BaseSynchronizedData,
    DegenerateRound,
    EventToTimeout,
    TransactionType
)

from packages.balancer.skills.pool_manager_abci.payloads import (
    UpdatePoolTxPayload,
)


class Event(Enum):
    """PoolManagerAbciApp Events"""

    ROUND_TIMEOUT = "round_timeout"
    DONE = "done"
    NO_MAJORITY = "no_majority"


class SynchronizedData(BaseSynchronizedData):
    """
    Class to represent the synchronized data.

    This data is replicated by the tendermint application.
    """


class UpdatePoolTxRound(AbstractRound):
    """UpdatePoolTxRound"""

    # TODO: replace AbstractRound with one of CollectDifferentUntilAllRound, CollectSameUntilAllRound, CollectSameUntilThresholdRound, CollectDifferentUntilThresholdRound, OnlyKeeperSendsRound, VotingRound
    # TODO: set the following class attributes
    round_id: str = "update_pool_tx"
    allowed_tx_type: Optional[TransactionType]
    payload_attribute: str = UpdatePoolTxPayload.transaction_type

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Enum]]:
        """Process the end of the block."""
        raise NotImplementedError

    def check_payload(self, payload: UpdatePoolTxPayload) -> None:
        """Check payload."""
        raise NotImplementedError

    def process_payload(self, payload: UpdatePoolTxPayload) -> None:
        """Process payload."""
        raise NotImplementedError


class FinishedTxPreparationRound(DegenerateRound):
    """FinishedTxPreparationRound"""

    round_id: str = "finished_tx_preparation"


class PoolManagerAbciApp(AbciApp[Event]):
    """PoolManagerAbciApp"""

    initial_round_cls: AppState = UpdatePoolTxRound
    initial_states: Set[AppState] = {UpdatePoolTxRound}
    transition_function: AbciAppTransitionFunction = {UpdatePoolTxRound: {Event.DONE: FinishedTxPreparationRound, Event.ROUND_TIMEOUT: UpdatePoolTxRound, Event.NO_MAJORITY: UpdatePoolTxRound}, FinishedTxPreparationRound: {}}
    final_states: Set[AppState] = {FinishedTxPreparationRound}
    event_to_timeout: EventToTimeout = {}
    cross_period_persisted_keys: List[str] = []
