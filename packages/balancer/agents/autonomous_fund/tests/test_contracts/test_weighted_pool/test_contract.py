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
# pylint: disable=import-error

"""Tests for balancer/weighted_pool contract."""
from typing import Dict

from aea.test_tools.test_contract import BaseContractTestCase
from aea_ledger_ethereum import EthereumCrypto
from aea_test_autonomy.docker.base import skip_docker_tests

from packages.balancer.agents.autonomous_fund.tests.helpers.constants import (
    INITIAL_POOL_WEIGHTS,
    WEIGHTED_POOL,
)
from packages.balancer.agents.autonomous_fund.tests.helpers.fixtures import (
    UseHardHatAutoFundBaseTest,
)
from packages.balancer.contracts.weighted_pool import PACKAGE_DIR
from packages.balancer.contracts.weighted_pool.contract import WeightedPoolContract


@skip_docker_tests
class TestWeightedPoolContractContractTest(
    BaseContractTestCase, UseHardHatAutoFundBaseTest
):
    """WeightedPool contract tests"""

    contract_address = WEIGHTED_POOL
    path_to_contract = PACKAGE_DIR
    ledger_identifier = EthereumCrypto.identifier
    contract: WeightedPoolContract
    private_key_path: str
    USE_SAFE_CONTRACTS = False

    @classmethod
    def finish_contract_deployment(cls) -> str:
        """Finish the contract deployment."""
        return cls.contract_address

    @classmethod
    def _deploy_contract(cls, contract, ledger_api, deployer_crypto, gas) -> Dict:  # type: ignore
        """Deploy contract."""
        return {}

    def test_get_normalized_weights(self) -> None:
        """Test whether `get_normalized_weights` returns the expected weights."""
        tolerance = 0.1  # we allow for 0.1% difference between expected and actual
        expected_weights = INITIAL_POOL_WEIGHTS
        num_expected_weights = len(expected_weights)
        actual_weights = self.contract.get_normalized_weights(
            ledger_api=self.ledger_api,
            contract_address=self.contract_address,
        ).get("weights", [])

        assert num_expected_weights == len(
            actual_weights
        ), "an unexpected number of weights was send"

        # check that actual weights are within the tolerance interval defined above
        assert all(
            abs(expected_weights[i] - actual_weights[i]) < tolerance
            for i in range(num_expected_weights)
        ), "weights are not as expected"
