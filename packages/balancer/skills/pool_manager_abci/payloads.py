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


class BasePoolManagerPayload(BaseTxPayload, ABC):
    """Base payload for PoolManager."""

    def __init__(self, sender: str, content: Hashable, **kwargs: Any) -> None:
        """Initialize a transaction payload."""

        super().__init__(sender, **kwargs)
        setattr(self, f"_{self.transaction_type}", content)
        p = property(lambda s: getattr(self, f"_{self.transaction_type}"))
        setattr(self.__class__, f"{self.transaction_type}", p)

    @property
    def data(self) -> Dict[str, Hashable]:
        """Get the data."""
        return {str(self.transaction_type): getattr(self, str(self.transaction_type))}


class DecisionMakingPayload(BasePoolManagerPayload):
    """Represent a transaction payload for the DecisionMakingRound."""

    transaction_type = TransactionType.DECISION_MAKING



class UpdatePoolTxPayload(BasePoolManagerPayload):
    """Represent a transaction payload for the UpdatePoolTxRound."""

    transaction_type = TransactionType.UPDATE_POOL_TX

    def __init__(self, sender: str, update_pool_tx: str, **kwargs: Any) -> None:
        """Initialize an UpdatePoolTx transaction payload."""
        super().__init__(sender=sender, content=update_pool_tx, **kwargs)
