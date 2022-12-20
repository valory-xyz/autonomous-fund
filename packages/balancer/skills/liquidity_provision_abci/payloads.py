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

"""This module contains the transaction payloads of the LiquidityProvisionAbciApp."""

from abc import ABC
from enum import Enum
from typing import Any, Dict, Hashable, Optional

from packages.valory.skills.abstract_round_abci.base import BaseTxPayload


class TransactionType(Enum):
    """Enumeration of transaction types."""

    # TODO: define transaction types: e.g. TX_HASH: "tx_hash"
    ALLOW_LIST_UPDATE = "allow_list_update"

    def __str__(self) -> str:
        """Get the string value of the transaction type."""
        return self.value


class BaseLiquidityProvisionPayload(BaseTxPayload, ABC):
    """Base payload for LiquidityProvisionAbciApp."""

    def __init__(self, sender: str, content: Hashable, **kwargs: Any) -> None:
        """Initialize a transaction payload."""

        super().__init__(sender, **kwargs)
        setattr(self, f"_{self.transaction_type}", content)
        p = property(lambda s: getattr(self, f"_{self.transaction_type}"))
        setattr(self.__class__, f"{self.transaction_type}", p)

    @property
    def data(self) -> Dict[str, Hashable]:
        """Get the data."""
        return dict(content=getattr(self, str(self.transaction_type)))


class AllowListUpdatePayload(BaseLiquidityProvisionPayload):
    """Represent a transaction payload for the AllowListUpdateRound."""

    transaction_type = TransactionType.ALLOW_LIST_UPDATE
