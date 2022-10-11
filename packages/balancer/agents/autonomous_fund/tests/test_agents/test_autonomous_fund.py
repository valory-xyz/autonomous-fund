# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2021-2022 Valory AG
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
# pylint: skip-file
# mypy: ignore-errors
# flake8: noqa

"""End-to-End tests for the balancer/autonomous_fund agent."""

import pytest
from aea_test_autonomy.fixture_helpers import (  # noqa: F401
    abci_host,
    abci_port,
    flask_tendermint,
    tendermint_port,
)

from packages.balancer.agents.autonomous_fund.tests.helpers.fixtures import (
    UseHardHatAutoFundBaseTest,
    UseMockFearAndGreedApiBaseTest,
)
from packages.balancer.agents.autonomous_fund.tests.test_agents.base import (
    BaseTestAutonomousFundEnd2End,
)


TIME_TO_FINISH = 60  # 1 minute
TARGET_AGENT = "balancer/autonomous_fund:0.1.0"
TARGET_SKILL = "balancer/autonomous_fund_abci:0.1.0"

REGISTRATION_CHECK_STRINGS = (
    "Entered in the 'registration_startup' round for period 0",
    "'registration_startup' round is done",
)

_expected_api_response = (
    '[{"timestamp": 1665360000, "value": 22}, {"timestamp": 1665273600, "value": 22}]'
)
_expected_outlier_status = '{"status": "outlier_not_detected"}'
FEAR_AND_GREED_ORACLE_STRINGS = (
    "Entered in the 'collect_observation' round for period 0",
    f"Received data from Fear and Greed API: {_expected_api_response}",
    "Entered in the 'estimation_round' round for period 0",
    "Estimated Fear and Greed Index values to be ",
    "Entered in the 'outlier_detection_round' round for period 0",
    f"Outlier detection status: {_expected_outlier_status}",
)

_expected_update_weights_decision = '{"weights": [60, 30, 10]}'
POOL_MANAGER_STRINGS = (
    "Entered in the 'decision_making' round for period 0",
    f"Updated weights decision: {_expected_update_weights_decision}",
    "Entered in the 'update_pool_tx' round for period 0",
    "Prepared safe tx:",
)

TRANSACTION_SUBMISSION_STRINGS = (
    "Entered in the 'validate_transaction' round for period 0",
    "Verified result: True",
)

RESET_STRINGS = (
    "Entered in the 'reset_and_pause' round for period 0",
    "Period end.",
)


@pytest.mark.parametrize("nb_nodes", (1,))
class TestAutonomousFundSingleAgent(
    BaseTestAutonomousFundEnd2End,
    UseMockFearAndGreedApiBaseTest,
    UseHardHatAutoFundBaseTest,
):
    """
    Test the Autonomous Fund through the happy path, when using a single agent.

    By running this test, we spawn up a single agent service, along with the external dependencies:
        - tendermint
        - a hardhat network
        - a mock Fear and Greed API server
    The test firstly takes care of the setting up the dependencies, and then runs the service.
    The test passes if the agent produces all the logs in specified in `strict_check_strings`.
    """

    agent_package = TARGET_AGENT
    skill_package = TARGET_SKILL
    wait_to_finish = TIME_TO_FINISH
    strict_check_strings = (
        REGISTRATION_CHECK_STRINGS
        + FEAR_AND_GREED_ORACLE_STRINGS
        + POOL_MANAGER_STRINGS
        + TRANSACTION_SUBMISSION_STRINGS
        + RESET_STRINGS
    )
    use_benchmarks = True


@pytest.mark.parametrize("nb_nodes", (2,))
class TestAutonomousFundTwoAgents(
    BaseTestAutonomousFundEnd2End,
    UseMockFearAndGreedApiBaseTest,
    UseHardHatAutoFundBaseTest,
):
    """
    Test the Autonomous Fund through the "happy path", when using two agents.

    By running this test, we spawn up a single agent service, along with the external dependencies:
        - tendermint
        - a hardhat network
        - a mock Fear and Greed API server
    The test firstly takes care of the setting up the dependencies, and then runs the service.
    The test passes if both agents produce all the logs in specified in `strict_check_strings`.
    """

    agent_package = TARGET_AGENT
    skill_package = TARGET_SKILL
    wait_to_finish = TIME_TO_FINISH
    strict_check_strings = (
        REGISTRATION_CHECK_STRINGS
        + FEAR_AND_GREED_ORACLE_STRINGS
        + POOL_MANAGER_STRINGS
        + TRANSACTION_SUBMISSION_STRINGS
        + RESET_STRINGS
    )
    use_benchmarks = True


@pytest.mark.parametrize("nb_nodes", (4,))
class TestAutonomousFundFourAgents(
    BaseTestAutonomousFundEnd2End,
    UseMockFearAndGreedApiBaseTest,
    UseHardHatAutoFundBaseTest,
):
    """
    Test the Autonomous Fund through the "happy path", when using 4 agents.

    By running this test, we spawn up a single agent service, along with the external dependencies:
        - tendermint
        - a hardhat network
        - a mock Fear and Greed API server
    The test firstly takes care of the setting up the dependencies, and then runs the service.
    The test passes if all 4 agents produce all the logs in specified in `strict_check_strings`.
    """

    agent_package = TARGET_AGENT
    skill_package = TARGET_SKILL
    wait_to_finish = TIME_TO_FINISH
    strict_check_strings = (
        REGISTRATION_CHECK_STRINGS
        + FEAR_AND_GREED_ORACLE_STRINGS
        + POOL_MANAGER_STRINGS
        + TRANSACTION_SUBMISSION_STRINGS
        + RESET_STRINGS
    )
    use_benchmarks = True
