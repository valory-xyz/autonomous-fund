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
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Hashable, Optional, Type
from dataclasses import dataclass
from unittest import mock

import pytest

from packages.balancer.contracts.managed_pool_controller.contract import ManagedPoolControllerContract
from packages.balancer.contracts.managed_pool_controller.tests.helpers.constants import (
    MANAGED_POOL_CONTROLLER as MANAGED_POOL_CONTROLLER_ADDRESS,
    CONFIGURED_SAFE_INSTANCE as SAFE_CONTRACT_ADDRESS,
)
from packages.valory.contracts.gnosis_safe.contract import GnosisSafeContract
from packages.valory.protocols.contract_api import ContractApiMessage
from packages.valory.protocols.contract_api.custom_types import State
from packages.valory.skills.abstract_round_abci.base import AbciAppDB, AbciApp
from packages.valory.skills.abstract_round_abci.behaviours import (
    AbstractRoundBehaviour,
    BaseBehaviour,
    make_degenerate_behaviour,
)
from packages.balancer.skills.pool_manager_abci.behaviours import (
    PoolManagerBaseBehaviour,
    DecisionMakingBehaviour,
    UpdatePoolTxBehaviour,
)
from packages.balancer.skills.pool_manager_abci.rounds import (
    SynchronizedData,
    Event,
    FinishedTxPreparationRound,
)

from packages.valory.skills.abstract_round_abci.test_tools.base import (
    FSMBehaviourBaseCase,
)


@dataclass
class BehaviourTestCase:
    """BehaviourTestCase"""

    name: str
    initial_data: Dict[str, Hashable]
    event: Event
    next_behaviour_class: Optional[Type[PoolManagerBaseBehaviour]] = None


class BasePoolManagerTest(FSMBehaviourBaseCase):
    """Base test case."""

    path_to_skill = Path(__file__).parent.parent

    behaviour: PoolManagerBaseBehaviour
    behaviour_class: Type[PoolManagerBaseBehaviour]
    next_behaviour_class: Type[PoolManagerBaseBehaviour]
    synchronized_data: SynchronizedData
    done_event = Event.DONE

    def fast_forward(self, data: Optional[Dict[str, Any]] = None) -> None:
        """Fast-forward on initialization"""

        data = data if data is not None else {}
        self.fast_forward_to_behaviour(
            self.behaviour,  # type: ignore
            self.behaviour_class.behaviour_id,
            SynchronizedData(AbciAppDB(setup_data=AbciAppDB.data_to_lists(data))),
        )
        assert (
                self.behaviour.current_behaviour.behaviour_id  # type: ignore
                == self.behaviour_class.behaviour_id
        )

    def complete(
            self, event: Event, next_behaviour_class: Optional[Type[BaseBehaviour]] = None
    ) -> None:
        """Complete test"""
        if next_behaviour_class is None:
            # use the class value as fallback
            next_behaviour_class = self.next_behaviour_class

        self.behaviour.act_wrapper()
        self.mock_a2a_transaction()
        self._test_done_flag_set()
        self.end_round(done_event=event)
        assert (
                self.behaviour.current_behaviour.behaviour_id  # type: ignore
                == next_behaviour_class.behaviour_id
        )


class TestDecisionMakingBehaviour(BasePoolManagerTest):
    """Tests DecisionMakingBehaviour"""

    # TODO: set next_behaviour_class
    behaviour_class: Type[BaseBehaviour] = DecisionMakingBehaviour
    next_behaviour_class: Type[BaseBehaviour] = ...

    # TODO: provide test cases
    @pytest.mark.parametrize("test_case, kwargs", [])
    def test_run(self, test_case: BehaviourTestCase, **kwargs: Any) -> None:
        """Run tests."""

        self.fast_forward(test_case.initial_data)
        # TODO: mock the necessary calls
        # self.mock_ ...
        self.complete(test_case.event)


