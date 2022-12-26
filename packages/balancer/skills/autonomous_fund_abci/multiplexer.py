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
"""This package contains the rounds of TransactionSettlementAbciMultiplexer."""

from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, cast

from packages.balancer.skills.liquidity_provision_abci.rounds import (
    AllowListUpdateRound,
)
from packages.balancer.skills.pool_manager_abci.rounds import UpdatePoolTxRound
from packages.valory.skills.abstract_round_abci.base import (
    AbciApp,
    AbciAppTransitionFunction,
    AppState,
    BaseSynchronizedData,
    CollectSameUntilThresholdRound,
    DegenerateRound,
    get_name,
)


_NO_TX_ROUND = "no_tx"


class Event(Enum):
    """Multiplexing events."""

    WEIGHT_UPDATE_DONE = "weight_update_done"
    ALLOWLIST_UPDATE_DONE = "allowlist_update_done"


class SynchronizedData(BaseSynchronizedData):
    """
    Class to represent the synchronized data.

    This data is replicated by the tendermint application.
    """

    @property
    def tx_submitter(self) -> str:
        """Get the round that submitted a tx to transaction_settlement_abci."""
        return cast(str, self.db.get_strict("tx_submitter"))


class PostTransactionSettlementRound(CollectSameUntilThresholdRound):
    """A round that will be called after tx settlement is done."""

    allowed_tx_type = _NO_TX_ROUND
    payload_attribute = _NO_TX_ROUND
    synchronized_data_class = SynchronizedData

    round_id_to_event: Dict[str, Event] = {
        AllowListUpdateRound.auto_round_id(): Event.ALLOWLIST_UPDATE_DONE,
        UpdatePoolTxRound.auto_round_id(): Event.WEIGHT_UPDATE_DONE,
    }

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Enum]]:
        """
        The end block.

        This is a dummy round, no consensus is necessary here.
        There is no need to send a tx through, nor to check for majority.
        We simply use this round to check which round submitted the tx,
        and move to the next state in accordance to that.
        """
        sync_data = cast(SynchronizedData, self.synchronized_data)
        return sync_data, self.round_id_to_event[sync_data.tx_submitter]


class FinishedAllowlistUpdateRound(DegenerateRound):
    """Finished allowlist update round."""


class FinishedWeightUpdateRound(DegenerateRound):
    """Finished weight update round."""


class TransactionSettlementAbciMultiplexer(AbciApp[Event]):
    """ABCI app to multiplex the transaction settlement skill."""

    initial_round_cls: AppState = PostTransactionSettlementRound
    initial_states: Set[AppState] = {PostTransactionSettlementRound}
    transition_function: AbciAppTransitionFunction = {
        PostTransactionSettlementRound: {
            Event.ALLOWLIST_UPDATE_DONE: FinishedAllowlistUpdateRound,
            Event.WEIGHT_UPDATE_DONE: FinishedWeightUpdateRound,
        },
        FinishedAllowlistUpdateRound: {},
        FinishedWeightUpdateRound: {},
    }
    final_states: Set[AppState] = {
        FinishedWeightUpdateRound,
        FinishedAllowlistUpdateRound,
    }
    db_pre_conditions: Dict[AppState, List[str]] = {
        PostTransactionSettlementRound: [get_name(SynchronizedData.tx_submitter)]
    }
    db_post_conditions: Dict[AppState, List[str]] = {
        FinishedAllowlistUpdateRound: [],
        FinishedWeightUpdateRound: [],
    }
