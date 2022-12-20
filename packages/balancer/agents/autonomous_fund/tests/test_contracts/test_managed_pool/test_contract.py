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

"""Tests for balancer/managed contract."""
import os
import tempfile
import time
from typing import Dict, List, cast

from aea.crypto.registries import crypto_registry
from aea.test_tools.test_contract import BaseContractTestCase
from aea_ledger_ethereum import EthereumCrypto
from aea_test_autonomy.docker.base import skip_docker_tests

from packages.balancer.agents.autonomous_fund.tests.helpers.constants import (
    ACCOUNTS,
    INITIAL_POOL_WEIGHTS,
    MANAGED_POOL,
    MANAGED_POOL_TOKENS,
)
from packages.balancer.agents.autonomous_fund.tests.helpers.fixtures import (
    UseHardHatAutoFundBaseTest,
)
from packages.balancer.contracts.managed_pool import PACKAGE_DIR
from packages.balancer.contracts.managed_pool.contract import ManagedPoolContract


@skip_docker_tests
class TestManagedPoolContractContractTest(
    BaseContractTestCase, UseHardHatAutoFundBaseTest
):
    """ManagedPool contract tests"""

    contract_address = MANAGED_POOL
    path_to_contract = PACKAGE_DIR
    ledger_identifier = EthereumCrypto.identifier
    contract: ManagedPoolContract
    private_key_path: str
    USE_SAFE_CONTRACTS = False

    def setup_class(self) -> None:
        """Setup the test."""
        _, pk = ACCOUNTS[0]
        fd, path = tempfile.mkstemp()
        with os.fdopen(fd, "w") as tmp:
            tmp.write(pk)
        self.private_key_path = path

    @classmethod
    def finish_contract_deployment(cls) -> str:
        """Finish the contract deployment."""
        return cls.contract_address

    @classmethod
    def _deploy_contract(cls, contract, ledger_api, deployer_crypto, gas) -> Dict:  # type: ignore
        """Deploy contract."""
        return {}

    def _update_weights_tx(
        self, start_datetime: int, end_datetime: int, end_weights: List[int]
    ) -> None:
        """Update the weights of the pool."""
        sender = crypto_registry.make(
            EthereumCrypto.identifier, private_key_path=self.private_key_path
        )
        tokens = MANAGED_POOL_TOKENS
        tx_raw = self.contract.update_weights_gradually(
            ledger_api=self.ledger_api,
            sender_address=sender.address,
            contract_address=self.contract_address,
            start_datetime=start_datetime,
            tokens=tokens,
            end_datetime=end_datetime,
            end_weights=end_weights,
        )
        tx_signed = sender.sign_transaction(tx_raw)
        self.ledger_api.send_signed_transaction(tx_signed)

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

    def test_get_gradual_weight_update_params(self) -> None:
        """Test whether `get_gradual_weight_update_params` returns the expected params."""
        update_params = self.contract.get_gradual_weight_update_params(
            self.ledger_api,
            self.contract_address,
        )
        assert (
            update_params["start_time"] == update_params["end_time"]
        ), "Before an update is made, the start and end time of an update should match"
        assert (
            update_params["start_weights"]
            == update_params["end_weights"]
            == INITIAL_POOL_WEIGHTS
        )

    def teardown_class(self) -> None:
        """Remove the tmp file."""
        os.remove(self.private_key_path)


@skip_docker_tests
class TestGradualUpdateParams(TestManagedPoolContractContractTest):
    """ManagedPool gradual update params."""

    def test_get_normalized_weights(self) -> None:
        """Test whether `get_normalized_weights` returns the expected weights."""
        ONE_DAY = 86400
        start_datetime = int(time.time()) + ONE_DAY
        end_datetime = start_datetime + ONE_DAY
        end_weights = [80, 10, 10]
        self._update_weights_tx(start_datetime, end_datetime, end_weights)

        update_params = self.contract.get_gradual_weight_update_params(
            self.ledger_api,
            self.contract_address,
        )
        assert cast(int, update_params["start_time"]) == start_datetime
        assert cast(int, update_params["end_time"]) == end_datetime
        assert update_params["start_weights"] == INITIAL_POOL_WEIGHTS
        assert update_params["end_weights"] == end_weights
