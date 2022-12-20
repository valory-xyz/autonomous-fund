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

"""This module contains the shared state for the abci skill of PoolManagerAbciApp."""

from typing import Any, Dict, List

from aea.exceptions import enforce

from packages.balancer.skills.pool_manager_abci.rounds import PoolManagerAbciApp
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

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the state."""
        super().__init__(*args, abci_app_cls=PoolManagerAbciApp, **kwargs)


class Params(BaseParams):
    """Parameters."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the parameters object."""
        self.pool_tokens: List[str] = self._ensure("pool_tokens", kwargs)
        self.pool_weights: Dict[int, List[int]] = self._ensure_pool_weights(kwargs)
        self.weight_update_timespan: int = self._ensure_weight_update_timespan(kwargs)
        self.managed_pool_address: str = self._ensure("managed_pool_address", kwargs)
        self.weight_tolerance: float = self._ensure("weight_tolerance", kwargs)
        super().__init__(*args, **kwargs)

    def _ensure_pool_weights(self, kwargs: Dict) -> Dict[int, List[int]]:
        """Checks that the "pool_weights" param exists and that the weights sum up to 100%."""
        num_tokens = len(self.pool_tokens)
        all_pool_weights: Dict[int, List[int]] = self._ensure("pool_weights", kwargs)
        for i, pool_weights in all_pool_weights.items():
            enforce(
                sum(pool_weights) == 100,
                f"The pool weights MUST sum up to 100, "
                f"the weights at pool_weights[{i}] do not sum up to 100.",
            )
            enforce(
                len(pool_weights) == num_tokens,
                f"The pool weights MUST be the same length as the number of tokens in the pool, "
                f"the weights at pool_weights[{i}] do not match the number of tokens ({num_tokens}).",
            )
        return all_pool_weights

    def _ensure_weight_update_timespan(self, kwargs: Dict) -> int:
        """Ensure that `weight_update_timespan` exists and that it is positive."""
        weight_update_timespan: int = self._ensure("weight_update_timespan", kwargs)
        enforce(weight_update_timespan > 0, "weight_update_timespan MUST be positive.")
        return weight_update_timespan


Requests = BaseRequests
BenchmarkTool = BaseBenchmarkTool
