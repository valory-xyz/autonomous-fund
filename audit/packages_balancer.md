```
.
├── agents
│   ├── autonomous_fund
│   │   ├── aea-config.yaml
│   │   ├── __init__.py
│   │   └── tests
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
│   │   │   └── IManagedPool.json
│   │   ├── contract.py
│   │   ├── contract.yaml
│   │   └── __init__.py
│   └── managed_pool_controller
│       ├── build
│       │   └── ManagedPoolController.json
│       ├── contract.py
│       ├── contract.yaml
│       └── __init__.py
├── __init__.py
└── skills
    ├── autonomous_fund_abci
    │   ├── behaviours.py
    │   ├── composition.py
    │   ├── dialogues.py
    │   ├── fsm_specification.yaml
    │   ├── handlers.py
    │   ├── __init__.py
    │   ├── models.py
    │   ├── skill.yaml
    │   └── tests
    │       ├── __init__.py
    │       ├── test_behaviours.py
    │       ├── test_dialogues.py
    │       ├── test_handlers.py
    │       └── test_models.py
    ├── fear_and_greed_oracle_abci
    │   ├── behaviours.py
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
