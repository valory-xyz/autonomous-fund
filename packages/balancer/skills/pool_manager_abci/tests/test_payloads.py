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

"""This package contains payload tests for the PoolManagerAbciApp."""

from dataclasses import dataclass
from typing import Dict, Type

import pytest

from packages.balancer.skills.pool_manager_abci.payloads import (
    DecisionMakingPayload,
    UpdatePoolTxPayload,
)
from packages.valory.skills.abstract_round_abci.base import BaseTxPayload


@dataclass
class PayloadTestCase:
    """PayloadTestCase"""

    payload_cls: Type[BaseTxPayload]
    content: Dict


@pytest.mark.parametrize(
    "test_case",
    [
        PayloadTestCase(
            payload_cls=DecisionMakingPayload,
            content=dict(decision_making="test"),
        ),
        PayloadTestCase(
            payload_cls=UpdatePoolTxPayload,
            content=dict(update_pool_tx="test"),
        ),
    ],
)
def test_payloads(test_case: PayloadTestCase) -> None:
    """Tests for PoolManagerAbciApp payloads"""

    payload = test_case.payload_cls(  # type: ignore
        sender="sender",
        **test_case.content,
    )
    assert payload.sender == "sender"
    assert getattr(payload, "data") == test_case.content  # type: ignore # noqa: B009
