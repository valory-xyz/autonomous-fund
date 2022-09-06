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
import json
from abc import abstractmethod
from typing import Dict, Generator, Set, Type, cast

from packages.balancer.skills.fear_and_greed_oracle_abci.models import Params
from packages.balancer.skills.fear_and_greed_oracle_abci.payloads import (
    ObservationRoundPayload,
)
from packages.balancer.skills.fear_and_greed_oracle_abci.rounds import (
    EstimationRound,
    FearAndGreedOracleAbciApp,
    ObservationRound,
    OutlierDetectionRound,
    SynchronizedData,
)
from packages.valory.skills.abstract_round_abci.base import AbstractRound
from packages.valory.skills.abstract_round_abci.behaviours import (
    AbstractRoundBehaviour,
    BaseBehaviour,
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
        """
        Get the data from the Fear and Greed API.

        After the data is received from the API,
        it is shared with the other peers.
        """
        with self.context.benchmark_tool.measure(
            self.behaviour_id,
        ).local():
            api_response = yield from self.get_data()
            self.context.logger.info(
                f"Received data from Fear and Greed API: {api_response}"
            )

        # at this point the agent has the data,
        # and shares it with the other agents (peers)
        with self.context.benchmark_tool.measure(
            self.behaviour_id,
        ).consensus():
            payload = ObservationRoundPayload(
                self.context.agent_address,
                json.dumps(api_response, sort_keys=True),
            )
            yield from self.send_a2a_transaction(payload)
            yield from self.wait_until_round_end()

        self.set_done()

    def get_data(self) -> Generator[None, None, Dict]:
        """
        Get the data from the Fear and Greed API.

        This method can be overridden to get data from whatever source, or collection of sources you want.
        In case of changing the source of the data, make sure the logic in `EstimationBehaviour` is updated accordingly.

        :yield: HttpMessage object
        :return: return the data retrieved from the Fear and Greed API
        """
        response = yield from self.get_http_response(
            method="GET",
            url=self.params.fear_and_greed_endpoint,
        )
        if response.status_code != 200:
            self.context.logger.error(
                f"Could not retrieve data from Fear and Greed API. "
                f"Received status code {response.status_code}."
            )
            return {}

        try:
            response_body = json.loads(response.body)
        except (ValueError, TypeError) as e:
            self.context.logger.error(
                f"Could not parse response from Fear and Greed API, "
                f"the following error was encountered {type(e).__name__}: {e}"
            )
            return {}
        except Exception as e:  # pylint: disable=broad-except
            self.context.logger.error(
                f"An unexpected error was encountered while parsing the Fear and Greed API response "
                f"{type(e).__name__}: {e}"
            )
            return {}

        return response_body


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
    behaviours: Set[Type[BaseBehaviour]] = {
        ObservationBehaviour,  # type: ignore
        EstimationBehaviour,  # type: ignore
        OutlierDetectionRound,  # type: ignore
    }
