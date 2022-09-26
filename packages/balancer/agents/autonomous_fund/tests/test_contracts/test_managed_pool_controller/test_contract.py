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

"""Tests for balancer/managed_pool_controller contract."""
import os
import tempfile
import time
from typing import Dict

from aea.crypto.registries import crypto_registry
from aea.test_tools.test_contract import BaseContractTestCase
from aea_ledger_ethereum import EthereumCrypto
from aea_test_autonomy.docker.base import skip_docker_tests

from packages.balancer.agents.autonomous_fund.tests.helpers.constants import (
    ACCOUNTS,
    MANAGED_POOL_CONTROLLER,
)
from packages.balancer.agents.autonomous_fund.tests.helpers.fixtures import (
    UseHardHatAutoFundBaseTest,
)
from packages.balancer.contracts.managed_pool_controller import PACKAGE_DIR
from packages.balancer.contracts.managed_pool_controller.contract import (
    ManagedPoolControllerContract,
)


@skip_docker_tests
class TestManagedPoolControllerContractTest(
    BaseContractTestCase, UseHardHatAutoFundBaseTest
):
    """Test Managed Pool Controller contract tests"""

    contract_address = MANAGED_POOL_CONTROLLER
    path_to_contract = PACKAGE_DIR
    ledger_identifier = EthereumCrypto.identifier
    contract: ManagedPoolControllerContract
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

    def test_update_weights_gradually(self) -> None:
        """Test the data returned by update weights gradually."""
        sender = crypto_registry.make(
            EthereumCrypto.identifier, private_key_path=self.private_key_path
        )
        start_datetime = int(time.time())
        ONE_DAY = 86400
        end_datetime = start_datetime + ONE_DAY
        end_weights = [80, 10, 10]

        tx_raw = self.contract.update_weights_gradually(
            ledger_api=self.ledger_api,
            sender_address=sender.address,
            contract_address=self.contract_address,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            end_weights=end_weights,
        )
        tx_signed = sender.sign_transaction(tx_raw)
        tx_hash = self.ledger_api.send_signed_transaction(tx_signed)
        assert tx_hash is not None, "Tx hash not none"

        tx = self.ledger_api.get_transaction(tx_hash)
        assert tx is not None, "tx was None"

        tx_receipt = self.ledger_api.get_transaction_receipt(tx_hash)
        assert tx_receipt is not None, "tx receipt was None"
        assert tx_receipt["status"] == 1, "the tx failed"

    def teardown(self) -> None:
        """Remove the tmp file."""
        os.remove(self.private_key_path)
