# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2021-2022 Valory AG
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
# pylint: disable=import-error

"""Autonomous Fund Contracts Docker image."""
import logging
import time
from typing import Dict, List

import docker
import requests
from aea.exceptions import enforce
from aea_test_autonomy.docker.base import DockerImage
from docker.models.containers import Container

from packages.balancer.contracts.managed_pool_controller.tests.helpers.constants import (
    MANAGED_POOL_CONTROLLER,
)


DEFAULT_HARDHAT_ADDR = "http://127.0.0.1"
DEFAULT_HARDHAT_PORT = 8545


class AutonomousFundNetworkDockerImage(DockerImage):
    """Spawn a local network with deployed Gnosis Safe Factory and Balancer Contracts."""

    _CONTAINER_PORT = DEFAULT_HARDHAT_PORT

    def __init__(
        self,
        client: docker.DockerClient,
        addr: str = DEFAULT_HARDHAT_ADDR,
        port: int = DEFAULT_HARDHAT_PORT,
        use_safe_contracts: bool = True,
    ) -> None:
        """
        Initializes an instance.

        :param client: the docker client instance.
        :param addr: the host to run the network on, localhost by default.
        :param port: the port to run the network on, 8545 by default.
        :param use_safe_contracts: whether to make the already configured safe the manager of the pool controller.
        """
        super().__init__(client)
        self.addr = addr
        self.port = port
        self.use_safe_contracts = use_safe_contracts

    def create_many(self, nb_containers: int) -> List[Container]:
        """Instantiate the image in many containers, parametrized."""
        raise NotImplementedError()

    @property
    def tag(self) -> str:
        """Get the tag."""
        return "valory/autonomous-fund-contracts:latest"

    def _get_env_vars(self) -> Dict:
        """Returns the container env vars."""
        env_vars = {"USE_SAFE_CONTRACTS": self.use_safe_contracts.__str__().lower()}
        return env_vars

    def create(self) -> Container:
        """Create the container."""
        ports = {f"{self._CONTAINER_PORT}/tcp": ("0.0.0.0", self.port)}  # nosec
        env_vars = self._get_env_vars()
        container = self._client.containers.run(
            self.tag,
            detach=True,
            ports=ports,
            environment=env_vars,
            extra_hosts={"host.docker.internal": "host-gateway"},
        )
        return container

    def wait(self, max_attempts: int = 15, sleep_rate: float = 1.0) -> bool:
        """
        Wait until the image is running.

        :param max_attempts: max number of attempts.
        :param sleep_rate: the amount of time to sleep between different requests.
        :return: True if the wait was successful, False otherwise.
        """
        for i in range(max_attempts):
            try:
                body = {
                    "jsonrpc": "2.0",
                    "method": "eth_getCode",
                    "params": [MANAGED_POOL_CONTROLLER],
                    "id": 1,
                }
                response = requests.post(
                    f"{self.addr}:{self.port}",
                    json=body,
                )
                enforce(response.status_code == 200, "Network not running yet.")
                enforce(response.json()["result"] != "0x", "Contract not deployed yet.")
                return True
            except Exception as e:  # pylint: disable=broad-except
                logging.error("Exception: %s: %s", type(e).__name__, str(e))
                logging.info(
                    "Attempt %s failed. Retrying in %s seconds...", i, sleep_rate
                )
                time.sleep(sleep_rate)
        return False
