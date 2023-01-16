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

"""This package contains round behaviours of FearAndGreedOracleAbciApp."""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Hashable, List, Optional, Type
from unittest import mock

import pytest

from packages.balancer.skills.fear_and_greed_oracle_abci.behaviours import (
    EstimationBehaviour,
    FearAndGreedOracleBaseBehaviour,
    ObservationBehaviour,
    OutlierDetectionBehaviour,
)
from packages.balancer.skills.fear_and_greed_oracle_abci.payloads import (
    ObservationRoundPayload,
)
from packages.balancer.skills.fear_and_greed_oracle_abci.rounds import (
    Event,
    FinishedDataCollectionRound,
    SynchronizedData,
)
from packages.valory.skills.abstract_round_abci.base import AbciAppDB
from packages.valory.skills.abstract_round_abci.behaviours import (
    BaseBehaviour,
    make_degenerate_behaviour,
)
from packages.valory.skills.abstract_round_abci.test_tools.base import (
    FSMBehaviourBaseCase,
)


DEFAULT_FEAR_AND_GREED_INDEX_BASE_URL = (
    "https://api.alternative.me/fng/?format=json&limit="
)
DEFAULT_FEAR_AND_GREED_NUM_POINTS = 2


@dataclass
class BehaviourTestCase:
    """BehaviourTestCase"""

    name: str
    initial_data: Dict[str, Hashable]
    event: Event
    next_behaviour_class: Optional[Type[FearAndGreedOracleBaseBehaviour]] = None


class BaseFearAndGreedOracleTest(FSMBehaviourBaseCase):
    """Base test case."""

    path_to_skill = Path(__file__).parent.parent

    behaviour: FearAndGreedOracleBaseBehaviour  # type: ignore
    behaviour_class: Type[FearAndGreedOracleBaseBehaviour]
    next_behaviour_class: Type[FearAndGreedOracleBaseBehaviour]
    synchronized_data: SynchronizedData
    done_event = Event.DONE

    def fast_forward(self, data: Optional[Dict[str, Any]] = None) -> None:
        """Fast-forward on initialization"""

        data = data if data is not None else {}
        self.fast_forward_to_behaviour(
            self.behaviour,  # type: ignore
            self.behaviour_class.auto_behaviour_id(),
            SynchronizedData(AbciAppDB(setup_data=AbciAppDB.data_to_lists(data))),
        )
        assert (
            self.behaviour.current_behaviour.auto_behaviour_id()  # type: ignore
            == self.behaviour_class.auto_behaviour_id()
        )

    def complete(
        self, event: Event, next_behaviour_class: Optional[Type[BaseBehaviour]] = None
    ) -> None:
        """Complete test"""
        if next_behaviour_class is None:
            # use the class value as fallback
            next_behaviour_class = self.next_behaviour_class

        self.behaviour.act_wrapper()
        self.mock_a2a_transaction()
        self._test_done_flag_set()
        self.end_round(done_event=event)
        assert (
            self.behaviour.current_behaviour.auto_behaviour_id()  # type: ignore
            == next_behaviour_class.auto_behaviour_id()
        )


class TestObservationBehaviour(BaseFearAndGreedOracleTest):
    """Tests ObservationBehaviour"""

    behaviour_class = ObservationBehaviour
    next_behaviour_class = EstimationBehaviour

    @pytest.mark.parametrize(
        "test_case, kwargs",
        [
            (
                BehaviourTestCase(
                    "the happy path",
                    initial_data=dict(),
                    event=Event.DONE,
                ),
                {
                    "body": '{"name":"Fear and Greed Index","data":[{"value":"25","value_classification":"Extreme Fear","timestamp":"1662940800","time_until_update":"44102"},{"value":"26","value_classification":"Fear","timestamp":"1662854400"}],"metadata":{"error":null}}',
                    "status_code": 200,
                },
            ),
            (
                BehaviourTestCase(
                    "the api is misbehaving",
                    initial_data=dict(),
                    event=Event.NO_ACTION,
                    next_behaviour_class=ObservationBehaviour,
                ),
                {
                    "body": "",
                    "status_code": 500,
                },
            ),
            (
                BehaviourTestCase(
                    "the api has changed its response format",
                    initial_data=dict(),
                    event=Event.NO_ACTION,
                    next_behaviour_class=ObservationBehaviour,
                ),
                {
                    "body": '{"data":[{"value":"25","value_classification":"Extreme Fear","timestamp":"1662940800","time_until_update":"44102"},{"value":"26","value_classification":"Fear","timestamp":"1662854400"}],"metadata":{"error":null}}',
                    "status_code": 200,
                },
            ),
            (
                BehaviourTestCase(
                    "the api sends invalid json",
                    initial_data=dict(),
                    event=Event.NO_ACTION,
                    next_behaviour_class=ObservationBehaviour,
                ),
                {
                    "body": "bad_json",
                    "status_code": 200,
                },
            ),
        ],
    )
    def test_run(self, test_case: BehaviourTestCase, kwargs: Any) -> None:
        """Run tests."""
        self.fast_forward(test_case.initial_data)
        self.behaviour.act_wrapper()
        self.mock_http_request(
            request_kwargs=dict(
                method="GET",
                headers="",
                version="",
                url=f"{DEFAULT_FEAR_AND_GREED_INDEX_BASE_URL}{DEFAULT_FEAR_AND_GREED_NUM_POINTS}",
            ),
            response_kwargs=dict(
                version="",
                status_code=kwargs.get("status_code"),
                status_text="",
                headers="",
                body=kwargs.get("body").encode(),
            ),
        )
        self.complete(test_case.event, test_case.next_behaviour_class)

    @pytest.mark.parametrize(
        "test_case, kwargs",
        [
            (
                BehaviourTestCase(
                    "unexpected error from api response handling",
                    initial_data=dict(),
                    event=Event.NO_ACTION,
                    next_behaviour_class=ObservationBehaviour,
                ),
                {
                    "body": "irrelevant for the test",
                    "status_code": 500,
                },
            ),
        ],
    )
    def test_unexpected_error(self, test_case: BehaviourTestCase, kwargs: Any) -> None:
        """An unexpected exception is raised while handling the Fear and Greed API response."""
        self.fast_forward(test_case.initial_data)
        self.behaviour.act_wrapper()
        self.mock_http_request(
            request_kwargs=dict(
                method="GET",
                headers="",
                version="",
                url=f"{DEFAULT_FEAR_AND_GREED_INDEX_BASE_URL}{DEFAULT_FEAR_AND_GREED_NUM_POINTS}",
            ),
            response_kwargs=dict(
                version="",
                status_code=kwargs.get("status_code"),
                status_text="",
                headers="",
                body=kwargs.get("body").encode(),
            ),
        )
        with mock.patch(
            "json.loads",
            side_effect=Exception("unexpected error"),
        ):
            self.behaviour.act_wrapper()

        next_behaviour_class = test_case.next_behaviour_class
        if next_behaviour_class is None:
            # use the class value as fallback
            next_behaviour_class = self.next_behaviour_class

        self.mock_a2a_transaction()
        self._test_done_flag_set()
        self.end_round(done_event=test_case.event)
        assert (
            self.behaviour.current_behaviour.auto_behaviour_id()  # type: ignore
            == next_behaviour_class.auto_behaviour_id()
        )


