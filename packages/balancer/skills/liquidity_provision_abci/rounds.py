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

"""This package contains the rounds of LiquidityProvisionAbciApp."""

from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

from packages.valory.skills.abstract_round_abci.base import (
    AbciApp,
    AbciAppTransitionFunction,
    AbstractRound,
    AppState,
    BaseSynchronizedData,
    DegenerateRound,
    EventToTimeout,
    TransactionType,
)

from packages.balancer.skills.liquidity_provision_abci.payloads import (
    AllowListUpdatePayload,
)


class Event(Enum):
    """LiquidityProvisionAbciApp Events"""

    NO_ACTION = "no_action"
    ROUND_TIMEOUT = "round_timeout"
    DONE = "done"
    NO_MAJORITY = "no_majority"


class SynchronizedData(BaseSynchronizedData):
    """
    Class to represent the synchronized data.

    This data is replicated by the tendermint application.
    """


class AllowListUpdateRound(AbstractRound):
    """AllowListUpdateRound"""

    # TODO: replace AbstractRound with one of CollectDifferentUntilAllRound, CollectSameUntilAllRound, CollectSameUntilThresholdRound, CollectDifferentUntilThresholdRound, OnlyKeeperSendsRound, VotingRound
    allowed_tx_type: Optional[TransactionType] = AllowListUpdatePayload.transaction_type
    # TODO: set the correct payload attribute
    payload_attribute: str

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Enum]]:
        """Process the end of the block."""
        return self.synchronized_data, Event.DONE
        return self.synchronized_data, Event.NO_ACTION
        return self.synchronized_data, Event.NO_MAJORITY

    def check_payload(self, payload: AllowListUpdatePayload) -> None:
        """Check payload."""
        raise NotImplementedError

    def process_payload(self, payload: AllowListUpdatePayload) -> None:
        """Process payload."""
        raise NotImplementedError


class FinishedTxPreparationRound(DegenerateRound):
    """FinishedTxPreparationRound"""


class FinishedWithoutTxRound(DegenerateRound):
    """FinishedWithoutTxRound"""


class LiquidityProvisionAbciApp(AbciApp[Event]):
    """LiquidityProvisionAbciApp"""

    initial_round_cls: AppState = AllowListUpdateRound
    initial_states: Set[AppState] = {AllowListUpdateRound}
    transition_function: AbciAppTransitionFunction = {
        AllowListUpdateRound: {
            Event.DONE: FinishedTxPreparationRound,
            Event.NO_ACTION: FinishedWithoutTxRound,
            Event.NO_MAJORITY: AllowListUpdateRound,
            Event.ROUND_TIMEOUT: AllowListUpdateRound,
        },
        FinishedWithoutTxRound: {},
        FinishedTxPreparationRound: {},
    }
    final_states: Set[AppState] = {FinishedWithoutTxRound, FinishedTxPreparationRound}
    event_to_timeout: EventToTimeout = {}
    cross_period_persisted_keys: List[str] = []
    db_pre_conditions: Dict[AppState, List[str]] = {
        AllowListUpdateRound: [],
    }
    db_post_conditions: Dict[AppState, List[str]] = {
        FinishedWithoutTxRound: [],
        FinishedTxPreparationRound: [],
    }
    event_to_timeout: EventToTimeout = {
        Event.ROUND_TIMEOUT: 30.0,
    }
