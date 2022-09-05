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

"""This module contains the transaction payloads for the fear and greed oracle app."""

from enum import Enum
from typing import Any, Dict, Optional

from packages.valory.skills.abstract_round_abci.base import BaseTxPayload


class TransactionType(Enum):
    """Enumeration of transaction types."""

    OBSERVATION = "observation"
    ESTIMATION = "estimation"

    def __str__(self) -> str:
        """Get the string value of the transaction type."""
        return self.value


class ObservationRoundPayload(BaseTxPayload):
    """Represent a transaction payload of type 'observation'."""

    transaction_type = TransactionType.OBSERVATION

    def __init__(
        self, sender: str, observation_data: str, **kwargs: Any
    ) -> None:
        """Initialize an 'observation' transaction payload.

        :param sender: the sender (Ethereum) address
        :param observation_data: the observation data json encoded
        :param kwargs: the keyword arguments
        """
        super().__init__(sender, **kwargs)
        self._observation_data = observation_data

    @property
    def observation_data(self) -> str:
        """Get the observation data."""
        return self._observation_data

    @property
    def data(self) -> Dict:
        """Get the data."""
        return dict(observation_data=self.observation_data)


class EstimationRoundPayload(BaseTxPayload):
    """Represent a transaction payload of type 'randomness'."""

    transaction_type = TransactionType.ESTIMATION

    def __init__(
        self, sender: str, estimation_data: str, **kwargs: Any
    ) -> None:
        """Initialize an 'estimation' transaction payload.

        :param sender: the sender (Ethereum) address
        :param estimation_data: the estimation data json encoded
        :param kwargs: the keyword arguments
        """
        super().__init__(sender, **kwargs)
        self._estimation_data = estimation_data

    @property
    def estimation_data(self) -> str:
        """Get the estimation data."""
        return self._estimation_data

    @property
    def data(self) -> Dict:
        """Get the data."""
        return dict(estimation_data=self.estimation_data)
