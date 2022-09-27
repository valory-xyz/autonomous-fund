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

"""This module contains the shared state for the abci skill of AutonomousFundAbciApp."""

from typing import Any

from packages.balancer.skills.autonomous_fund_abci.composition import (
    AutonomousFundAbciApp,
)
from packages.valory.skills.reset_pause_abci.rounds import Event as ResetPauseEvent
from packages.valory.skills.safe_deployment_abci.rounds import Event as SafeEvent
from packages.valory.skills.transaction_settlement_abci.models import TransactionParams
from packages.valory.skills.transaction_settlement_abci.rounds import Event as TSEvent
from packages.balancer.skills.fear_and_greed_oracle_abci.rounds import Event as FearAndGreedOracleEvent
from packages.balancer.skills.pool_manager_abci.rounds import Event as PoolManagerEvent
from packages.valory.skills.abstract_round_abci.models import (
    BenchmarkTool as BaseBenchmarkTool, ApiSpecs,
)
from packages.valory.skills.abstract_round_abci.models import Requests as BaseRequests
from packages.valory.skills.abstract_round_abci.models import (
    SharedState as BaseSharedState,
)
from packages.balancer.skills.fear_and_greed_oracle_abci.models import Params as FearAndGreedOracleParams
from packages.balancer.skills.pool_manager_abci.models import Params as PoolManagerParams

MARGIN = 5
MULTIPLIER = 2

FearAndGreedOracleParams = FearAndGreedOracleParams
PoolManagerParams = PoolManagerParams
Requests = BaseRequests
BenchmarkTool = BaseBenchmarkTool

class RandomnessApi(ApiSpecs):
    """A model that wraps ApiSpecs for randomness api specifications."""



class SharedState(BaseSharedState):
    """Keep the current shared state of the skill."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the state."""
        super().__init__(*args, abci_app_cls=AutonomousFundAbciApp, **kwargs)

    def setup(self) -> None:
        """Set up."""
        super().setup()
        AutonomousFundAbciApp.event_to_timeout[
            PoolManagerEvent.ROUND_TIMEOUT
        ] = self.context.params.round_timeout_seconds
        AutonomousFundAbciApp.event_to_timeout[
            SafeEvent.ROUND_TIMEOUT
        ] = self.context.params.round_timeout_seconds
        AutonomousFundAbciApp.event_to_timeout[
            FearAndGreedOracleEvent.ROUND_TIMEOUT
        ] = self.context.params.round_timeout_seconds
        AutonomousFundAbciApp.event_to_timeout[
            TSEvent.ROUND_TIMEOUT
        ] = self.context.params.round_timeout_seconds
        AutonomousFundAbciApp.event_to_timeout[
            ResetPauseEvent.ROUND_TIMEOUT
        ] = self.context.params.round_timeout_seconds
        AutonomousFundAbciApp.event_to_timeout[TSEvent.RESET_TIMEOUT] = (
            self.context.params.round_timeout_seconds * MULTIPLIER
        )

class Params(PoolManagerParams, TransactionParams, FearAndGreedOracleParams):
    """holder class"""


