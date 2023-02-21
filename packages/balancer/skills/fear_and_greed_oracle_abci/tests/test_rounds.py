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
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Hashable, List, cast

import pytest

from packages.balancer.skills.fear_and_greed_oracle_abci.payloads import (
    EstimationRoundPayload,
    ObservationRoundPayload,
    OutlierDetectionRoundPayload,
)
from packages.balancer.skills.fear_and_greed_oracle_abci.rounds import (
    EstimationRound,
    Event,
    ObservationRound,
    OutlierDetectionRound,
    SynchronizedData,
)
from packages.valory.skills.abstract_round_abci.base import BaseTxPayload
from packages.valory.skills.abstract_round_abci.test_tools.rounds import (
    BaseRoundTestClass,
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

    def run_test(self, test_case: RoundTestCase, **kwargs: Any) -> None:
        """Run the test"""

        self.synchronized_data.update(**test_case.initial_data)  # type: ignore

        test_round = self.round_class(  # type: ignore # pylint: disable=no-member
            synchronized_data=self.synchronized_data,
        )

        self._complete_run(
            self._test_round(  # type: ignore # pylint: disable=unused-import,no-member
                test_round=test_round,
                round_payloads=test_case.payloads,
                synchronized_data_update_fn=lambda sync_data, _: sync_data.update(
                    **test_case.final_data
                ),
                synchronized_data_attr_checks=test_case.synchronized_data_attr_checks,
                exit_event=test_case.event,
                **kwargs,  # varies per BaseRoundTestClass child
            )
        )


class TestObservationRound(BaseFearAndGreedOracleRoundTestClass):
    """Tests for ObservationRound."""

    round_class = ObservationRound

    def test_run(self) -> None:
        """Tests the happy path for ObservationRound."""
        test_round = self.round_class(
            synchronized_data=self.synchronized_data,
        )

        payload = dict(test_observation=123)
        serialized_payload = json.dumps(payload, sort_keys=True)
        first_payload, *payloads = [
            ObservationRoundPayload(
                sender=participant, observation_data=serialized_payload
            )
            for participant in self.participants
        ]

        # only one participant has voted
        # no event should be returned
        test_round.process_payload(first_payload)
        assert test_round.collection[first_payload.sender] == first_payload
        assert test_round.end_block() is None

        # enough members have voted
        # but no majority is reached
        self._test_no_majority_event(test_round)

        # all members voted in the same way
        for payload in payloads:  # type: ignore
            test_round.process_payload(payload)  # type: ignore

        expected_next_state = cast(
            SynchronizedData,
            self.synchronized_data.update(
                participant_to_observations=self.round_class.serialize_collection(
                    test_round.collection
                ),
                most_voted_observation=cast(ObservationRoundPayload, payload).json,
            ),
        )

        res = test_round.end_block()
        assert res is not None
        state, event = res
        actual_next_state = cast(SynchronizedData, state)

        # check that the state is updated as expected
        assert (
            actual_next_state.most_voted_observation
            == expected_next_state.most_voted_observation
        )

        # make sure all the votes are as expected
        assert all(
            [
                cast(Dict, actual_next_state.participant_to_observations)[participant]
                == actual_vote
                for (participant, actual_vote) in cast(
                    Dict, expected_next_state.participant_to_observations
                ).items()
            ]
        )

        assert event == Event.DONE

    def test_err_payload(self) -> None:
        """Test case for when a bad payload is sent."""
        test_round = self.round_class(
            synchronized_data=self.synchronized_data,
        )

        payload: Dict = dict()  # an empty dict is the error payload
        serialized_payload = json.dumps(payload, sort_keys=True)
        first_payload, *payloads = [
            ObservationRoundPayload(
                sender=participant, observation_data=serialized_payload
            )
            for participant in self.participants
        ]

        # only one participant has voted
        # no event should be returned
        test_round.process_payload(first_payload)
        assert test_round.collection[first_payload.sender] == first_payload
        assert test_round.end_block() is None

        # enough members have voted
        # but no majority is reached
        self._test_no_majority_event(test_round)

        # all members voted in the same way
        # Event DONE should be returned
        for payload in payloads:  # type: ignore
            test_round.process_payload(payload)  # type: ignore

        res = test_round.end_block()
        assert res is not None
        state, event = res
        actual_next_state = cast(SynchronizedData, state)

        with pytest.raises(ValueError):
            actual_next_state.most_voted_observation  # pylint: disable=pointless-statement

        assert event == Event.NO_ACTION


class TestEstimationRound(BaseFearAndGreedOracleRoundTestClass):
    """Tests for EstimationRound."""

    round_class = EstimationRound

    def test_run(self) -> None:
        """Run tests."""
        test_round = self.round_class(
            synchronized_data=self.synchronized_data,
        )

        payload = dict(test_estimation=123)
        serialized_payload = json.dumps(payload, sort_keys=True)
        first_payload, *payloads = [
            EstimationRoundPayload(
                sender=participant, estimation_data=serialized_payload
            )
            for participant in self.participants
        ]

        # only one participant has voted
        # no event should be returned
        test_round.process_payload(first_payload)
        assert test_round.collection[first_payload.sender] == first_payload
        assert test_round.end_block() is None

        # enough members have voted
        # but no majority is reached
        self._test_no_majority_event(test_round)

        # all members voted in the same way
        for payload in payloads:  # type: ignore
            test_round.process_payload(payload)  # type: ignore

        expected_next_state = cast(
            SynchronizedData,
            self.synchronized_data.update(
                participant_to_observations=self.round_class.serialize_collection(
                    test_round.collection
                ),
                most_voted_observation=cast(EstimationRoundPayload, payload).json,
            ),
        )

        res = test_round.end_block()
        assert res is not None
        state, event = res
        actual_next_state = cast(SynchronizedData, state)

        # check that the state is updated as expected
        assert (
            actual_next_state.most_voted_estimates
            == expected_next_state.most_voted_estimates
        )

        # make sure all the votes are as expected
        assert all(
            [
                cast(Dict, actual_next_state.participant_to_estimates)[participant]
                == actual_vote
                for (participant, actual_vote) in cast(
                    Dict, expected_next_state.participant_to_estimates
                ).items()
            ]
        )

        assert event == Event.DONE


class TestOutlierDetectionRound(BaseFearAndGreedOracleRoundTestClass):
    """Tests for OutlierDetectionRound."""

    round_class = OutlierDetectionRound

    def test_outlier_detected(self) -> None:
        """Test case for when an outlier was detected."""
        test_round = self.round_class(
            synchronized_data=self.synchronized_data,
        )

        payload = dict(
            status=OutlierDetectionRound.OutlierStatus.OUTLIER_DETECTED.value
        )
        serialized_payload = json.dumps(payload, sort_keys=True)
        first_payload, *payloads = [
            OutlierDetectionRoundPayload(
                sender=participant, outlier_detection_data=serialized_payload
            )
            for participant in self.participants
        ]

        # only one participant has voted
        # no event should be returned
        test_round.process_payload(first_payload)
        assert test_round.collection[first_payload.sender] == first_payload
        assert test_round.end_block() is None

        # enough members have voted
        # but no majority is reached
        self._test_no_majority_event(test_round)

        # all members voted in the same way
        for payload in payloads:  # type: ignore
            test_round.process_payload(payload)  # type: ignore

        expected_next_state = cast(
            SynchronizedData,
            self.synchronized_data.update(
                participant_to_outlier_status=self.round_class.serialize_collection(
                    test_round.collection
                ),
                most_voted_outlier_status=cast(
                    OutlierDetectionRoundPayload, payload
                ).json,
            ),
        )

        res = test_round.end_block()
        assert res is not None
        state, event = res
        actual_next_state = cast(SynchronizedData, state)

        # check that the state is updated as expected
        assert actual_next_state.db.get_strict(
            "most_voted_outlier_status"
        ) == expected_next_state.db.get_strict("most_voted_outlier_status")

        # make sure all the votes are as expected
        assert all(
            [
                cast(
                    Dict,
                    actual_next_state.db.get_strict("participant_to_outlier_status"),
                )[participant]
                == actual_vote
                for (participant, actual_vote) in cast(
                    Dict,
                    expected_next_state.db.get_strict("participant_to_outlier_status"),
                ).items()
            ]
        )

        assert event == Event.NO_ACTION

    def test_outlier_not_detected(self) -> None:
        """Test case for when an outlier was not detected."""
        test_round = self.round_class(
            synchronized_data=self.synchronized_data,
        )

        payload = dict(
            status=OutlierDetectionRound.OutlierStatus.OUTLIER_NOT_DETECTED.value
        )
        serialized_payload = json.dumps(payload, sort_keys=True)
        first_payload, *payloads = [
            OutlierDetectionRoundPayload(
                sender=participant, outlier_detection_data=serialized_payload
            )
            for participant in self.participants
        ]

        # only one participant has voted
        # no event should be returned
        test_round.process_payload(first_payload)
        assert test_round.collection[first_payload.sender] == first_payload
        assert test_round.end_block() is None

        # enough members have voted
        # but no majority is reached
        self._test_no_majority_event(test_round)

        # all members voted in the same way
        for payload in payloads:  # type: ignore
            test_round.process_payload(payload)  # type: ignore

        expected_next_state = cast(
            SynchronizedData,
            self.synchronized_data.update(
                participant_to_outlier_status=self.round_class.serialize_collection(
                    test_round.collection
                ),
                most_voted_outlier_status=cast(
                    OutlierDetectionRoundPayload, payload
                ).json,
            ),
        )

        res = test_round.end_block()
        assert res is not None
        state, event = res
        actual_next_state = cast(SynchronizedData, state)

        # check that the state is updated as expected
        assert actual_next_state.db.get_strict(
            "most_voted_outlier_status"
        ) == expected_next_state.db.get_strict("most_voted_outlier_status")

        # make sure all the votes are as expected
        assert all(
            [
                cast(
                    Dict,
                    actual_next_state.db.get_strict("participant_to_outlier_status"),
                )[participant]
                == actual_vote
                for (participant, actual_vote) in cast(
                    Dict,
                    expected_next_state.db.get_strict("participant_to_outlier_status"),
                ).items()
            ]
        )

        assert event == Event.DONE

    def test_err_payload(self) -> None:
        """Test case for when a bad payload is sent."""
        test_round = self.round_class(
            synchronized_data=self.synchronized_data,
        )

        payload: Dict = dict()  # empty dict used for bad payload
        serialized_payload = json.dumps(payload, sort_keys=True)
        first_payload, *payloads = [
            OutlierDetectionRoundPayload(
                sender=participant, outlier_detection_data=serialized_payload
            )
            for participant in self.participants
        ]

        # only one participant has voted
        # no event should be returned
        test_round.process_payload(first_payload)
        assert test_round.collection[first_payload.sender] == first_payload
        assert test_round.end_block() is None

        # enough members have voted
        # but no majority is reached
        self._test_no_majority_event(test_round)

        # all members voted in the same way
        for payload in payloads:  # type: ignore
            test_round.process_payload(payload)  # type: ignore

        res = test_round.end_block()
        assert res is not None
        state, event = res
        actual_next_state = cast(SynchronizedData, state)

        with pytest.raises(ValueError):
            actual_next_state.most_voted_observation  # pylint: disable=pointless-statement

        assert event == Event.NO_ACTION
