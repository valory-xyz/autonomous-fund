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
from typing import Any, Dict, List, Optional, cast

from aea.common import JSONLike
from aea.configurations.base import PublicId
from aea.contracts.base import Contract
from aea_ledger_ethereum import EthereumApi, LedgerApi
from web3.types import Nonce, TxParams, Wei


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
    def scale_down_weights(cls, weights: List[int]) -> List[float]:
        """Scales down the weights to be represented in the [0, 100] interval."""
        scaled_weights = list(map(lambda weight: weight / SCALING_FACTOR, weights))
        return scaled_weights

    @classmethod
    def get_gradual_weight_update_params(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
    ) -> Dict[str, Any]:
        """
        Returns the current gradual weight change update parameters.

        :return: the update params
        """
        contract_instance = cls.get_instance(ledger_api, contract_address)
        update_params = (
            contract_instance.functions.getGradualWeightUpdateParams().call()
        )
        start_time = int(update_params[0])
        end_time = int(update_params[1])
        start_weights = cls.scale_down_weights(update_params[2])
        end_weights = cls.scale_down_weights(update_params[3])
        return dict(
            start_time=start_time,
            end_time=end_time,
            start_weights=start_weights,
            end_weights=end_weights,
        )

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
        scaled_weights = cls.scale_down_weights(current_weights)
        return dict(
            weights=scaled_weights,
        )

    @classmethod
    def get_set_must_allowlist_lps_tx(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
        must_allowlist_lps: bool,
    ) -> Dict[str, Any]:
        """
        Get the encoded params for a update weights gradually function call.

        Note: This transaction is not being signed here. We simply encode the data for calling `updateWeightsGradually`
        function. This data is later passed to the safe contract, that will ultimately make the tx.

        :param must_allowlist_lps: The datetime from which the update should begin.
        :return: the encoded tx data
        """
        contract_instance = cls.get_instance(ledger_api, contract_address)
        tx_data = contract_instance.encodeABI(
            fn_name="setMustAllowlistLPs",
            args=[
                must_allowlist_lps,
            ],
        )

        return dict(
            data=tx_data,
        )

    @classmethod
    def update_weights_gradually(  # pylint: disable=too-many-locals
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
        sender_address: str,
        start_datetime: int,
        end_datetime: int,
        tokens: List[str],
        end_weights: List[int],
        gas: Optional[int] = None,
        gas_price: Optional[int] = None,
        max_fee_per_gas: Optional[int] = None,
        max_priority_fee_per_gas: Optional[int] = None,
    ) -> JSONLike:
        """
        Builds and returns the tx to update the weights of a pool.

        NOTE: THIS IS NOT USED TO SEND TXs VIA THE SAFE CONTRACT!
        If you want to send TXs via the safe contract, you need to use
        `get_update_weights_gradually_tx`.

        :param ledger_api: ledger API object.
        :param contract_address: Address of the Managed Pool Controller
        :param sender_address: the address of the tx sender
        :param start_datetime: The datetime from which the update should begin.
        :param end_datetime: The datetime in which the update should end.
        :param tokens: The tokens in the pool.
        :param end_weights: What to set the weights to, updated gradually.
        :param gas: Gas
        :param gas_price: Gas Price
        :param max_fee_per_gas: max
        :param max_priority_fee_per_gas: max
        :return: the raw transaction
        """
        eth_api = cast(EthereumApi, ledger_api)
        contract = cls.get_instance(ledger_api, contract_address)
        tx_parameters = TxParams()

        if gas_price is not None:
            tx_parameters["gasPrice"] = Wei(gas_price)  # pragma: nocover

        if max_fee_per_gas is not None:
            tx_parameters["maxFeePerGas"] = Wei(max_fee_per_gas)  # pragma: nocover

        if max_priority_fee_per_gas is not None:
            tx_parameters["maxPriorityFeePerGas"] = Wei(  # pragma: nocover
                max_priority_fee_per_gas
            )

        if (
            gas_price is None
            and max_fee_per_gas is None
            and max_priority_fee_per_gas is None
        ):
            tx_parameters.update(eth_api.try_get_gas_pricing())

        if gas is not None:
            tx_parameters["gas"] = Wei(gas)

        nonce = eth_api._try_get_transaction_count(  # pylint: disable=protected-access
            sender_address
        )
        tx_parameters["nonce"] = Nonce(nonce)

        if nonce is None:
            raise ValueError("No nonce returned.")  # pragma: nocover

        scaled_weights = list(map(lambda weight: weight * SCALING_FACTOR, end_weights))
        raw_tx = contract.functions.updateWeightsGradually(
            start_datetime,
            end_datetime,
            tokens,
            scaled_weights,
        ).buildTransaction(tx_parameters)

        return raw_tx

    @classmethod
    def get_update_weights_gradually_tx(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
        start_datetime: int,
        end_datetime: int,
        tokens: List[str],
        end_weights: List[int],
    ) -> Dict[str, Any]:
        """
        Get the encoded params for a update weights gradually function call.

        Note: This transaction is not being signed here. We simply encode the data for calling `updateWeightsGradually`
        function. This data is later passed to the safe contract, that will ultimately make the tx.

        :param start_datetime: The datetime from which the update should begin.
        :param end_datetime: The datetime in which the update should end.
        :param tokens: The tokens in the pool.
        :param end_weights: What to set the weights to, updated gradually.
        :return: the encoded tx data
        """
        contract_instance = cls.get_instance(ledger_api, contract_address)
        scaled_weights = list(map(lambda weight: weight * SCALING_FACTOR, end_weights))
        tx_data = contract_instance.encodeABI(
            fn_name="updateWeightsGradually",
            args=[
                start_datetime,
                end_datetime,
                tokens,
                scaled_weights,
            ],
        )

        return dict(
            data=tx_data,
        )
