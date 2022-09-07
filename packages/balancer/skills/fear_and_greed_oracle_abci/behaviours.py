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
import statistics
from abc import abstractmethod
from typing import Callable, Dict, Generator, List, Set, Tuple, Type, cast

from packages.balancer.skills.fear_and_greed_oracle_abci.models import Params
from packages.balancer.skills.fear_and_greed_oracle_abci.payloads import (
    EstimationRoundPayload,
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


TIMESTAMP_KEY = "timestamp"
VALUE_KEY = "value"


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
                api_response,
            )
            yield from self.send_a2a_transaction(payload)
            yield from self.wait_until_round_end()

        self.set_done()

    def get_data(self) -> Generator[None, None, str]:
        """
        Get the data from the Fear and Greed API.

        This method can be overridden to get data from whatever source, or collection of sources you want.
        In case of changing the source of the data, make sure the logic in `EstimationBehaviour` is updated accordingly.
        The ObservationRound is of type (subclass) of type CollectSameUntilThresholdRound. This round type expects the
        payload to be the same. In case the payload is expected to be different for each agent, for example each
        agent/peer has with their own datasource, then you should use CollectDifferentUntilAllRound.
        See https://github.com/valory-xyz/open-autonomy/tree/v0.2.1.post1/packages/valory/skills/price_estimation_abci
        for an example that works in the latter way.

        :yield: HttpMessage object
        :return: return the data retrieved from the Fear and Greed API, in case something goes wrong we return "{}".
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
            return "{}"

        try:
            # we parse the response bytes into a dict
            # checkout https://api.alternative.me/fng/?limit=2&format=json for a response example
            index_updates = json.loads(response.body)["data"]
            response_body = [
                {
                    VALUE_KEY: int(index_update[VALUE_KEY]),
                    TIMESTAMP_KEY: int(index_update[TIMESTAMP_KEY]),
                }
                for index_update in index_updates
            ]

        except (ValueError, TypeError) as e:
            self.context.logger.error(
                f"Could not parse response from Fear and Greed API, "
                f"the following error was encountered {type(e).__name__}: {e}"
            )
            return "{}"
        except Exception as e:  # pylint: disable=broad-except
            self.context.logger.error(
                f"An unexpected error was encountered while parsing the Fear and Greed API response "
                f"{type(e).__name__}: {e}"
            )
            return "{}"

        # We dump the json into a string, notice the sort_keys=True
        # we MUST ensure that they keys are ordered in the same way
        # otherwise the payload MAY end up being different on different
        # agents. This can happen in case the API responds with keys
        # in different order, which can happen since there is no requirement
        # against this. Here we only have 2 keys, but we cannot guarantee
        # the order without sort_keys=True.
        deterministic_body = json.dumps(response_body, sort_keys=True)
        return deterministic_body


class EstimationBehaviour(FearAndGreedOracleBaseBehaviour):
    """Defines the logic used for processing the previously collected data."""

    state_id: str = "estimation"
    behaviour_id: str = "estimation_behaviour"
    matching_round: Type[AbstractRound] = EstimationRound

    _aggregator_methods: Dict[str, Callable] = {
        "mean": statistics.mean,
        "median": statistics.median,
        "mode": statistics.mode,
    }

    def async_act(self) -> Generator:
        """Accumulate responses from the previous round, and come up with a single number (estimate) for the index."""
        with self.context.benchmark_tool.measure(self.behaviour_id).local():
            estimate_data = self.get_estimate()
            self.context.logger.info(
                f"Estimated Fear and Greed Index values to be {estimate_data}",
            )
        with self.context.benchmark_tool.measure(self.behaviour_id).consensus():
            payload = EstimationRoundPayload(
                self.context.agent_address,
                estimate_data,
            )
            yield from self.send_a2a_transaction(payload)
            yield from self.wait_until_round_end()

        self.set_done()

    def get_estimate(self) -> str:
        """
        Get the estimate, by applying the aggregate method across multiple points, for both the value and timestamp.

        Example:
        Given observations:
            - agent A has observed [(t_a1, v_a1), (t_a2, v_a2)]
            - agent B has observed [(t_b1, v_b1), (t_b2, v_b2)]
        and an aggregate function aggregate(), this method aggregates the points per type.

        So the observations above would be combined into:

        values = [aggregate([v_a1, v_b1]), aggregate([v_a2, v_b2])]
        timestamps = [aggregate([t_a1, t_b1]), aggregate([t_a2, t_b2])]

        :return: values, timestamp obtained as explained above.
        """
        aggregator_method = self._aggregator_methods.get(
            self.params.observation_aggregator_function,
            self._aggregator_methods["median"],
        )
        timestamps, values = self._observations_per_point()
        aggregated_values, aggregated_timestamps = [], []
        for i in range(self.params.fear_and_greed_num_points):
            ith_values = values[i]
            ith_timestamps = timestamps[i]

            aggregated_values.append(aggregator_method(ith_values))
            aggregated_timestamps.append(aggregator_method(ith_timestamps))

        estimate_data = dict(
            value_estimates=aggregated_values, timestamp_estimates=aggregated_timestamps
        )
        serialized_data = json.dumps(estimate_data, sort_keys=True)
        return serialized_data

    def _observations_per_point(self) -> Tuple[List, List]:
        """
        Formats the observation in arrays per observation point.

        Example:
        Given observations:
            - agent A has observed [(t_a1, v_a1), (t_a2, v_a2)]
            - agent B has observed [(t_b1, v_b1), (t_b2, v_b2)]

        This method combines the points per type.
        So the observations above would be combined into:
        values = [[v_a1, v_b1], [v_a1, v_b1]]
        timestamps = [[t_a1, t_b1], [t_a2, t_b2]]

        :returns: values and timestamps as described above.
        """
        values: List[List] = [[] for _ in range(self.params.fear_and_greed_num_points)]
        timestamps: List[List] = [
            [] for _ in range(self.params.fear_and_greed_num_points)
        ]
        for observation in self.synchronized_data.participant_to_observations.values():
            index_values = observation.observation_data
            if len(index_values) != self.params.fear_and_greed_num_points:
                self.context.logger.warning(
                    f"Expected {self.params.fear_and_greed_num_points} points, found {len(index_values)}"
                )
                continue

            i = 0
            for index_value in index_values:
                ith_values = values[i]
                ith_timestamps = timestamps[i]

                ith_values.append(index_value[VALUE_KEY])
                ith_timestamps.append(index_value[TIMESTAMP_KEY])
                i += 1
        return timestamps, values


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
