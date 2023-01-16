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
import packages.balancer.skills.autonomous_fund_abci.multiplexer as TxMultiplexingAbci
import packages.balancer.skills.fear_and_greed_oracle_abci.rounds as FearAndGreedAbci
import packages.balancer.skills.liquidity_provision_abci.rounds as LiqudityProvisionAbci
import packages.balancer.skills.pool_manager_abci.rounds as PoolManagerAbci
import packages.valory.skills.registration_abci.rounds as RegistrationAbci
import packages.valory.skills.reset_pause_abci.rounds as ResetAndPauseAbci
import packages.valory.skills.transaction_settlement_abci.rounds as TransactionSubmissionAbci
from packages.valory.skills.abstract_round_abci.abci_app_chain import (
    AbciAppTransitionMapping,
    chain,
)
from packages.valory.skills.termination_abci.rounds import BackgroundRound
from packages.valory.skills.termination_abci.rounds import Event as TerminationEvent
from packages.valory.skills.termination_abci.rounds import TerminationAbciApp


# here we define how the transition between the FSMs should happen
# more information here: https://docs.autonolas.network/fsm_app_introduction/#composition-of-fsm-apps
abci_app_transition_mapping: AbciAppTransitionMapping = {
    RegistrationAbci.FinishedRegistrationRound: LiqudityProvisionAbci.AllowListUpdateRound,
    FearAndGreedAbci.FinishedDataCollectionRound: PoolManagerAbci.DecisionMakingRound,
    PoolManagerAbci.FinishedTxPreparationRound: TransactionSubmissionAbci.RandomnessTransactionSubmissionRound,
    PoolManagerAbci.FinishedWithoutTxRound: ResetAndPauseAbci.ResetAndPauseRound,
    LiqudityProvisionAbci.FinishedAllowlistTxPreparationRound: TransactionSubmissionAbci.RandomnessTransactionSubmissionRound,
    LiqudityProvisionAbci.FinishedWithoutAllowlistTxRound: FearAndGreedAbci.ObservationRound,
    TransactionSubmissionAbci.FinishedTransactionSubmissionRound: TxMultiplexingAbci.PostTransactionSettlementRound,
    TxMultiplexingAbci.FinishedAllowlistUpdateRound: FearAndGreedAbci.ObservationRound,
    TxMultiplexingAbci.FinishedWeightUpdateRound: ResetAndPauseAbci.ResetAndPauseRound,
    ResetAndPauseAbci.FinishedResetAndPauseRound: FearAndGreedAbci.ObservationRound,
    TransactionSubmissionAbci.FailedRound: LiqudityProvisionAbci.AllowListUpdateRound,
    ResetAndPauseAbci.FinishedResetAndPauseErrorRound: RegistrationAbci.RegistrationRound,
}


AutonomousFundAbciApp = chain(
    (
        RegistrationAbci.AgentRegistrationAbciApp,
        FearAndGreedAbci.FearAndGreedOracleAbciApp,
        PoolManagerAbci.PoolManagerAbciApp,
        TxMultiplexingAbci.TransactionSettlementAbciMultiplexer,
        TransactionSubmissionAbci.TransactionSubmissionAbciApp,
        ResetAndPauseAbci.ResetPauseAbciApp,
        LiqudityProvisionAbci.LiquidityProvisionAbciApp,
    ),
    abci_app_transition_mapping,
).add_termination(
    background_round_cls=BackgroundRound,
    termination_event=TerminationEvent.TERMINATE,
    termination_abci_app=TerminationAbciApp,
)
