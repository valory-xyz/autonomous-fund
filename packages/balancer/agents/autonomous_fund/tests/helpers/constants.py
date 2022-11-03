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

"""Defines constant used in the AutonomousFund docker image."""

# the network is configured with these accounts, every account has 100ETH
ACCOUNTS = [
    (
        "0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0",
        "0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1",
    ),
    (
        "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1",
        "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d",
    ),
    (
        "0x22d491Bde2303f2f43325b2108D26f1eAbA1e32b",
        "0x6370fd033278c143179d81c5526140625662b8daa446c22ee2d73db3707e620c",
    ),
    (
        "0xE11BA2b4D45Eaed5996Cd0823791E0C93114882d",
        "0x646f1ce2fdad0e6deeeb5c7e8e5543bdde65e86029e2fd9fc169899c440a7913",
    ),
]

# NOTE: these addresses are deterministic
PROXY_FACTORY = "0xD3aA556287Afe63102e5797BFDDd2A1E8DbB3eA5"
GNOSIS_SAFE_L2_SINGLETON = "0x32Cf1f3a98aeAF57b88b3740875D19912A522c1A"
DEFAULT_CALLBACK_HANDLER = "0xD17e1233A03aFFB9092D5109179B43d6A8828607"
SIMULATE_TX_ACCESSOR = "0x5Cca2cF3f8a0e5a5aF6A1E9A54A0c98510D92081"
COMPATIBILITY_FALLBACK_HANDLER = "0x559E01ac5e8fe78963998D632e510bEF3e306A78"
CREATE_CALL = "0x1967D06b1fabA91eAadb1be33b277447ea24fa0e"
MULTISEND = "0x336e71DaB0302774b1e4c53202bF3f2D1aD1a8e6"
MULTISEND_CALL_ONLY = "0x3635D6aE8610Ea00b6AD8342b819fD21c7Db77Ed"
MANAGED_POOL_CONTROLLER = "0xb821BFfE924E18F8B3d92473C5279d60F0Dfc6eA"
MANAGED_POOL = "0x28BF8d29cFA99aE9C3D876210453272f30e4D131"
INITIAL_POOL_WEIGHTS = [30, 40, 30]  # scaled on 0-100

# this safe contract is configured with the accounts above, and has the threshold set at 1/4.
CONFIGURED_SAFE_INSTANCE = "0x8001bdCf80F8Fb61CdcDA48419A30b430B385ca1"

MOCK_API_PATH = "/fng?format=json"
