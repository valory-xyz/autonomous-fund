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

"""This package contains the rounds of FearAndGreedOracleAbciApp."""
import json
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, cast

from packages.balancer.skills.fear_and_greed_oracle_abci.payloads import (
    EstimationRoundPayload,
    ObservationRoundPayload,
    OutlierDetectionRoundPayload,
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
    """Defines the events for this abci."""

    ROUND_TIMEOUT = "round_timeout"
    DONE = "done"
    NO_ACTION = "no_action"
    NO_MAJORITY = "no_majority"


class SynchronizedData(BaseSynchronizedData):
    """
    Class to represent the synchronized data.

    This data is replicated by the tendermint application.
    """

    @property
    def participant_to_observations(self) -> Dict:
        """Get the participant_to_observations."""
        return cast(Dict, self.db.get_strict("participant_to_observations"))

    @property
    def most_voted_observation(self) -> Dict:
        """Get the participant_to_observations."""
        return cast(Dict, self.db.get_strict("most_voted_observation"))

    @property
    def participant_to_estimates(self) -> Dict:
        """Get the participant_to_estimates."""
        return cast(Dict, self.db.get_strict("participant_to_estimates"))

    @property
    def most_voted_estimates(self) -> str:
        """Get the most_voted_estimates."""
        return cast(str, self.db.get_strict("most_voted_estimates"))


class ObservationRound(CollectSameUntilThresholdRound):
    """A round in which agents collect observations"""

    payload_class = ObservationRoundPayload
    payload_attribute = "observation_data"
    synchronized_data_class = SynchronizedData

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Event]]:
        """Process the end of the block."""
        if self.threshold_reached:
            payload = json.loads(self.most_voted_payload)
            if payload == {}:
                return self.synchronized_data, Event.NO_ACTION

            state = self.synchronized_data.update(
                synchronized_data_class=self.synchronized_data_class,
                **{
                    get_name(
                        SynchronizedData.participant_to_observations
                    ): self.collection,
                    get_name(SynchronizedData.most_voted_observation): payload,
                },
            )
            return state, Event.DONE
        if not self.is_majority_possible(
            self.collection, self.synchronized_data.nb_participants
        ):
            return self.synchronized_data, Event.NO_MAJORITY

        return None


class EstimationRound(CollectSameUntilThresholdRound):
    """A round that in which the data processing logic is done."""

    payload_class = EstimationRoundPayload
    payload_attribute = "estimation_data"
    synchronized_data_class = SynchronizedData
    done_event = Event.DONE
    none_event = Event.NO_ACTION
    no_majority_event = Event.NO_MAJORITY
    collection_key = get_name(SynchronizedData.participant_to_estimates)
    selection_key = get_name(SynchronizedData.most_voted_estimates)


class OutlierDetectionRound(CollectSameUntilThresholdRound):
    """A round in which outlier detection is done."""

    payload_class = OutlierDetectionRoundPayload
    payload_attribute = "outlier_detection_data"
    synchronized_data_class = SynchronizedData

    class OutlierStatus(Enum):
        """Defines the possible status the outlier check may result in."""

        OUTLIER_DETECTED = "outlier_detected"
        OUTLIER_NOT_DETECTED = "outlier_not_detected"
        INVALID_STATE = "invalid_state"

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Event]]:
        """Process the end of the block."""
        if self.threshold_reached:
            payload = json.loads(self.most_voted_payload)
            if payload == {}:
                # this should never happen, however if it does
                # we don't take any action
                return self.synchronized_data, Event.NO_ACTION

            status = payload.get("status", self.OutlierStatus.INVALID_STATE.value)
            state = self.synchronized_data.update(
                synchronized_data_class=self.synchronized_data_class,
                participant_to_outlier_status=self.collection,
                most_voted_outlier_status=payload,
            )
            if status == self.OutlierStatus.OUTLIER_NOT_DETECTED.value:
                return state, Event.DONE

            return state, Event.NO_ACTION
        if not self.is_majority_possible(
            self.collection, self.synchronized_data.nb_participants
        ):
            return self.synchronized_data, Event.NO_MAJORITY

        return None


class FinishedDataCollectionRound(DegenerateRound):
    """A degenerate round that acts as the terminal state of FearAndGreedOracleAbciApp."""


class FearAndGreedOracleAbciApp(AbciApp[Event]):
    """A class that defines the transition between rounds in this abci app."""

    initial_round_cls: AppState = ObservationRound
    initial_states: Set[AppState] = {ObservationRound}
    transition_function: AbciAppTransitionFunction = {
        ObservationRound: {
            Event.DONE: EstimationRound,
            Event.ROUND_TIMEOUT: ObservationRound,
            Event.NO_MAJORITY: ObservationRound,
            Event.NO_ACTION: ObservationRound,
        },
        EstimationRound: {
            Event.DONE: OutlierDetectionRound,
            Event.NO_ACTION: ObservationRound,
            Event.NO_MAJORITY: ObservationRound,
            Event.ROUND_TIMEOUT: ObservationRound,
        },
        OutlierDetectionRound: {
            Event.DONE: FinishedDataCollectionRound,
            Event.NO_ACTION: ObservationRound,
            Event.NO_MAJORITY: ObservationRound,
        },
        FinishedDataCollectionRound: {},
    }
    final_states: Set[AppState] = {FinishedDataCollectionRound}
    event_to_timeout: EventToTimeout = {
        Event.ROUND_TIMEOUT: 30.0,
    }
    db_pre_conditions: Dict[AppState, List[str]] = {
        ObservationRound: [],
    }
    db_post_conditions: Dict[AppState, List[str]] = {
        FinishedDataCollectionRound: [
            get_name(SynchronizedData.participant_to_observations),
            get_name(SynchronizedData.most_voted_observation),
            get_name(SynchronizedData.participant_to_estimates),
            get_name(SynchronizedData.most_voted_estimates),
        ]
    }
    cross_period_persisted_keys: List[str] = []