class TestUpdatePoolTxBehaviour(BasePoolManagerTest):
    """Tests UpdatePoolTxBehaviour"""

    behaviour_class: Type[BaseBehaviour] = UpdatePoolTxBehaviour
    next_behaviour_class: Type[BaseBehaviour] = FinishedTxPreparationRound

    _estimates = {
        "value_estimates": [
            25.0,
            26.0,
        ],
        "timestamp_estimates": [
            1662940800.0,
            1662854400.0,
        ],
    }
    _pool_controller_error = (
        f"Couldn't get tx data for ManagedPoolControllerContract.update_weights_gradually. "
        f"Expected response performative {ContractApiMessage.Performative.STATE.value}, "
        f"received {ContractApiMessage.Performative.ERROR.value}."
    )
    _safe_contract_error = (
        f"Couldn't get safe hash. "
        f"Expected response performative {ContractApiMessage.Performative.STATE.value}, "
        f"received {ContractApiMessage.Performative.ERROR.value}."
    )

    def _mock_pool_controller_contract_request(
            self,
            response_body: Dict,
            response_performative: ContractApiMessage.Performative,
    ) -> None:
        """Mock the ManagedPoolControllerContract."""
        self.mock_contract_api_request(
            contract_id=str(ManagedPoolControllerContract.contract_id),
            request_kwargs=dict(
                performative=ContractApiMessage.Performative.GET_STATE,
                contract_address=MANAGED_POOL_CONTROLLER_ADDRESS,
            ),
            response_kwargs=dict(
                performative=response_performative,
                state=State(
                    ledger_id="ethereum",
                    body=response_body,
                ),
            ),
        )

    def _mock_safe_contract_request(
            self,
            response_body: Dict,
            response_performative: ContractApiMessage.Performative,
    ) -> None:
        """Mock the ManagedPoolControllerContract."""
        self.mock_contract_api_request(
            contract_id=str(GnosisSafeContract.contract_id),
            request_kwargs=dict(
                performative=ContractApiMessage.Performative.GET_STATE,
                contract_address=SAFE_CONTRACT_ADDRESS,
            ),
            response_kwargs=dict(
                performative=response_performative,
                state=State(
                    ledger_id="ethereum",
                    body=response_body,
                ),
            ),
        )

    @pytest.mark.parametrize(
        "test_case, kwargs",
        [
            (
                    BehaviourTestCase(
                        name='happy path',
                        initial_data=dict(
                            most_voted_estimates=_estimates,
                            safe_contract_address=SAFE_CONTRACT_ADDRESS,
                        ),
                        event=Event.DONE,
                        next_behaviour_class=make_degenerate_behaviour(  # type: ignore
                            FinishedTxPreparationRound.round_id
                        ),  # noqa
                    ),
                    {
                        "mock_response_data": dict(
                            data="0x" + "0" * 64,
                            tx_hash="0x" + "0" * 64,
                        ),
                        "mock_response_performative": ContractApiMessage.Performative.STATE,
                    }
            )
        ],
    )
    def test_happy_path(self, test_case: BehaviourTestCase, kwargs: Any) -> None:
        """Test the happy path."""

        with mock.patch(
                'packages.valory.skills.abstract_round_abci.base.AbciApp.last_timestamp',
                return_value=datetime.now(),
        ):
            self.fast_forward(test_case.initial_data)
            self.behaviour.act_wrapper()

            self._mock_pool_controller_contract_request(
                response_body=kwargs.get("mock_response_data"),
                response_performative=kwargs.get("mock_response_performative"),
            )
            self._mock_safe_contract_request(
                response_body=kwargs.get("mock_response_data"),
                response_performative=kwargs.get("mock_response_performative"),
            )

            self.complete(test_case.event, test_case.next_behaviour_class)

    @pytest.mark.parametrize(
        "test_case, kwargs",
        [
            (
                    BehaviourTestCase(
                        name='contract error',
                        initial_data=dict(
                            most_voted_estimates=_estimates,
                            safe_contract_address=SAFE_CONTRACT_ADDRESS,
                        ),
                        event=Event.NO_ACTION,
                        next_behaviour_class=UpdatePoolTxBehaviour,
                    ),
                    {
                        "mock_response_data": dict(),
                        "mock_failing_response_performative": ContractApiMessage.Performative.ERROR,
                        "expected_error": _pool_controller_error,
                    }

            )

        ],
    )
    def test_managed_pool_controller_error(self, test_case: BehaviourTestCase, kwargs: Any) -> None:
        """Test Managed Pool Controller Error."""

        with mock.patch(
                'packages.valory.skills.abstract_round_abci.base.AbciApp.last_timestamp',
                return_value=datetime.now(),
        ), mock.patch.object(
            self.behaviour.context.logger, "log"
        ) as mock_logger:
            self.fast_forward(test_case.initial_data)
            self.behaviour.act_wrapper()

            self._mock_pool_controller_contract_request(
                response_body=kwargs.get("mock_response_data"),
                response_performative=kwargs.get("mock_failing_response_performative"),
            )

            mock_logger.assert_any_call(
                logging.ERROR,
                kwargs.get("expected_error"),
            )

            self.complete(test_case.event, test_case.next_behaviour_class)

    @pytest.mark.parametrize(
        "test_case, kwargs",
        [
            (
                    BehaviourTestCase(
                        name='contract error',
                        initial_data=dict(
                            most_voted_estimates=_estimates,
                            safe_contract_address=SAFE_CONTRACT_ADDRESS,
                        ),
                        event=Event.NO_ACTION,
                        next_behaviour_class=UpdatePoolTxBehaviour,
                    ),
                    {
                        "mock_response_data": dict(
                            data="0x" + "0" * 64,
                        ),
                        "mock_response_performative": ContractApiMessage.Performative.STATE,
                        "mock_failing_response_performative": ContractApiMessage.Performative.ERROR,
                        "expected_error": _safe_contract_error,
                    }

            )

        ],
    )
    def test_safe_contract_error(self, test_case: BehaviourTestCase, kwargs: Any) -> None:
        """Test Safe Contract Error."""

        with mock.patch(
                'packages.valory.skills.abstract_round_abci.base.AbciApp.last_timestamp',
                return_value=datetime.now(),
        ), mock.patch.object(
            self.behaviour.context.logger, "log"
        ) as mock_logger:
            self.fast_forward(test_case.initial_data)
            self.behaviour.act_wrapper()

            self._mock_pool_controller_contract_request(
                response_body=kwargs.get("mock_response_data"),
                response_performative=kwargs.get("mock_response_performative"),
            )
            self._mock_safe_contract_request(
                response_body=kwargs.get("mock_response_data"),
                response_performative=kwargs.get("mock_failing_response_performative"),
            )

            mock_logger.assert_any_call(
                logging.ERROR,
                kwargs.get("expected_error"),
            )

            self.complete(test_case.event, test_case.next_behaviour_class)