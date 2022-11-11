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

"""This package contains the tests for rounds of PoolManagerAbciApp."""
import json
from dataclasses import dataclass, field
from typing import Callable, Dict, Hashable, List, cast

import pytest

from packages.balancer.skills.pool_manager_abci.payloads import (
    DecisionMakingPayload,
    UpdatePoolTxPayload,
)
from packages.balancer.skills.pool_manager_abci.rounds import (
    DecisionMakingRound,
    Event,
    SynchronizedData,
    UpdatePoolTxRound,
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


class BasePoolManagerRoundTestClass(
    BaseRoundTestClass
):  # pylint: disable=too-few-public-methods
    """Base test class for PoolManager rounds."""

    synchronized_data: SynchronizedData
    _synchronized_data_class = SynchronizedData
    _event_class = Event


class TestDecisionMakingRound(BasePoolManagerRoundTestClass):
    """Tests for DecisionMakingRound."""

    round_class = DecisionMakingRound

    def test_run(self) -> None:
        """Tests the happy path for DecisionMakingRound."""
        test_round = self.round_class(
            synchronized_data=self.synchronized_data,
            consensus_params=self.consensus_params,
        )
        dummy_weights = [123, 123, 123]
        payload_data = json.dumps(dict(weights=dummy_weights))
        first_payload, *payloads = [
            DecisionMakingPayload(participant, payload_data)
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
                participant_to_decision=test_round.collection,
                most_voted_weights=dummy_weights,
            ),
        )

        res = test_round.end_block()
        assert res is not None
        state, event = res
        actual_next_state = cast(SynchronizedData, state)

        # check that the state is updated as expected
        assert (
            actual_next_state.most_voted_weights
            == expected_next_state.most_voted_weights
        )

        # make sure all the votes are as expected
        assert all(
            [
                cast(Dict, actual_next_state.participant_to_decision)[participant]
                == actual_vote
                for (participant, actual_vote) in cast(
                    Dict, expected_next_state.participant_to_decision
                ).items()
            ]
        )

        assert event == Event.DONE

    def test_err_payload(self) -> None:
        """Test case for when a bad payload is sent."""
        test_round = self.round_class(
            synchronized_data=self.synchronized_data,
            consensus_params=self.consensus_params,
        )

        payload_data = DecisionMakingRound.NO_UPDATE_PAYLOAD
        first_payload, *payloads = [
            DecisionMakingPayload(participant, payload_data)
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
            actual_next_state.most_voted_weights  # pylint: disable=pointless-statement

        assert event == Event.NO_ACTION


class TestUpdatePoolTxRound(BasePoolManagerRoundTestClass):
    """Tests for UpdatePoolTxRound."""

    round_class = UpdatePoolTxRound

    def test_run(self) -> None:
        """Tests the happy path for UpdatePoolTxRound."""
        test_round = self.round_class(
            synchronized_data=self.synchronized_data,
            consensus_params=self.consensus_params,
        )
        payload_data = "0x-test-123"
        first_payload, *payloads = [
            UpdatePoolTxPayload(sender=participant, update_pool_tx=payload_data)
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
                participant_to_tx=test_round.collection,
                most_voted_tx=payload_data,
            ),
        )

        res = test_round.end_block()
        assert res is not None
        state, event = res
        actual_next_state = cast(SynchronizedData, state)

        # check that the state is updated as expected
        assert (
            actual_next_state.most_voted_tx_hash
            == expected_next_state.most_voted_tx_hash
        )

        # make sure all the votes are as expected
        assert all(
            [
                cast(Dict, actual_next_state.participant_to_tx)[participant]
                == actual_vote
                for (participant, actual_vote) in cast(
                    Dict, expected_next_state.participant_to_tx
                ).items()
            ]
        )

        assert event == Event.DONE

    def test_err_payload(self) -> None:
        """Test case for when a bad payload is sent."""
        test_round = self.round_class(
            synchronized_data=self.synchronized_data,
            consensus_params=self.consensus_params,
        )

        payload_data = UpdatePoolTxRound.ERROR_PAYLOAD
        first_payload, *payloads = [
            UpdatePoolTxPayload(sender=participant, update_pool_tx=payload_data)
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
            actual_next_state.most_voted_tx_hash  # pylint: disable=pointless-statement

        assert event == Event.NO_ACTION
