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

"""This package contains payload tests for the FearAndGreedOracleAbciApp."""

from typing import Hashable, Type, Dict
from dataclasses import dataclass

import pytest

from packages.balancer.skills.fear_and_greed_oracle_abci.payloads import (
    TransactionType,
    EstimationRoundPayload,
    ObservationRoundPayload,
    OutlierDetectionRoundPayload,
)
from packages.valory.skills.abstract_round_abci.base import BaseTxPayload


@dataclass
class PayloadTestCase:
    """PayloadTestCase"""

    payload_cls: Type[BaseTxPayload]
    content: Dict
    transaction_type: TransactionType


@pytest.mark.parametrize("test_case", [
    PayloadTestCase(
        payload_cls=EstimationRoundPayload,
        content=dict(estimation_data="test"),
        transaction_type=TransactionType.ESTIMATION,
    ),
    PayloadTestCase(
        payload_cls=ObservationRoundPayload,
        content=dict(observation_data="test"),
        transaction_type=TransactionType.OBSERVATION,
    ),
    PayloadTestCase(
        payload_cls=OutlierDetectionRoundPayload,
        content=dict(outlier_detection_data="test"),
        transaction_type=TransactionType.OUTLIER_DETECTION,
    ),
])
def test_payloads(test_case: PayloadTestCase) -> None:
    """Tests for FearAndGreedOracleAbciApp payloads"""

    payload = test_case.payload_cls(sender="sender", **test_case.content,)
    assert payload.sender == "sender"
    assert getattr(payload, "data") == test_case.content
    assert payload.transaction_type == test_case.transaction_type
    assert payload.from_json(payload.json) == payload

