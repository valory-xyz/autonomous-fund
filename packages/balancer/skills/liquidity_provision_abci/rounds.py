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
from typing import Dict, List, Optional, Set, Tuple, cast

from packages.balancer.skills.liquidity_provision_abci.payloads import (
    AllowListUpdatePayload,
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
    """LiquidityProvisionAbciApp Events"""

    NO_ACTION = "no_action"
    ROUND_TIMEOUT = "round_timeout"
    DONE = "done"
    NO_MAJORITY = "no_majority"
    ERROR = "error"


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
    def participant_to_tx_hash(self) -> Dict:
        """Get the participant_to_tx_hash."""
        return cast(Dict, self.db.get_strict("participant_to_tx_hash"))

    @property
    def most_voted_tx_hash(self) -> str:
        """Get the most_voted_tx_hash."""
        return cast(str, self.db.get_strict("most_voted_tx_hash"))


class AllowListUpdateRound(CollectSameUntilThresholdRound):
    """A round in which the"""

    allowed_tx_type = AllowListUpdatePayload.transaction_type
    payload_attribute: str = get_name(AllowListUpdatePayload.allow_list_update)
    synchronized_data_class = SynchronizedData

    class NoUpdatePayloads(Enum):
        """
        This class defines special payload types to be used in this round.

        These payloads are for cases when we are not required or able
        to perform an allowlist update.
        """

        NO_UPDATE_PAYLOAD = "no_allowlist_update"
        ERROR_PAYLOAD = "error_payload"

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Enum]]:
        """Process the end of the block."""
        if self.threshold_reached:
            if self.most_voted_payload == self.NoUpdatePayloads.NO_UPDATE_PAYLOAD.value:
                return self.synchronized_data, Event.NO_ACTION

            if self.most_voted_payload == self.NoUpdatePayloads.ERROR_PAYLOAD.value:
                return self.synchronized_data, Event.ERROR

            state = self.synchronized_data.update(
                synchronized_data_class=self.synchronized_data_class,
                **{
                    get_name(SynchronizedData.participant_to_tx_hash): self.collection,
                    get_name(
                        SynchronizedData.most_voted_tx_hash
                    ): self.most_voted_payload,
                }
            )
            return state, Event.DONE
        if not self.is_majority_possible(
            self.collection, self.synchronized_data.nb_participants
        ):
            return self.synchronized_data, Event.NO_MAJORITY

        return None


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
            Event.ERROR: AllowListUpdateRound,
        },
        FinishedWithoutTxRound: {},
        FinishedTxPreparationRound: {},
    }
    final_states: Set[AppState] = {FinishedWithoutTxRound, FinishedTxPreparationRound}
    event_to_timeout: EventToTimeout = {
        Event.ROUND_TIMEOUT: 30.0,
    }
    cross_period_persisted_keys: List[str] = []
    db_pre_conditions: Dict[AppState, List[str]] = {
        AllowListUpdateRound: [
            get_name(SynchronizedData.safe_contract_address),
        ],
    }
    db_post_conditions: Dict[AppState, List[str]] = {
        FinishedWithoutTxRound: [],
        FinishedTxPreparationRound: [
            get_name(SynchronizedData.most_voted_tx_hash),
        ],
    }
