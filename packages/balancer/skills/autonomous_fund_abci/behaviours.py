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

"""This package contains round behaviours of AutonomousFundAbciApp."""
from abc import ABC
from typing import Generator, Set, Type, cast

from packages.balancer.skills.autonomous_fund_abci.composition import (
    AutonomousFundAbciApp,
)
from packages.balancer.skills.autonomous_fund_abci.multiplexer import (
    PostTransactionSettlementRound,
    SynchronizedData,
    TransactionSettlementAbciMultiplexer,
)
from packages.balancer.skills.fear_and_greed_oracle_abci.behaviours import (
    FearAndGreedOracleRoundBehaviour,
)
from packages.balancer.skills.liquidity_provision_abci.behaviours import (
    LiquidityProvisionRoundBehaviour,
)
from packages.balancer.skills.pool_manager_abci.behaviours import (
    PoolManagerRoundBehaviour,
)
from packages.valory.skills.abstract_round_abci.behaviours import (
    AbstractRoundBehaviour,
    BaseBehaviour,
)
from packages.valory.skills.registration_abci.behaviours import (
    AgentRegistrationRoundBehaviour,
    RegistrationStartupBehaviour,
)
from packages.valory.skills.reset_pause_abci.behaviours import (
    ResetPauseABCIConsensusBehaviour,
)
from packages.valory.skills.termination_abci.behaviours import (
    BackgroundBehaviour,
    TerminationAbciBehaviours,
)
from packages.valory.skills.transaction_settlement_abci.behaviours import (
    TransactionSettlementRoundBehaviour,
)


class PostTransactionSettlementBehaviour(BaseBehaviour, ABC):
    """
    The post transaction settlement behaviour.

    This behaviour is executed after a tx is settled,
    via the transaction_settlement_abci.
    """

    matching_round = PostTransactionSettlementRound

    @property
    def synchronized_data(self) -> SynchronizedData:
        """Return the synchronized data."""
        return cast(SynchronizedData, super().synchronized_data)

    def async_act(self) -> Generator:
        """Simply log that a tx is settled and wait for round end."""
        self.context.logger.info(
            f"The transaction submitted by {self.synchronized_data.tx_submitter} was successfully settled."
        )
        yield from self.wait_until_round_end()
        self.set_done()


class PostTransactionSettlementFullBehaviour(AbstractRoundBehaviour):
    """The post tx settlement full behaviour."""

    initial_behaviour_cls = PostTransactionSettlementBehaviour
    abci_app_cls = TransactionSettlementAbciMultiplexer
    behaviours: Set[Type[BaseBehaviour]] = {PostTransactionSettlementBehaviour}


class AutonomousFundConsensusBehaviour(AbstractRoundBehaviour):
    """Class to define the behaviours this AbciApp has."""

    initial_behaviour_cls = RegistrationStartupBehaviour
    abci_app_cls = AutonomousFundAbciApp
    behaviours: Set[Type[BaseBehaviour]] = {
        *PostTransactionSettlementFullBehaviour.behaviours,
        *LiquidityProvisionRoundBehaviour.behaviours,
        *FearAndGreedOracleRoundBehaviour.behaviours,
        *PoolManagerRoundBehaviour.behaviours,
        *AgentRegistrationRoundBehaviour.behaviours,
        *TransactionSettlementRoundBehaviour.behaviours,
        *ResetPauseABCIConsensusBehaviour.behaviours,
        *TerminationAbciBehaviours.behaviours,
    }
    background_behaviour_cls = BackgroundBehaviour
