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
# pylint: disable=no-self-use, too-few-public-methods, protected-access
"""Test the models.py module of the PoolManager."""

from packages.balancer.skills.pool_manager_abci.models import Params, SharedState
from packages.valory.skills.abstract_round_abci.test_tools.base import DummyContext


class TestSharedState:
    """Test SharedState of PoolManager."""

    def test_initialization(self) -> None:
        """Test initialization."""
        SharedState(name="", skill_context=DummyContext())


class TestParams:
    """Test Params of PoolManager."""

    def test_sort(self) -> None:
        """Tests whether sort works as expected."""
        tokens = ["c", "b", "a"]
        weights = {0: [3, 2, 1], 1: [5, 6, 7]}

        actual_tokens, actual_weights = Params._sort(tokens, weights)
        expected_tokens = ["a", "b", "c"]
        expected_weights = {0: [1, 2, 3], 1: [7, 6, 5]}

        assert actual_tokens == expected_tokens
        assert actual_weights == expected_weights
