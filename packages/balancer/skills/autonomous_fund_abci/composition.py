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

"""This package contains round behaviours of AutonomousFundAbciApp."""
import packages.balancer.skills.fear_and_greed_oracle_abci.rounds as FearAndGreedAbci
import packages.balancer.skills.pool_manager_abci.rounds as PoolManagerAbci
import packages.valory.skills.registration_abci.rounds as RegistrationAbci
import packages.valory.skills.reset_pause_abci.rounds as ResetAndPauseAbci
import packages.valory.skills.safe_deployment_abci.rounds as SafeDeploymentAbci
import packages.valory.skills.transaction_settlement_abci.rounds as TransactionSubmissionAbci
from packages.valory.skills.abstract_round_abci.abci_app_chain import (
    AbciAppTransitionMapping,
    chain,
)


# here we define how the transition between the FSMs should happen
# more information here: https://docs.autonolas.network/fsm_app_introduction/#composition-of-fsm-apps
abci_app_transition_mapping: AbciAppTransitionMapping = {
    RegistrationAbci.FinishedRegistrationRound: SafeDeploymentAbci.RandomnessSafeRound,
    RegistrationAbci.FinishedRegistrationFFWRound: FearAndGreedAbci.ObservationRound,
    SafeDeploymentAbci.FinishedSafeRound: FearAndGreedAbci.ObservationRound,
    FearAndGreedAbci.FinishedDataCollectionRound: PoolManagerAbci.DecisionMakingRound,
    PoolManagerAbci.FinishedTxPreparationRound: TransactionSubmissionAbci.RandomnessTransactionSubmissionRound,
    PoolManagerAbci.FinishedWithoutTxRound: ResetAndPauseAbci.ResetAndPauseRound,
    TransactionSubmissionAbci.FinishedTransactionSubmissionRound: ResetAndPauseAbci.ResetAndPauseRound,
    ResetAndPauseAbci.FinishedResetAndPauseRound: FearAndGreedAbci.ObservationRound,
    TransactionSubmissionAbci.FailedRound: ResetAndPauseAbci.ResetAndPauseRound,
    ResetAndPauseAbci.FinishedResetAndPauseErrorRound: RegistrationAbci.RegistrationRound,
}

AutonomousFundAbciApp = chain(
    (
        RegistrationAbci.AgentRegistrationAbciApp,
        SafeDeploymentAbci.SafeDeploymentAbciApp,
        FearAndGreedAbci.FearAndGreedOracleAbciApp,
        PoolManagerAbci.PoolManagerAbciApp,
        TransactionSubmissionAbci.TransactionSubmissionAbciApp,
        ResetAndPauseAbci.ResetPauseAbciApp,
    ),
    abci_app_transition_mapping,
)
