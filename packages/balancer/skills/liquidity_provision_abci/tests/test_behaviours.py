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

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union, cast

import pytest
from _pytest.logging import LogCaptureFixture
from aea.common import JSONLike

from packages.balancer.contracts.managed_pool.contract import ManagedPoolContract
from packages.balancer.skills.liquidity_provision_abci.behaviours import (
    AllowListUpdateBehaviour,
    LiquidityProvisionBaseBehaviour,
    LiquidityProvisionRoundBehaviour,
)
from packages.balancer.skills.liquidity_provision_abci.rounds import (
    Event,
    FinishedAllowlistTxPreparationRound,
    SynchronizedData,
)
from packages.valory.contracts.gnosis_safe.contract import GnosisSafeContract
from packages.valory.contracts.multisend.contract import MultiSendContract
from packages.valory.protocols.contract_api import ContractApiMessage
from packages.valory.protocols.contract_api.custom_types import RawTransaction, State
from packages.valory.skills.abstract_round_abci.base import AbciAppDB
from packages.valory.skills.abstract_round_abci.behaviours import (
    BaseBehaviour,
    make_degenerate_behaviour,
)
from packages.valory.skills.abstract_round_abci.test_tools.base import (
    FSMBehaviourBaseCase,
)


@dataclass
class BehaviourTestCase:
    """BehaviourTestCase"""

    name: str
    initial_data: Dict[str, Any]
    ok_reqs: List[Tuple[Callable, Dict]]
    err_reqs: List[Tuple[Callable, Dict]]
    expected_logs: List[str]
    expected_event: Event = Event.DONE
    allowed_lp_addresses: Union[List[str], Tuple[str]] = ()  # type: ignore


SAFE_CONTRACT_ADDRESS = "0x5564550A54EcD43bA8f7c666fff1C4762889A572"
MANAGED_POOL_ADDRESS = "0xb5f3FC2579b134D836271AC872de2DA83Fe6e6a1"
MULTISEND_ADDRESS = "0xA238CBeb142c10Ef7Ad8442C6D1f9E89e07e7761"


class BaseLiquidityProvisionTest(FSMBehaviourBaseCase):
    """Base test case."""

    path_to_skill = Path(__file__).parent.parent

    behaviour: LiquidityProvisionRoundBehaviour  # type: ignore
    behaviour_class: Type[LiquidityProvisionBaseBehaviour]
    next_behaviour_class: Type[LiquidityProvisionBaseBehaviour]
    synchronized_data: SynchronizedData
    done_event = Event.DONE

    @property
    def current_behaviour_id(self) -> str:
        """Current RoundBehaviour's behaviour id"""

        return self.behaviour.current_behaviour.auto_behaviour_id()  # type: ignore

    def fast_forward(self, data: Optional[Dict[str, Any]] = None) -> None:
        """Fast-forward on initialization"""

        data = data if data is not None else {}
        self.fast_forward_to_behaviour(
            self.behaviour,
            self.behaviour_class.auto_behaviour_id(),
            SynchronizedData(AbciAppDB(setup_data=AbciAppDB.data_to_lists(data))),
        )
        assert self.current_behaviour_id == self.behaviour_class.auto_behaviour_id()

    def complete(self, event: Event) -> None:
        """Complete test"""

        self.behaviour.act_wrapper()
        self.mock_a2a_transaction()
        self._test_done_flag_set()
        self.end_round(done_event=event)
        assert (
            self.current_behaviour_id == self.next_behaviour_class.auto_behaviour_id()
        )