class TestEstimationBehaviour(BaseFearAndGreedOracleTest):
    """Tests EstimationBehaviour"""

    behaviour_class = EstimationBehaviour
    next_behaviour_class = OutlierDetectionBehaviour

    _observation = [
        {
            "value": 25,
            "timestamp": 1662940800,
        },
        {
            "value": 26,
            "timestamp": 1662854400,
        },
    ]
    _bad_observation: List = []

    @pytest.mark.parametrize(
        "test_case",
        [
            BehaviourTestCase(
                "the happy path",
                initial_data={  # type: ignore
                    "participant_to_observations": {  # type: ignore
                        "agent_a": ObservationRoundPayload(
                            "agent_a", json.dumps(_observation)
                        ),
                        "agent_b": ObservationRoundPayload(
                            "agent_b", json.dumps(_observation)
                        ),
                        "agent_c": ObservationRoundPayload(
                            "agent_c", json.dumps(_observation)
                        ),
                        "agent_d": ObservationRoundPayload(
                            "agent_d", json.dumps(_bad_observation)
                        ),
                    }
                },
                event=Event.DONE,
                next_behaviour_class=OutlierDetectionBehaviour,
            ),
        ],
    )
    def test_run(self, test_case: BehaviourTestCase) -> None:
        """Run tests."""
        self.fast_forward(test_case.initial_data)
        self.complete(test_case.event, test_case.next_behaviour_class)


class TestOutlierDetectionBehaviour(BaseFearAndGreedOracleTest):
    """Tests OutlierDetectionBehaviour"""

    behaviour_class = OutlierDetectionBehaviour
    next_behaviour_class = ObservationBehaviour
    _normal_estimates = {
        "value_estimates": [
            25.0,
            26.0,
        ],
        "timestamp_estimates": [
            1662940800.0,
            1662854400.0,
        ],
    }
    _negative_estimates = {
        "value_estimates": [
            -25.0,  # estimate is negative
            26.0,
        ],
        "timestamp_estimates": [
            1662940800.0,
            1662854400.0,
        ],
    }
    _over_100_estimates = {
        "value_estimates": [
            5001,  # it's over 5000
            26.0,
        ],
        "timestamp_estimates": [
            1662940800.0,
            1662854400.0,
        ],
    }
    _aggressive_change = {
        "value_estimates": [
            5,
            95,
        ],
        "timestamp_estimates": [
            1662940800.0,
            1662854400.0,
        ],
    }

    @pytest.mark.parametrize(
        "test_case",
        [
            BehaviourTestCase(
                "no outlier detected",
                initial_data=dict(most_voted_estimates=json.dumps(_normal_estimates)),
                event=Event.DONE,
                next_behaviour_class=make_degenerate_behaviour(  # type: ignore
                    FinishedDataCollectionRound
                ),  # noqa
            ),
            BehaviourTestCase(
                "negative estimate",
                initial_data=dict(most_voted_estimates=json.dumps(_negative_estimates)),
                event=Event.NO_ACTION,
            ),
            BehaviourTestCase(
                "estimate over 100",
                initial_data=dict(most_voted_estimates=json.dumps(_over_100_estimates)),
                event=Event.NO_ACTION,
            ),
            BehaviourTestCase(
                "aggressive change",
                initial_data=dict(most_voted_estimates=json.dumps(_aggressive_change)),
                event=Event.NO_ACTION,
            ),
        ],
    )
    def test_run(self, test_case: BehaviourTestCase) -> None:
        """Run tests."""
        self.fast_forward(test_case.initial_data)
        self.complete(test_case.event, test_case.next_behaviour_class)
