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

"""This package contains the tests for TxMultiplexing."""

import pytest

from packages.balancer.skills.autonomous_fund_abci.multiplexer import (
    Event,
    PostTransactionSettlementRound,
    SynchronizedData,
)
from packages.balancer.skills.liquidity_provision_abci.rounds import (
    AllowListUpdateRound,
)
from packages.balancer.skills.pool_manager_abci.rounds import UpdatePoolTxRound
from packages.valory.skills.abstract_round_abci.base import get_name
from packages.valory.skills.abstract_round_abci.test_tools.rounds import (
    BaseRoundTestClass,
)


class TestPostTransactionSettlementRound(BaseRoundTestClass):
    """Tests for PostTransactionSettlementRound."""

    round_class = PostTransactionSettlementRound
    synchronized_data: SynchronizedData
    _synchronized_data_class = SynchronizedData
    _event_class = Event

    @pytest.mark.parametrize(
        "tx_submitter, expected_event",
        [
            (UpdatePoolTxRound.auto_round_id(), Event.WEIGHT_UPDATE_DONE),
            (
                AllowListUpdateRound.auto_round_id(),
                Event.ALLOWLIST_UPDATE_DONE,
            ),
        ],
    )
    def test_run(self, tx_submitter: str, expected_event: Event) -> None:
        """Run round tests."""
        self.synchronized_data.update(
            **{get_name(SynchronizedData.tx_submitter): tx_submitter}  # type: ignore
        )
        test_round = self.round_class(
            synchronized_data=self.synchronized_data,
            consensus_params=self.consensus_params,
        )
        res = test_round.end_block()
        assert res is not None
        _, event = res
        assert event == expected_event
