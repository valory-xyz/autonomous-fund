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
# pylint: disable=import-error

"""Tests for balancer/managed contract."""
import os
import tempfile
import time
from typing import Any, Dict, List, cast

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


class BaseManagedPoolContractContractTest(
    BaseContractTestCase, UseHardHatAutoFundBaseTest
):
    """ManagedPool contract tests"""

    contract_address = MANAGED_POOL
    path_to_contract = PACKAGE_DIR
    ledger_identifier = EthereumCrypto.identifier
    contract: ManagedPoolContract
    private_key_path: str
    USE_SAFE_CONTRACTS = False

    @classmethod
    def setup_class(cls) -> None:
        """Setup the test."""
        super().setup_class()
        _, pk = ACCOUNTS[0]
        fd, path = tempfile.mkstemp()
        with os.fdopen(fd, "w") as tmp:
            tmp.write(pk)
        cls.private_key_path = path

    @classmethod
    def finish_contract_deployment(cls) -> str:
        """Finish the contract deployment."""
        return cls.contract_address

    @classmethod
    def _deploy_contract(cls, contract, ledger_api, deployer_crypto, gas) -> Dict:  # type: ignore
        """Deploy contract."""
        return {}

    @property
    def sender(self) -> Any:
        """Returns the default tx sender."""
        sender = crypto_registry.make(
            EthereumCrypto.identifier, private_key_path=self.private_key_path
        )
        return sender

    def send_tx(self, raw_tx: Dict) -> None:
        """Send a tx with the default sender."""
        tx_signed = self.sender.sign_transaction(raw_tx)
        self.ledger_api.send_signed_transaction(tx_signed)

    def _update_weights_tx(
        self, start_datetime: int, end_datetime: int, end_weights: List[int]
    ) -> None:
        """Update the weights of the pool."""
        tokens = MANAGED_POOL_TOKENS
        raw_tx = self.contract.update_weights_gradually(
            ledger_api=self.ledger_api,
            sender_address=self.sender.address,
            contract_address=self.contract_address,
            start_datetime=start_datetime,
            tokens=tokens,
            end_datetime=end_datetime,
            end_weights=end_weights,
        )
        self.send_tx(raw_tx)

    def teardown_class(self) -> None:
        """Remove the tmp file."""
        os.remove(self.private_key_path)


@skip_docker_tests
class TestWeightUpdating(BaseManagedPoolContractContractTest):
    """ManagedPool gradual update params."""

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


@skip_docker_tests
class TestGradualUpdateParams(BaseManagedPoolContractContractTest):
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


@skip_docker_tests
class TestAllowlist(BaseManagedPoolContractContractTest):
    """ManagedPool allow-list related tests."""

    def test_run(self) -> None:
        """Test allow_list calls and txs."""
        contract = cast(ManagedPoolContract, self.contract)
        self._test_no_allowlist_on_init(contract)
        self._test_allowlist_enforced_after_update(contract)
        self._test_allowlist_gets_updated_by_adding(contract)
        self._test_allowlist_gets_updated_by_removing(contract)
        self._test_get_allowlist(contract)

    def _test_get_allowlist(self, contract: ManagedPoolContract) -> None:
        """Tests whether get allowlist returns correctly."""
        # the allowlist is empty in the beginning
        allowlist = contract.get_allowlist(self.ledger_api, self.contract_address).get(
            "allowlist"
        )
        assert allowlist is not None
        assert len(allowlist) == 0

        # a member gets added
        raw_tx = contract.add_allowed_address(
            self.ledger_api,
            self.contract_address,
            self.sender.address,
            self.sender.address,
        )
        self.send_tx(raw_tx)

        # the allowlist should contain it
        allowlist = contract.get_allowlist(self.ledger_api, self.contract_address).get(
            "allowlist"
        )
        assert allowlist is not None
        assert len(allowlist) == 1
        assert self.sender.address in allowlist

        # the member gets removed
        raw_tx = contract.remove_allowed_address(
            self.ledger_api,
            self.contract_address,
            self.sender.address,
            self.sender.address,
        )
        self.send_tx(raw_tx)

        # the allowlist should be empty
        allowlist = contract.get_allowlist(self.ledger_api, self.contract_address).get(
            "allowlist"
        )
        assert allowlist is not None
        assert len(allowlist) == 0

    def _test_allowlist_gets_updated_by_removing(
        self, contract: ManagedPoolContract
    ) -> None:
        """Check that the contract gets updated when a member gets removed."""
        # the member is in the allowlist before it gets removed
        is_address_in_allowlist = contract.is_address_in_allowlist(
            self.ledger_api, self.contract_address, self.sender.address
        ).get("is_address_in_allowlist")
        assert is_address_in_allowlist

        # the member gets removed
        raw_tx = contract.remove_allowed_address(
            self.ledger_api,
            self.contract_address,
            self.sender.address,
            self.sender.address,
        )
        self.send_tx(raw_tx)

        # the member should no longer be in the allowlist
        is_address_in_allowlist = contract.is_address_in_allowlist(
            self.ledger_api, self.contract_address, self.sender.address
        ).get("is_address_in_allowlist")
        assert not is_address_in_allowlist

    def _test_allowlist_gets_updated_by_adding(
        self, contract: ManagedPoolContract
    ) -> None:
        """Check that the contract gets updated when a member gets added."""
        # the member is not in the allowlist before it gets added
        is_address_in_allowlist = contract.is_address_in_allowlist(
            self.ledger_api, self.contract_address, self.sender.address
        ).get("is_address_in_allowlist")
        assert not is_address_in_allowlist

        # the member gets added
        raw_tx = contract.add_allowed_address(
            self.ledger_api,
            self.contract_address,
            self.sender.address,
            self.sender.address,
        )
        self.send_tx(raw_tx)

        # the member should be in the allowlist
        is_address_in_allowlist = contract.is_address_in_allowlist(
            self.ledger_api, self.contract_address, self.sender.address
        ).get("is_address_in_allowlist")
        assert is_address_in_allowlist

    def _test_allowlist_enforced_after_update(
        self, contract: ManagedPoolContract
    ) -> None:
        """Check the allowlist is enforced after an update."""
        # the allowlist should not be enforced before an update
        is_enforced = contract.get_must_allowlist_lps(
            self.ledger_api, self.contract_address
        ).get("is_enforced")
        assert not is_enforced

        # a tx to enforce the allowlist is made
        enforce_allowlist = True
        raw_tx = contract.set_must_allowlist_lps(
            self.ledger_api,
            self.contract_address,
            self.sender.address,
            enforce_allowlist,
        )
        self.send_tx(raw_tx)

        # the allowlist should be enforced before an update
        is_enforced = contract.get_must_allowlist_lps(
            self.ledger_api, self.contract_address
        ).get("is_enforced")
        assert is_enforced

    def _test_no_allowlist_on_init(self, contract: ManagedPoolContract) -> None:
        """The allowlist should not be enforced on pool init."""
        is_enforced = contract.get_must_allowlist_lps(
            self.ledger_api, self.contract_address
        ).get("is_enforced")
        assert not is_enforced
