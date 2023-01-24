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

"""This module contains the shared state for the abci skill of PoolManagerAbciApp."""
from copy import deepcopy
from typing import Any, Dict, List, Tuple

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

    abci_app_cls = PoolManagerAbciApp


class Params(BaseParams):
    """Parameters."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the parameters object."""
        self.pool_tokens: List[str] = self._ensure(
            "pool_tokens", kwargs, type_=List[str]
        )
        self.pool_weights: Dict[int, List[int]] = self._ensure_pool_weights(kwargs)
        self.pool_tokens, self.pool_weights = self._sort(
            self.pool_tokens, self.pool_weights
        )
        self.weight_update_timespan: int = self._ensure_weight_update_timespan(kwargs)
        self.managed_pool_address: str = self._ensure_managed_pool_address(kwargs)
        self.weight_tolerance: float = self._ensure(
            "weight_tolerance", kwargs, type_=float
        )
        super().__init__(*args, **kwargs)

    def _ensure_pool_weights(self, kwargs: Dict) -> Dict[int, List[int]]:
        """Checks that the "pool_weights" param exists and that the weights sum up to 100%."""
        num_tokens = len(self.pool_tokens)
        all_pool_weights: Dict[int, List[int]] = self._ensure(
            "pool_weights", kwargs, type_=Dict[int, List[int]]
        )
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
        weight_update_timespan: int = self._ensure(
            "weight_update_timespan", kwargs, type_=int
        )
        enforce(weight_update_timespan > 0, "weight_update_timespan MUST be positive.")
        return weight_update_timespan

    def _ensure_managed_pool_address(  # pylint: disable=no-self-use
        self, kwargs: Dict
    ) -> str:
        """Ensure that the ManagedPool address is available."""
        managed_pool_address = kwargs.get("managed_pool_address", None)
        enforce(
            managed_pool_address is not None,
            "'managed_pool_address' is a required parameter",
        )
        return managed_pool_address

    @staticmethod
    def _sort(
        tokens: List[str], weights: Dict[int, List[int]]
    ) -> Tuple[List[str], Dict[int, List[int]]]:
        """Sort the tokens in alphabetic order, and ensure the weights reflect the same order."""
        sorted_tokens = deepcopy(tokens)
        sorted_tokens.sort()
        sorted_weights = deepcopy(weights)

        new_index = 0
        for token in sorted_tokens:
            # the tokens are now sorted, we sort the weights at each key
            # we manipulate the order of the weights in the same way we
            # have manipulated the order of the tokens
            original_index = tokens.index(token)
            for key in weights.keys():
                sorted_weights[key][new_index] = weights[key][original_index]
            new_index += 1

        return sorted_tokens, sorted_weights


Requests = BaseRequests
BenchmarkTool = BaseBenchmarkTool
