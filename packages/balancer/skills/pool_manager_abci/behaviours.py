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

"""This package contains round behaviours of PoolManagerAbciApp."""

from abc import abstractmethod
from typing import Generator, Set, Type, cast

from packages.valory.skills.abstract_round_abci.base import AbstractRound
from packages.valory.skills.abstract_round_abci.behaviours import (
    AbstractRoundBehaviour,
    BaseBehaviour,
)

from packages.balancer.skills.pool_manager_abci.models import Params
from packages.balancer.skills.pool_manager_abci.rounds import (
    SynchronizedData,
    PoolManagerAbciApp,
    UpdatePoolTxRound,
)


class PoolManagerBaseBehaviour(BaseBehaviour):
    """Base behaviour for the common apps' skill."""

    @property
    def synchronized_data(self) -> SynchronizedData:
        """Return the synchronized data."""
        return cast(SynchronizedData, super().synchronized_data)

    @property
    def params(self) -> Params:
        """Return the params."""
        return cast(Params, super().params)


class UpdatePoolTxBehaviour(PoolManagerBaseBehaviour):
    """UpdatePoolTxBehaviour"""

    # TODO: set the following class attributes
    state_id: str
    behaviour_id: str = "update_pool_tx"
    matching_round: Type[AbstractRound] = UpdatePoolTxRound

    @abstractmethod
    def async_act(self) -> Generator:
        """Do the act, supporting asynchronous execution."""


class PoolManagerRoundBehaviour(AbstractRoundBehaviour):
    """PoolManagerRoundBehaviour"""

    initial_behaviour_cls = UpdatePoolTxBehaviour
    abci_app_cls = PoolManagerAbciApp  # type: ignore
    behaviours: Set[Type[BaseBehaviour]] = [UpdatePoolTxBehaviour]
