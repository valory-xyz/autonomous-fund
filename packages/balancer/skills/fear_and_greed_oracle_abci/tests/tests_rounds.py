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

"""This package contains the tests for rounds of FearAndGreedOracleAbciApp."""

from typing import Any, Dict, List, Callable, Hashable
from dataclasses import dataclass, field

import pytest

# TODO: define and import specific payloads explicitly by name
from packages.balancer.skills.fear_and_greed_oracle_abci.payloads import *
from packages.balancer.skills.fear_and_greed_oracle_abci.rounds import (
    Event,
    SynchronizedData,
    EstimationRound,
    ObservationRound,
    OutlierDetectionRound,
)
from packages.valory.skills.abstract_round_abci.base import (
    BaseTxPayload,
)
from packages.valory.skills.abstract_round_abci.test_tools.rounds import (
    BaseRoundTestClass,
    BaseOnlyKeeperSendsRoundTest,
    BaseCollectDifferentUntilThresholdRoundTest,
    BaseCollectSameUntilThresholdRoundTest,
 )


@dataclass
class RoundTestCase:
    """RoundTestCase"""

    initial_data: Dict[str, Hashable]
    payloads: BaseTxPayload
    final_data: Dict[str, Hashable]
    event: Event
    synchronized_data_attr_checks: List[Callable] = field(default_factory=list)


MAX_PARTICIPANTS: int = 4


class BaseFearAndGreedOracleRoundTestClass(BaseRoundTestClass):
    """Base test class for FearAndGreedOracle rounds."""

    synchronized_data: SynchronizedData
    _synchronized_data_class = SynchronizedData
    _event_class = Event

    def run_test(self, test_case: RoundTestCase, **kwargs) -> None:
        """Run the test"""

        self.synchronized_data.update(**test_case.initial_data)

        test_round = self.round_class(
            synchronized_data=self.synchronized_data,
            consensus_params=self.consensus_params,
        )

        self._complete_run(
            self._test_round(
                test_round=test_round,
                round_payloads=test_case.payloads,
                synchronized_data_update_fn=lambda sync_data, _: sync_data.update(**test_case.final_data),
                synchronized_data_attr_checks=test_case.synchronized_data_attr_checks,
                exit_event=test_case.event,
                **kwargs,  # varies per BaseRoundTestClass child
            )
        )


class TestEstimationRound(BaseFearAndGreedOracleRoundTestClass):
    """Tests for EstimationRound."""

    round_class = EstimationRound

    # TODO: provide test cases
    @pytest.mark.parametrize("test_case, kwargs", [])
    def test_run(self, test_case: RoundTestCase, **kwargs: Any) -> None:
        """Run tests."""

        self.run_test(test_case, **kwargs)


class TestObservationRound(BaseFearAndGreedOracleRoundTestClass):
    """Tests for ObservationRound."""

    round_class = ObservationRound

    # TODO: provide test cases
    @pytest.mark.parametrize("test_case, kwargs", [])
    def test_run(self, test_case: RoundTestCase, **kwargs: Any) -> None:
        """Run tests."""

        self.run_test(test_case, **kwargs)


class TestOutlierDetectionRound(BaseFearAndGreedOracleRoundTestClass):
    """Tests for OutlierDetectionRound."""

    round_class = OutlierDetectionRound

    # TODO: provide test cases
    @pytest.mark.parametrize("test_case, kwargs", [])
    def test_run(self, test_case: RoundTestCase, **kwargs: Any) -> None:
        """Run tests."""

        self.run_test(test_case, **kwargs)

