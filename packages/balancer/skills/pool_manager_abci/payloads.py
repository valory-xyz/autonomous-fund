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

"""This module contains the transaction payloads of the PoolManagerAbciApp."""

from abc import ABC
from enum import Enum
from typing import Any, Dict, Hashable

from packages.valory.skills.abstract_round_abci.base import BaseTxPayload


class TransactionType(Enum):
    """Enumeration of transaction types."""

    DECISION_MAKING = "decision_making"
    UPDATE_POOL_TX = "update_pool_tx"

    def __str__(self) -> str:
        """Get the string value of the transaction type."""
        return self.value


class DecisionMakingPayload(BaseTxPayload):
    """Represent a transaction payload for the DecisionMakingRound."""

    transaction_type = TransactionType.DECISION_MAKING

    def __init__(self, sender: str, decision_making: str, **kwargs: Any) -> None:
        """Initialize an DecisionMakingPayload transaction payload."""
        super().__init__(sender, **kwargs)
        self._decision_making = decision_making

    @property
    def decision_making(self) -> str:
        """Get the decision-making data."""
        return self._decision_making

    @property
    def data(self) -> Dict:
        """Get the data."""
        return dict(decision_making=self.decision_making)


class UpdatePoolTxPayload(BaseTxPayload):
    """Represent a transaction payload for the UpdatePoolTxRound."""

    transaction_type = TransactionType.UPDATE_POOL_TX

    def __init__(self, sender: str, update_pool_tx: str, **kwargs: Any) -> None:
        """Initialize an UpdatePoolTx transaction payload."""
        super().__init__(sender, **kwargs)
        self._update_pool_tx = update_pool_tx

    @property
    def update_pool_tx(self) -> str:
        """Get the UpdatePool transaction data."""
        return self._update_pool_tx

    @property
    def data(self) -> Dict:
        """Get the data."""
        return dict(update_pool_tx=self.update_pool_tx)
