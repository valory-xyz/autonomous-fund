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

"""This package contains the tests for rounds of LiquidityProvision."""

from typing import Dict, cast

import pytest

from packages.balancer.skills.liquidity_provision_abci.payloads import (
    AllowListUpdatePayload,
)
from packages.balancer.skills.liquidity_provision_abci.rounds import (
    AllowListUpdateRound,
    Event,
    SynchronizedData,
)
from packages.valory.skills.abstract_round_abci.test_tools.rounds import (
    BaseRoundTestClass,
)


MAX_PARTICIPANTS: int = 4


class TestAllowListUpdateRound(BaseRoundTestClass):
    """Tests for AllowListUpdateRound."""

    round_class = AllowListUpdateRound
    synchronized_data: SynchronizedData
    _synchronized_data_class = SynchronizedData
    _event_class = Event

    @pytest.mark.parametrize(
        "payload_data, expected_event",
        [
            ("0xTX_hash", Event.DONE),
            (
                AllowListUpdateRound.NoUpdatePayloads.NO_UPDATE_PAYLOAD.value,
                Event.NO_ACTION,
            ),
            (AllowListUpdateRound.NoUpdatePayloads.ERROR_PAYLOAD.value, Event.ERROR),
        ],
    )
    def test_run(self, payload_data: str, expected_event: Event) -> None:
        """Run round tests."""
        test_round = self.round_class(
            synchronized_data=self.synchronized_data,
            consensus_params=self.consensus_params,
        )
        first_payload, *payloads = [
            AllowListUpdatePayload(sender=participant, allow_list_update=payload_data)
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

        if expected_event == Event.DONE:
            # check that the state is updated as expected
            assert (
                actual_next_state.most_voted_tx_hash
                == expected_next_state.most_voted_tx_hash
            )

            # make sure all the votes are as expected
            assert all(
                [
                    cast(Dict, actual_next_state.participant_to_tx_hash)[participant]
                    == actual_vote
                    for (participant, actual_vote) in cast(
                        Dict, expected_next_state.participant_to_tx_hash
                    ).items()
                ]
            )

        assert event == expected_event
