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
https://github.com/valory-xyz/autonomous-fund/pull/37/files/eb6872bed54ae8b353ff7c6b95f64783ca831a44#r1011472552
Solved.
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
WIP Maybe, solved in skills
https://github.com/valory-xyz/autonomous-fund/pull/37/files/eb6872bed54ae8b353ff7c6b95f64783ca831a44#r1011503092
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

    │   ├── dialogues.py
    │   ├── fsm_specification.yaml
    │   ├── handlers.py
    │   ├── __init__.py
    │   ├── models.py
    │   ├── my_model.py
    │   ├── payloads.py
    │   ├── rounds.py
    │   ├── skill.yaml
    │   └── tests
    │       ├── __init__.py
    │       ├── test_behaviours.py
    │       ├── test_dialogues.py
    │       ├── test_handlers.py
    │       ├── test_models.py
    │       ├── test_payloads.py
    │       └── tests_rounds.py
    ├── __init__.py
    └── pool_manager_abci
        ├── behaviours.py
        ├── dialogues.py
        ├── fsm_specification.yaml
        ├── handlers.py
        ├── __init__.py
        ├── models.py
        ├── payloads.py
        ├── rounds.py
        ├── skill.yaml
        └── tests
            ├── __init__.py
            ├── test_behaviours.py
            ├── test_dialogues.py
            ├── test_handlers.py
            ├── test_models.py
            ├── test_payloads.py
            └── test_rounds.py
```