class TestAllowListUpdateBehaviour(BaseLiquidityProvisionTest):
    """Tests AllowListUpdateBehaviour"""

    behaviour_class: Type[BaseBehaviour] = AllowListUpdateBehaviour  # type: ignore
    next_behaviour_class: Type[BaseBehaviour] = make_degenerate_behaviour(  # type: ignore
        FinishedAllowlistTxPreparationRound
    )

    _MOCK_TX_RESPONSE = b"0xIrrelevantForTests".hex()
    _MOCK_TX_HASH = "0x" + "0" * 64
    _INITIAL_DATA: Dict[str, Any] = dict(
        safe_contract_address=SAFE_CONTRACT_ADDRESS,
    )
    _MOCK_MEMBERS = ["0x0", "0x1", "0x2", "0x3"]

    # possible logs from the behaviour
    _NO_UPDATES_REQUIRED = "No updates to the allowlist are required."
    _ALLOWLIST_ENFORCING_CHANGE = (
        "A tx to change the allowlist enforcing should be made."
    )
    _MEMBER_ADDITION = "Member with address {} should be added to the allowlist."
    _MEMBER_REMOVAL = "Member with address {} should be removed from the allowlist."

    _STATE_ERR_LOG = (
        f"Expected response performative {ContractApiMessage.Performative.STATE.value}, "  # type: ignore
        f"received {ContractApiMessage.Performative.ERROR}."
    )
    _RAW_TRANSACTION_ERR = (
        f"Expected response performative {ContractApiMessage.Performative.RAW_TRANSACTION.value}, "  # type: ignore
        f"received {ContractApiMessage.Performative.ERROR}."
    )
    _GET_ALLOWLIST_ERR_LOG = (
        f"Couldn't get allowlist from IManagedPool.get_allowlist. " f"{_STATE_ERR_LOG}"
    )
    _IS_ALLOWLIST_ENFORCED_LOG = (
        f"Couldn't check whether the pool is configured to enforce an allowlist via IManagedPool.get_must_allowlist_lps. "
        f"{_STATE_ERR_LOG}"
    )
    _SET_ALLOWLIST_ERR_LOG = (
        f"Couldn't get tx data for IManagedPool.setMustAllowlistLPs(). "
        f"{_STATE_ERR_LOG}"
    )
    _ADD_MEMBER_ERR_LOG = (
        f"Couldn't get tx data for IManagedPool.addAllowedAddress(). "
        f"{_STATE_ERR_LOG}"
    )
    _REMOVE_MEMBER_ERR_LOG = (
        f"Couldn't get tx data for IManagedPool.removeAllowedAddress(). "
        f"{_STATE_ERR_LOG}"
    )
    _MULTISEND_ERR_LOG = "Couldn't compile the multisend tx. " f"{_RAW_TRANSACTION_ERR}"
    _SAFE_HASH_ERR_LOG = f"Couldn't get safe hash. " f"{_STATE_ERR_LOG}"

    def _mock_get_must_allowlist_lps(
        self,
        error: bool = False,
        is_enforced: bool = True,
    ) -> None:
        """Mock the response of IManagedPool.get_must_allowlist_lps"""
        if not error:
            response_performative = ContractApiMessage.Performative.STATE
            response_body = dict(is_enforced=is_enforced)
        else:
            response_body = dict()
            response_performative = ContractApiMessage.Performative.ERROR
        self.mock_contract_api_request(
            contract_id=str(ManagedPoolContract.contract_id),
            request_kwargs=dict(
                performative=ContractApiMessage.Performative.GET_STATE,
                contract_address=MANAGED_POOL_ADDRESS,
            ),
            response_kwargs=dict(
                performative=response_performative,
                state=State(
                    ledger_id="ethereum",
                    body=cast(JSONLike, response_body),
                ),
            ),
        )

    def _mock_get_current_allowlist(
        self,
        error: bool = False,
        allowlist: Union[Tuple[str], List[str]] = (),  # type: ignore
    ) -> None:
        """Mock the response of IManagedPool.get_allowlist"""
        if not error:
            response_performative = ContractApiMessage.Performative.STATE
            response_body = dict(allowlist=list(allowlist))
        else:
            response_body = dict()
            response_performative = ContractApiMessage.Performative.ERROR
        self.mock_contract_api_request(
            contract_id=str(ManagedPoolContract.contract_id),
            request_kwargs=dict(
                performative=ContractApiMessage.Performative.GET_STATE,
                contract_address=MANAGED_POOL_ADDRESS,
            ),
            response_kwargs=dict(
                performative=response_performative,
                state=State(
                    ledger_id="ethereum",
                    body=cast(JSONLike, response_body),
                ),
            ),
        )

    def _mock_set_must_allowlist_lps_tx(
        self,
        error: bool = False,
    ) -> None:
        """Mock the response of IManagedPool.setMustAllowlistLPs()"""
        if not error:
            response_performative = ContractApiMessage.Performative.STATE
            response_body = dict(data=self._MOCK_TX_RESPONSE)
        else:
            response_body = dict()
            response_performative = ContractApiMessage.Performative.ERROR
        self.mock_contract_api_request(
            contract_id=str(ManagedPoolContract.contract_id),
            request_kwargs=dict(
                performative=ContractApiMessage.Performative.GET_STATE,
                contract_address=MANAGED_POOL_ADDRESS,
            ),
            response_kwargs=dict(
                performative=response_performative,
                state=State(
                    ledger_id="ethereum",
                    body=cast(JSONLike, response_body),
                ),
            ),
        )

    def _mock_get_add_allowed_address_tx(
        self,
        error: bool = False,
    ) -> None:
        """Mock the response of IManagedPool.addAllowedAddress()"""
        if not error:
            response_performative = ContractApiMessage.Performative.STATE
            response_body = dict(data=self._MOCK_TX_RESPONSE)
        else:
            response_body = dict()
            response_performative = ContractApiMessage.Performative.ERROR
        self.mock_contract_api_request(
            contract_id=str(ManagedPoolContract.contract_id),
            request_kwargs=dict(
                performative=ContractApiMessage.Performative.GET_STATE,
                contract_address=MANAGED_POOL_ADDRESS,
            ),
            response_kwargs=dict(
                performative=response_performative,
                state=State(
                    ledger_id="ethereum",
                    body=cast(JSONLike, response_body),
                ),
            ),
        )

    def _mock_get_remove_allowed_address_tx(
        self,
        error: bool = False,
    ) -> None:
        """Mock the response of IManagedPool.removeAllowedAddress()"""
        if not error:
            response_performative = ContractApiMessage.Performative.STATE
            response_body = dict(data=self._MOCK_TX_RESPONSE)
        else:
            response_body = dict()
            response_performative = ContractApiMessage.Performative.ERROR
        self.mock_contract_api_request(
            contract_id=str(ManagedPoolContract.contract_id),
            request_kwargs=dict(
                performative=ContractApiMessage.Performative.GET_STATE,
                contract_address=MANAGED_POOL_ADDRESS,
            ),
            response_kwargs=dict(
                performative=response_performative,
                state=State(
                    ledger_id="ethereum",
                    body=cast(JSONLike, response_body),
                ),
            ),
        )

    def _mock_get_raw_safe_transaction_hash(
        self,
        error: bool = False,
    ) -> None:
        """Mock the response of GnosisSafeContract.get_raw_safe_transaction_hash()"""
        if not error:
            response_performative = ContractApiMessage.Performative.STATE
            response_body = dict(tx_hash=self._MOCK_TX_HASH)
        else:
            response_body = dict()
            response_performative = ContractApiMessage.Performative.ERROR
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
                    body=cast(JSONLike, response_body),
                ),
            ),
        )

    def _mock_get_multisend_tx(
        self,
        error: bool = False,
    ) -> None:
        """Mock the response of GnosisSafeContract.get_tx_data()"""
        if not error:
            response_performative = ContractApiMessage.Performative.RAW_TRANSACTION
            response_body = dict(data=self._MOCK_TX_RESPONSE)
        else:
            response_body = dict()
            response_performative = ContractApiMessage.Performative.ERROR
        self.mock_contract_api_request(
            contract_id=str(MultiSendContract.contract_id),
            request_kwargs=dict(
                performative=ContractApiMessage.Performative.GET_RAW_TRANSACTION,
                contract_address=MULTISEND_ADDRESS,
            ),
            response_kwargs=dict(
                performative=response_performative,
                raw_transaction=RawTransaction(
                    ledger_id="ethereum",
                    body=cast(JSONLike, response_body),
                ),
            ),
        )

    @pytest.mark.parametrize(
        "test_case",
        [
            BehaviourTestCase(
                name="Agent config matches the pool config, no changes need to be made.",
                initial_data=_INITIAL_DATA,
                ok_reqs=[
                    (_mock_get_must_allowlist_lps, {}),
                    (_mock_get_current_allowlist, {}),
                ],
                err_reqs=[],
                expected_logs=[_NO_UPDATES_REQUIRED],
            ),
            BehaviourTestCase(
                name="Allowlist enforcing needs to be changed.",
                initial_data=_INITIAL_DATA,
                ok_reqs=[
                    (_mock_get_must_allowlist_lps, {"is_enforced": False}),
                    (_mock_get_current_allowlist, {}),
                    (_mock_set_must_allowlist_lps_tx, {}),
                    (_mock_get_multisend_tx, {}),
                    (_mock_get_raw_safe_transaction_hash, {}),
                ],
                err_reqs=[],
                expected_logs=[_ALLOWLIST_ENFORCING_CHANGE],
            ),
            BehaviourTestCase(
                name="Allowlist enforcing needs to be changed, and one member needs to be removed.",
                initial_data=_INITIAL_DATA,
                ok_reqs=[
                    (_mock_get_must_allowlist_lps, {"is_enforced": False}),
                    (_mock_get_current_allowlist, {"allowlist": _MOCK_MEMBERS[:1]}),
                    (_mock_set_must_allowlist_lps_tx, {}),
                    (_mock_get_remove_allowed_address_tx, {}),
                    (_mock_get_multisend_tx, {}),
                    (_mock_get_raw_safe_transaction_hash, {}),
                ],
                err_reqs=[],
                expected_logs=[
                    _ALLOWLIST_ENFORCING_CHANGE,
                    _MEMBER_REMOVAL.format(_MOCK_MEMBERS[0]),
                ],
            ),
            BehaviourTestCase(
                name="Allowlist enforcing needs to be changed, and two members needs to be removed.",
                initial_data=_INITIAL_DATA,
                ok_reqs=[
                    (_mock_get_must_allowlist_lps, {"is_enforced": False}),
                    (_mock_get_current_allowlist, {"allowlist": _MOCK_MEMBERS[:2]}),
                    (_mock_set_must_allowlist_lps_tx, {}),
                    (_mock_get_remove_allowed_address_tx, {}),
                    (_mock_get_remove_allowed_address_tx, {}),
                    (_mock_get_multisend_tx, {}),
                    (_mock_get_raw_safe_transaction_hash, {}),
                ],
                err_reqs=[],
                expected_logs=[
                    _ALLOWLIST_ENFORCING_CHANGE,
                    _MEMBER_REMOVAL.format(_MOCK_MEMBERS[0]),
                    _MEMBER_REMOVAL.format(_MOCK_MEMBERS[1]),
                ],
            ),
            BehaviourTestCase(
                name="Two members needs to be removed.",
                initial_data=_INITIAL_DATA,
                ok_reqs=[
                    (_mock_get_must_allowlist_lps, {}),
                    (_mock_get_current_allowlist, {"allowlist": _MOCK_MEMBERS[:2]}),
                    (_mock_get_remove_allowed_address_tx, {}),
                    (_mock_get_remove_allowed_address_tx, {}),
                    (_mock_get_multisend_tx, {}),
                    (_mock_get_raw_safe_transaction_hash, {}),
                ],
                err_reqs=[],
                expected_logs=[
                    _MEMBER_REMOVAL.format(_MOCK_MEMBERS[0]),
                    _MEMBER_REMOVAL.format(_MOCK_MEMBERS[1]),
                ],
            ),
            BehaviourTestCase(
                name="Two members needs to be added.",
                initial_data=_INITIAL_DATA,
                ok_reqs=[
                    (_mock_get_must_allowlist_lps, {}),
                    (_mock_get_current_allowlist, {}),
                    (_mock_get_add_allowed_address_tx, {}),
                    (_mock_get_add_allowed_address_tx, {}),
                    (_mock_get_multisend_tx, {}),
                    (_mock_get_raw_safe_transaction_hash, {}),
                ],
                err_reqs=[],
                expected_logs=[
                    _MEMBER_ADDITION.format(_MOCK_MEMBERS[0]),
                    _MEMBER_ADDITION.format(_MOCK_MEMBERS[1]),
                ],
                allowed_lp_addresses=_MOCK_MEMBERS[:2],
            ),
            BehaviourTestCase(
                name="Two members needs to be added, one to be removed.",
                initial_data=_INITIAL_DATA,
                ok_reqs=[
                    (_mock_get_must_allowlist_lps, {}),
                    (_mock_get_current_allowlist, {"allowlist": _MOCK_MEMBERS[2:3]}),
                    (_mock_get_remove_allowed_address_tx, {}),
                    (_mock_get_add_allowed_address_tx, {}),
                    (_mock_get_add_allowed_address_tx, {}),
                    (_mock_get_multisend_tx, {}),
                    (_mock_get_raw_safe_transaction_hash, {}),
                ],
                err_reqs=[],
                expected_logs=[
                    _MEMBER_REMOVAL.format(_MOCK_MEMBERS[2]),
                    _MEMBER_ADDITION.format(_MOCK_MEMBERS[0]),
                    _MEMBER_ADDITION.format(_MOCK_MEMBERS[1]),
                ],
                allowed_lp_addresses=_MOCK_MEMBERS[:2],
            ),
            BehaviourTestCase(
                name="Allowlist enforcing check fails.",
                initial_data=_INITIAL_DATA,
                ok_reqs=[],
                err_reqs=[
                    (_mock_get_must_allowlist_lps, {}),
                ],
                expected_logs=[_IS_ALLOWLIST_ENFORCED_LOG],
            ),
            BehaviourTestCase(
                name="Getting allowlist from pool fails. ",
                initial_data=_INITIAL_DATA,
                ok_reqs=[
                    (_mock_get_must_allowlist_lps, {}),
                ],
                err_reqs=[
                    (_mock_get_current_allowlist, {}),
                ],
                expected_logs=[_GET_ALLOWLIST_ERR_LOG],
            ),
            BehaviourTestCase(
                name="Removing member from pool fails. ",
                initial_data=_INITIAL_DATA,
                ok_reqs=[
                    (_mock_get_must_allowlist_lps, {}),
                    (_mock_get_current_allowlist, {"allowlist": _MOCK_MEMBERS[2:3]}),
                ],
                err_reqs=[
                    (_mock_get_remove_allowed_address_tx, {}),
                ],
                expected_logs=[
                    _REMOVE_MEMBER_ERR_LOG,
                ],
            ),
            BehaviourTestCase(
                name="Adding member to allowlist from pool fails. ",
                initial_data=_INITIAL_DATA,
                ok_reqs=[
                    (_mock_get_must_allowlist_lps, {}),
                    (_mock_get_current_allowlist, {}),
                ],
                err_reqs=[
                    (_mock_get_add_allowed_address_tx, {}),
                ],
                expected_logs=[
                    _ADD_MEMBER_ERR_LOG,
                ],
                allowed_lp_addresses=_MOCK_MEMBERS[:1],
            ),
            BehaviourTestCase(
                name="Multisend tx preparation fails. ",
                initial_data=_INITIAL_DATA,
                ok_reqs=[
                    (_mock_get_must_allowlist_lps, {}),
                    (_mock_get_current_allowlist, {"allowlist": _MOCK_MEMBERS[2:3]}),
                    (_mock_get_remove_allowed_address_tx, {}),
                ],
                err_reqs=[
                    (_mock_get_multisend_tx, {}),
                ],
                expected_logs=[
                    _MULTISEND_ERR_LOG,
                ],
            ),
            BehaviourTestCase(
                name="Safe tx hash preparation fails. ",
                initial_data=_INITIAL_DATA,
                ok_reqs=[
                    (_mock_get_must_allowlist_lps, {}),
                    (_mock_get_current_allowlist, {"allowlist": _MOCK_MEMBERS[2:3]}),
                    (_mock_get_remove_allowed_address_tx, {}),
                    (_mock_get_multisend_tx, {}),
                ],
                err_reqs=[
                    (_mock_get_raw_safe_transaction_hash, {}),
                ],
                expected_logs=[
                    _SAFE_HASH_ERR_LOG,
                ],
            ),
            BehaviourTestCase(
                name="Safe tx hash preparation fails. ",
                initial_data=_INITIAL_DATA,
                ok_reqs=[
                    (_mock_get_must_allowlist_lps, {"is_enforced": False}),
                    (_mock_get_current_allowlist, {}),
                ],
                err_reqs=[
                    (_mock_set_must_allowlist_lps_tx, {}),
                ],
                expected_logs=[
                    _SET_ALLOWLIST_ERR_LOG,
                ],
            ),
        ],
    )
    def test_run(self, test_case: BehaviourTestCase, caplog: LogCaptureFixture) -> None:
        """Run tests."""
        self.mock_params(test_case)
        self.fast_forward(data=test_case.initial_data)
        self.behaviour.act_wrapper()

        # apply the OK reqs first
        for ok_req, kwargs in test_case.ok_reqs:
            ok_req(self, **kwargs)

        # apply the failing reqs
        for err_req, kwargs in test_case.err_reqs:
            err_req(self, **kwargs, error=True)

        # check that the expected logs appear
        for expected_log in test_case.expected_logs:
            assert expected_log in caplog.text

        # the behaviour should complete
        self.complete(event=test_case.expected_event)

    def mock_params(self, test_case: BehaviourTestCase) -> None:
        """Update skill params."""
        self.skill.skill_context.params.allowed_lp_addresses = list(
            test_case.allowed_lp_addresses
        )
