```
.
├── agents
│   ├── autonomous_fund (ok)
│   │   ├── aea-config.yaml
│   │   ├── __init__.py
│   │   └── tests (skip)
│   │       ├── helpers
│   │       │   ├── constants.py
│   │       │   ├── data
│   │       │   │   └── json_server
│   │       │   │       └── data.json
│   │       │   ├── docker.py
│   │       │   ├── fixtures.py
│   │       │   └── __init__.py
│   │       ├── __init__.py
│   │       ├── test_agents
│   │       │   ├── base.py
│   │       │   ├── __init__.py
│   │       │   └── test_autonomous_fund.py
│   │       └── test_contracts
│   │           ├── __init__.py
│   │           ├── test_managed_pool
│   │           │   ├── __init__.py
│   │           │   └── test_contract.py
│   │           └── test_managed_pool_controller
│   │               ├── __init__.py
│   │               └── test_contract.py
│   └── __init__.py
├── contracts
│   ├── __init__.py
│   ├── managed_pool
│   │   ├── build
│   │   │   └── IManagedPool.json (ok)
│   │   ├── contract.py (ok) (WeightedPool issue is solved.)
Ref: https://github.com/valory-xyz/autonomous-fund/pull/37/files/eb6872bed54ae8b353ff7c6b95f64783ca831a44#r1011472552
Issue is solved.
│   │   ├── contract.yaml
│   │   └── __init__.py
│   └── managed_pool_controller 
│       ├── build
│       │   └── ManagedPoolController.json
│       ├── contract.py (ok) (WeightedPool issue is solved. end_weights check in WIP)
if (
            gas_price is None
            and max_fee_per_gas is None
            and max_priority_fee_per_gas is None
        ):
            tx_parameters.update(eth_api.try_get_gas_pricing())
Is it possible to have a combination in which only one of the values will be None? Because the update condition: x is None and y is None and z is None => true and true and true

scaled_weights = list(map(lambda weight: weight * SCALING_FACTOR, end_weights))
As I understand is implemented via "model" of "skill":
Fixing: https://github.com/valory-xyz/autonomous-fund/commit/5637105e6a5b65ca5b1fe9fc3f2e40522220fa9b
Issue is solved.
│       ├── contract.yaml
│       └── __init__.py
├── __init__.py
└── skills
    ├── autonomous_fund_abci
    │   ├── behaviours.py (ok)
    │   ├── composition.py (ok)
    │   ├── dialogues.py (ok)
    │   ├── fsm_specification.yaml
    │   ├── handlers.py (ok)
    │   ├── __init__.py
    │   ├── models.py (ok)
    │   ├── skill.yaml
    │   └── tests (ok)
    │       ├── __init__.py
    │       ├── test_behaviours.py (ok)
    │       ├── test_dialogues.py (ok)
    │       ├── test_handlers.py (ok)
    │       └── test_models.py (ok)
    ├── fear_and_greed_oracle_abci
    │   ├── behaviours.py (ok)
    │   ├── dialogues.py (ok)
    │   ├── fsm_specification.yaml
    │   ├── handlers.py (ok)
    │   ├── __init__.py
    │   ├── models.py (ok)
    │   ├── my_model.py (ok)
    │   ├── payloads.py (ok)
    │   ├── rounds.py (ok)
    │   ├── skill.yaml
    │   └── tests
    │       ├── __init__.py
    │       ├── test_behaviours.py (ok)
Ref: https://github.com/valory-xyz/autonomous-fund/pull/37/files/eb6872bed54ae8b353ff7c6b95f64783ca831a44#r1011862790
aggregated_values.append(aggregator_method(ith_values)) most likely does not contain a bug, but please indicate in which test it was checked and what were the initial parameters for aggregation and aggregator_method.
    │       ├── test_dialogues.py (ok)
    │       ├── test_handlers.py (ok)
    │       ├── test_models.py (ok)
    │       ├── test_payloads.py (ok)
    │       └── tests_rounds.py (ok)
    ├── __init__.py
    └── pool_manager_abci
        ├── behaviours.py
Minor question:
ETHER_VALUE = 0
ether_value=self.ETHER_VALUE,  # we don't send any eth
Maybe exclude the parameter altogether? Or is it mandatory?

As I understand sum checking is implemented:
Fix: https://github.com/valory-xyz/autonomous-fund/commit/5637105e6a5b65ca5b1fe9fc3f2e40522220fa9b
Discussed: https://github.com/valory-xyz/autonomous-fund/pull/37/files/eb6872bed54ae8b353ff7c6b95f64783ca831a44#r1011503092
Issue is solved.

Ref: https://github.com/valory-xyz/autonomous-fund/pull/37/files/eb6872bed54ae8b353ff7c6b95f64783ca831a44#r1011854145
end_datetime - start_datetime >= _minWeightChangeDuration
Just a little clarification needed. Are we checking this? If we don't check now, do we plan to check?

Ref: https://github.com/valory-xyz/autonomous-fund/pull/37/files/eb6872bed54ae8b353ff7c6b95f64783ca831a44#r1012666847
As I understand it is not implemented yet?
As discussed this is an optional change.
        ├── dialogues.py (ok)
        ├── fsm_specification.yaml
        ├── handlers.py (ok)
        ├── __init__.py
        ├── models.py (ok)
Discussed: https://github.com/valory-xyz/autonomous-fund/pull/37/files/eb6872bed54ae8b353ff7c6b95f64783ca831a44#r1011503092
Issue is solved.
        ├── payloads.py (ok)
        ├── rounds.py (ok)
        ├── skill.yaml
        └── tests
            ├── __init__.py
            ├── test_behaviours.py (ok, as far as I understand test in goerli in WIP) 
            ├── test_dialogues.py (ok)
            ├── test_handlers.py (ok)
            ├── test_models.py (ok)
            ├── test_payloads.py (ok)
            └── test_rounds.py (ok)
```
