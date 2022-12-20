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

"""This package contains round behaviours of LiquidityProvisionAbciApp."""

from typing import Generator, Set, Type, cast

from packages.valory.skills.abstract_round_abci.base import AbstractRound
from packages.valory.skills.abstract_round_abci.behaviours import (
    AbstractRoundBehaviour,
    BaseBehaviour,
)

from packages.balancer.skills.liquidity_provision_abci.models import Params
from packages.balancer.skills.liquidity_provision_abci.rounds import (
    SynchronizedData,
    LiquidityProvisionAbciApp,
    AllowListUpdateRound,
)
from packages.balancer.skills.liquidity_provision_abci.rounds import (
    AllowListUpdatePayload,
)


class LiquidityProvisionBaseBehaviour(BaseBehaviour):
    """Base behaviour for the common apps' skill."""

    @property
    def synchronized_data(self) -> SynchronizedData:
        """Return the synchronized data."""
        return cast(SynchronizedData, super().synchronized_data)

    @property
    def params(self) -> Params:
        """Return the params."""
        return cast(Params, super().params)


class AllowListUpdateBehaviour(LiquidityProvisionBaseBehaviour):
    """AllowListUpdateBehaviour"""

    matching_round: Type[AbstractRound] = AllowListUpdateRound

    # TODO: implement logic required to set payload content (e.g. synchronized_data)
    def async_act(self) -> Generator:
        """Do the act, supporting asynchronous execution."""

        with self.context.benchmark_tool.measure(self.behaviour_id).local():
            sender = self.context.agent_address
            payload = AllowListUpdatePayload(sender=sender, content=...)

        with self.context.benchmark_tool.measure(self.behaviour_id).consensus():
            yield from self.send_a2a_transaction(payload)
            yield from self.wait_until_round_end()

        self.set_done()


class LiquidityProvisionRoundBehaviour(AbstractRoundBehaviour):
    """LiquidityProvisionRoundBehaviour"""

    initial_behaviour_cls = AllowListUpdateBehaviour
    abci_app_cls = LiquidityProvisionAbciApp  # type: ignore
    behaviours: Set[Type[BaseBehaviour]] = [
        AllowListUpdateBehaviour
    ]
