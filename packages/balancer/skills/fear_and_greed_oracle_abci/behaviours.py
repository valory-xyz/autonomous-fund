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

"""This package contains round behaviours of FearAndGreedOracleAbciApp."""

from abc import abstractmethod
from typing import Generator, Set, Type, cast

from packages.valory.skills.abstract_round_abci.base import AbstractRound
from packages.valory.skills.abstract_round_abci.behaviours import (
    AbstractRoundBehaviour,
    BaseBehaviour,
)

from packages.balancer.skills.fear_and_greed_oracle_abci.models import Params
from packages.balancer.skills.fear_and_greed_oracle_abci.rounds import (
    SynchronizedData,
    FearAndGreedOracleAbciApp,
    ObservationRound,
    EstimationRound, OutlierDetectionRound,
)


class FearAndGreedOracleBaseBehaviour(BaseBehaviour):
    """Base behaviour for the common apps' skill."""

    @property
    def synchronized_data(self) -> SynchronizedData:
        """Return the synchronized data."""
        return cast(SynchronizedData, super().synchronized_data)

    @property
    def params(self) -> Params:
        """Return the params."""
        return cast(Params, super().params)


class ObservationBehaviour(FearAndGreedOracleBaseBehaviour):
    """Defines the logic used for data collection."""

    state_id: str = "observation"
    behaviour_id: str = "observation_behaviour"
    matching_round: Type[AbstractRound] = ObservationRound

    @abstractmethod
    def async_act(self) -> Generator:
        """Do the act, supporting asynchronous execution."""


class EstimationBehaviour(FearAndGreedOracleBaseBehaviour):
    """Defines the logic used for processing the previously collected data."""

    state_id: str = "estimation"
    behaviour_id: str = "estimation_behaviour"
    matching_round: Type[AbstractRound] = EstimationRound

    @abstractmethod
    def async_act(self) -> Generator:
        """Do the act, supporting asynchronous execution."""

class OutlierDetectionBehaviour(FearAndGreedOracleBaseBehaviour):
    """Defines the logic used for outlier detection."""

    state_id: str = "outlier_detection"
    behaviour_id: str = "outlier_detection_behaviour"
    matching_round: Type[AbstractRound] = OutlierDetectionRound

    @abstractmethod
    def async_act(self) -> Generator:
        """Do the act, supporting asynchronous execution."""

class FearAndGreedOracleRoundBehaviour(AbstractRoundBehaviour):
    """Class to define the behaviours this AbciApp has."""

    initial_behaviour_cls = ObservationBehaviour
    abci_app_cls = FearAndGreedOracleAbciApp  # type: ignore
    behaviours: Set[Type[BaseBehaviour]] = {ObservationBehaviour, EstimationBehaviour, OutlierDetectionRound}
