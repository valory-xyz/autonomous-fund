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

from enum import Enum
from typing import Any, Dict

from packages.valory.skills.abstract_round_abci.base import BaseTxPayload


class TransactionType(Enum):
    """Enumeration of transaction types."""

    ALLOW_LIST_UPDATE = "allow_list_update"

    def __str__(self) -> str:
        """Get the string value of the transaction type."""
        return self.value


class AllowListUpdatePayload(BaseTxPayload):
    """Represent a transaction payload for the AllowListUpdateRound."""

    transaction_type = TransactionType.ALLOW_LIST_UPDATE

    def __init__(self, sender: str, allow_list_update: str, **kwargs: Any) -> None:
        """Initialize an AllowlistUpdate transaction payload."""
        super().__init__(sender, **kwargs)
        self._allow_list_update = allow_list_update

    @property
    def allow_list_update(self) -> str:
        """Get the Allowlist update transaction data."""
        return self._allow_list_update

    @property
    def data(self) -> Dict:
        """Get the data."""
        return dict(allow_list_update=self.allow_list_update)
