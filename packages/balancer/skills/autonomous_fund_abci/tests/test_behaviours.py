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
# pylint: skip-file

"""This package contains round behaviours of AutonomousFundAbciApp."""
from pathlib import Path

from _pytest.logging import LogCaptureFixture

from packages.balancer.skills.autonomous_fund_abci.behaviours import (  # noqa
    AutonomousFundConsensusBehaviour,
    PostTransactionSettlementBehaviour,
    PostTransactionSettlementFullBehaviour,
)
from packages.balancer.skills.autonomous_fund_abci.multiplexer import SynchronizedData
from packages.valory.skills.abstract_round_abci.base import AbciAppDB, get_name
from packages.valory.skills.abstract_round_abci.test_tools.base import (
    FSMBehaviourBaseCase,
)


class TestPostTransactionSettlementBehaviour(FSMBehaviourBaseCase):
    """Tests PostTransactionSettlementBehaviour."""

    path_to_skill = Path(__file__).parent.parent

    def test_run(self, caplog: LogCaptureFixture) -> None:
        """The behaviour should log when a tx is settled."""
        data = {
            get_name(SynchronizedData.tx_submitter): "test",
            get_name(SynchronizedData.consensus_threshold): None,
            get_name(SynchronizedData.participants): ["0x0"],
            get_name(SynchronizedData.all_participants): ["0x0"],
        }
        self.fast_forward_to_behaviour(
            self.behaviour,
            PostTransactionSettlementBehaviour.auto_behaviour_id(),
            SynchronizedData(AbciAppDB(setup_data=AbciAppDB.data_to_lists(data))),
        )
        self.behaviour.act_wrapper()
        assert (
            "The transaction submitted by test was successfully settled." in caplog.text
        )
