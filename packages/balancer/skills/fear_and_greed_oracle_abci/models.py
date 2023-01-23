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

"""This module contains the shared state for the abci skill of FearAndGreedOracleAbciApp."""

from typing import Any

from packages.balancer.skills.fear_and_greed_oracle_abci.rounds import (
    FearAndGreedOracleAbciApp,
)
from packages.valory.skills.abstract_round_abci.models import BaseParams
from packages.valory.skills.abstract_round_abci.models import (
    BenchmarkTool as BaseBenchmarkTool,
)
from packages.valory.skills.abstract_round_abci.models import Requests as BaseRequests
from packages.valory.skills.abstract_round_abci.models import (
    SharedState as BaseSharedState,
)


class SharedState(BaseSharedState):
    """Keep the current shared state of the skill."""

    abci_app_cls = FearAndGreedOracleAbciApp


class Params(BaseParams):
    """Parameters."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the parameters object."""
        self.fear_and_greed_num_points: int = self._ensure(
            "fear_and_greed_num_points", kwargs, type_=int
        )
        fear_and_greed_base_endpoint: str = self._ensure(
            "fear_and_greed_endpoint", kwargs, type_=str
        )
        self.fear_and_greed_endpoint: str = (
            f"{fear_and_greed_base_endpoint}&limit={self.fear_and_greed_num_points}"
        )
        self.observation_aggregator_function = self._ensure(
            "observation_aggregator_function",
            kwargs,
            type_=str,
        )
        self.min_index_value: int = self._ensure("min_index_value", kwargs, type_=int)
        self.max_index_value: int = self._ensure("max_index_value", kwargs, type_=int)
        self.max_index_change: float = self._ensure(
            "max_index_change", kwargs, type_=float
        )
        super().__init__(*args, **kwargs)


Requests = BaseRequests
BenchmarkTool = BaseBenchmarkTool
