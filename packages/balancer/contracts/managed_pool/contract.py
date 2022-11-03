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

"""This class contains a wrapper for ManagedPool contract interface."""

import logging
from typing import Any, Dict, List, Optional

from aea.common import JSONLike
from aea.configurations.base import PublicId
from aea.contracts.base import Contract
from aea_ledger_ethereum import LedgerApi


PUBLIC_ID = PublicId.from_str("balancer/managed_pool:0.1.0")

_logger = logging.getLogger(
    f"aea.packages.{PUBLIC_ID.author}.contracts.{PUBLIC_ID.name}.contract"
)

SCALING_FACTOR = 10 ** 16


class ManagedPoolContract(Contract):
    """The Managed Pool contract interface."""

    contract_id = PUBLIC_ID

    @classmethod
    def get_raw_transaction(
        cls, ledger_api: LedgerApi, contract_address: str, **kwargs: Any
    ) -> Optional[JSONLike]:
        """Get the Safe transaction."""
        raise NotImplementedError

    @classmethod
    def get_raw_message(
        cls, ledger_api: LedgerApi, contract_address: str, **kwargs: Any
    ) -> Optional[bytes]:
        """Get raw message."""
        raise NotImplementedError

    @classmethod
    def get_state(
        cls, ledger_api: LedgerApi, contract_address: str, **kwargs: Any
    ) -> Optional[JSONLike]:
        """Get state."""
        raise NotImplementedError

    @classmethod
    def get_normalized_weights(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
    ) -> Dict[str, List[float]]:
        """
        Returns all scaled down weights, in the same order as the Pool's tokens.

        :return: the pool's weights
        """
        contract_instance = cls.get_instance(ledger_api, contract_address)
        current_weights = contract_instance.functions.getNormalizedWeights().call()
        scaled_weights = list(
            map(lambda weight: weight / SCALING_FACTOR, current_weights)
        )
        return dict(
            weights=scaled_weights,
        )
