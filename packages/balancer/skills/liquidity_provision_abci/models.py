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

"""This module contains the shared state for the abci skill of LiquidityProvisionAbciApp."""

from typing import Any, Dict, List

from aea.exceptions import enforce

from packages.balancer.skills.liquidity_provision_abci.rounds import (
    LiquidityProvisionAbciApp,
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

    abci_app_cls = LiquidityProvisionAbciApp


Requests = BaseRequests
BenchmarkTool = BaseBenchmarkTool


class Params(BaseParams):
    """Parameters."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the parameters object."""
        self.enforce_allowlist: bool = self._ensure(
            "enforce_allowlist", kwargs, type_=bool
        )
        self.allowed_lp_addresses: List[str] = self._ensure(
            "allowed_lp_addresses", kwargs, type_=List[str]
        )
        self.managed_pool_address: str = self._ensure_managed_pool_address(kwargs)
        self.multisend_address: str = self._ensure_multisend_address(kwargs)
        super().__init__(*args, **kwargs)

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

    def _ensure_multisend_address(  # pylint: disable=no-self-use
        self, kwargs: Dict
    ) -> str:
        """Ensure that the MultiSend address is available."""
        multisend_address = kwargs.get("multisend_address", None)
        enforce(
            multisend_address is not None,
            "'multisend_address' is a required parameter",
        )
        return multisend_address
