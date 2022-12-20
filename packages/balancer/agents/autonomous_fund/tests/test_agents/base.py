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
# pylint: disable=broad-except,unspecified-encoding,import-error,redefined-outer-name

"""End2End tests base classes for the Autonomous Fund."""

from aea.configurations.base import PublicId
from aea_test_autonomy.base_test_classes.agents import BaseTestEnd2End

from packages.balancer.agents.autonomous_fund.tests.helpers.constants import (
    CONFIGURED_SAFE_INSTANCE as _DEFAULT_SAFE_CONTRACT_ADDRESS,
)
from packages.balancer.agents.autonomous_fund.tests.helpers.constants import (
    DEFAULT_CALLBACK_HANDLER as _DEFAULT_SAFE_CALLBACK_HANDLER_ADDRESS,
)
from packages.balancer.agents.autonomous_fund.tests.helpers.constants import (
    MANAGED_POOL as _DEFAULT_MANAGED_POOL_ADDRESS,
)
from packages.balancer.agents.autonomous_fund.tests.helpers.constants import (
    MOCK_API_PATH as _DEFAULT_MOCK_API_PATH,
)
from packages.balancer.agents.autonomous_fund.tests.helpers.docker import (
    DEFAULT_JSON_SERVER_ADDR as _DEFAULT_JSON_SERVER_ADDR,
)
from packages.balancer.agents.autonomous_fund.tests.helpers.docker import (
    DEFAULT_JSON_SERVER_PORT as _DEFAULT_JSON_SERVER_PORT,
)


TERMINATION_TIMEOUT = 120


class BaseTestAutonomousFundEnd2End(
    BaseTestEnd2End
):  # pylint: disable=too-few-public-methods
    """
    Extended base class for conducting E2E tests with the Autonomous Fund.

    Test subclasses must set NB_AGENTS, agent_package, wait_to_finish and check_strings.
    """

    cli_log_options = ["-v", "INFO"]  # no need for debug
    skill_package = "balancer/autonomous_fund_abci:0.1.0"

    # mock Fear and Greed API constants
    MOCK_API_ADDRESS = _DEFAULT_JSON_SERVER_ADDR
    MOCK_API_PORT = _DEFAULT_JSON_SERVER_PORT
    MOCK_API_PATH = _DEFAULT_MOCK_API_PATH

    # contract related constants
    SAFE_CALLBACK_HANDLER = _DEFAULT_SAFE_CALLBACK_HANDLER_ADDRESS
    SAFE_CONTRACT_ADDRESS = _DEFAULT_SAFE_CONTRACT_ADDRESS
    MANAGED_POOL_ADDRESS = _DEFAULT_MANAGED_POOL_ADDRESS

    __args_prefix = f"vendor.balancer.skills.{PublicId.from_str(skill_package).name}.models.params.args"
    extra_configs = [
        {
            "dotted_path": f"{__args_prefix}.managed_pool_address",
            "value": MANAGED_POOL_ADDRESS,
        },
        {
            "dotted_path": f"{__args_prefix}.fear_and_greed_endpoint",
            "value": f"{MOCK_API_ADDRESS}:{MOCK_API_PORT}{MOCK_API_PATH}",
        },
    ]

    def test_run(self, nb_nodes: int) -> None:
        """Run the test."""
        self.prepare_and_launch(nb_nodes)
        self.health_check(
            max_retries=self.HEALTH_CHECK_MAX_RETRIES,
            sleep_interval=self.HEALTH_CHECK_SLEEP_INTERVAL,
        )
        self.check_aea_messages()
        self.terminate_agents(timeout=TERMINATION_TIMEOUT)
