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
from packages.balancer.skills.fear_and_greed_oracle_abci.models import (
    Params as FearAndGreedOracleAbciParams,
)
from packages.balancer.skills.fear_and_greed_oracle_abci.rounds import (
    Event as FearAndGreedOracleEvent,
)
from packages.balancer.skills.liquidity_provision_abci.models import (
    Params as PoolManagerAbciParams,
)
from packages.balancer.skills.pool_manager_abci.models import (
    Params as LiquidityProvisionParams,
)
from packages.balancer.skills.pool_manager_abci.rounds import Event as PoolManagerEvent
from packages.valory.skills.abstract_round_abci.models import (
    BenchmarkTool as BaseBenchmarkTool,
)
from packages.valory.skills.abstract_round_abci.models import Requests as BaseRequests
from packages.valory.skills.abstract_round_abci.models import (
    SharedState as BaseSharedState,
)
from packages.valory.skills.reset_pause_abci.rounds import Event as ResetPauseEvent
from packages.valory.skills.safe_deployment_abci.rounds import Event as SafeEvent
from packages.valory.skills.termination_abci.models import TerminationParams
from packages.valory.skills.transaction_settlement_abci.models import (
    RandomnessApi as TransactionSettlementRandomness,
)
from packages.valory.skills.transaction_settlement_abci.rounds import Event as TSEvent


MARGIN = 5
MULTIPLIER = 2

FearAndGreedOracleParams = FearAndGreedOracleAbciParams
PoolManagerParams = PoolManagerAbciParams
Requests = BaseRequests
BenchmarkTool = BaseBenchmarkTool
RandomnessApi = TransactionSettlementRandomness


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
        AutonomousFundAbciApp.event_to_timeout[
            ResetPauseEvent.RESET_AND_PAUSE_TIMEOUT
        ] = (self.context.params.observation_interval + MARGIN)
        AutonomousFundAbciApp.event_to_timeout[
            SafeEvent.VALIDATE_TIMEOUT
        ] = self.context.params.validate_timeout
        AutonomousFundAbciApp.event_to_timeout[
            TSEvent.VALIDATE_TIMEOUT
        ] = self.context.params.validate_timeout
        AutonomousFundAbciApp.event_to_timeout[
            TSEvent.FINALIZE_TIMEOUT
        ] = self.context.params.finalize_timeout


class Params(
    LiquidityProvisionParams,
    PoolManagerParams,
    FearAndGreedOracleParams,
    TerminationParams,
):
    """A model to represent params for multiple abci apps."""
