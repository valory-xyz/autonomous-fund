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
│   │           ├── test_managed_pool_controller
│   │           │   ├── __init__.py
│   │           │   └── test_contract.py
│   │           └── test_weighted_pool
│   │               ├── __init__.py
│   │               └── test_contract.py
│   └── __init__.py
├── contracts (ok)
│   ├── __init__.py
│   ├── managed_pool_controller
│   │   ├── build
│   │   │   └── ManagedPoolController.json
│   │   ├── contract.py
https://github.com/valory-xyz/balancer-v2-monorepo/blob/master/pkg/pool-utils/contracts/controllers/ManagedPoolController.sol
https://github.com/valory-xyz/balancer-v2-monorepo/blob/master/pkg/pool-utils/contracts/controllers/ManagedPoolController.sol#L150
At the moment, one function has been implemented from the contract. 

/**
     * @dev Update weights linearly from the current values to the given end weights, between startTime
     * and endTime.
     */
    function updateWeightsGradually(
        uint256 startTime,
        uint256 endTime,
        uint256[] calldata endWeights
    ) external virtual onlyManager withBoundPool {
        _require(canChangeWeights(), Errors.FEATURE_DISABLED);
        _require(
            endTime >= startTime && endTime - startTime >= _minWeightChangeDuration,
            Errors.WEIGHT_CHANGE_TOO_FAST
        );

        IControlledManagedPool(pool).updateWeightsGradually(startTime, endTime, endWeights);
    }
It's not entirely clear how it works.
~/valory/balancer-v2-monorepo$ grep -rn --include="*.sol" "updateWeightsGradually" ./pkg/               
./pkg/interfaces/contracts/pool-utils/IControlledManagedPool.sol:22:    function updateWeightsGradually(
./pkg/pool-weighted/contracts/managed/ManagedPoolSettings.sol:388:     * updateWeightsGradually is called during an ongoing weight change.
./pkg/pool-weighted/contracts/managed/ManagedPoolSettings.sol:394:    function updateWeightsGradually(
./pkg/pool-weighted/contracts/managed/ManagedPoolSettings.sol:419:     * @dev When calling updateWeightsGradually again during an update, reset the start weights to the current weights,
./pkg/pool-weighted/contracts/managed/ManagedPoolSettings.sol:993:            (actionId == getActionId(ManagedPoolSettings.updateWeightsGradually.selector)) ||
./pkg/pool-weighted/contracts/lbp/LiquidityBootstrappingPool.sol:182:    function updateWeightsGradually(
./pkg/pool-weighted/contracts/lbp/LiquidityBootstrappingPool.sol:311:            (actionId == getActionId(LiquidityBootstrappingPool.updateWeightsGradually.selector)) ||
./pkg/pool-weighted/contracts/lbp/LiquidityBootstrappingPool.sol:318:     * @dev When calling updateWeightsGradually again during an update, reset the start weights to the current weights,
./pkg/pool-utils/contracts/controllers/ManagedPoolController.sol:150:    function updateWeightsGradually(
./pkg/pool-utils/contracts/controllers/ManagedPoolController.sol:161:        IControlledManagedPool(pool).updateWeightsGradually(startTime, endTime, endWeights);

From here `pool` must be the address of the contract where the function updateWeightsGradually is implemented.
Accordingly, it should be a contract ManagedPool.sol.
Accordingly, it cannot be ./pkg/pool-weighted/contracts/WeightedPool.sol.

/**
 * @dev Basic Weighted Pool with immutable weights.
 */
contract WeightedPool is BaseWeightedPool, WeightedPoolProtocolFees {
    using FixedPoint for uint256;

It is not entirely clear at the moment whether this is necessary and sufficient or only sufficient to demonstrate the idea of pool management.
It is not clear whether it is checked somewhere in the code above that
sum(end_weights) == 1e18
start_datetime < end_datetime and end_datetime - start_datetime >= _minWeightChangeDuration 
WIP

│   │   ├── contract.yaml
│   │   └── __init__.py
│   └── weighted_pool
│       ├── build
│       │   └── WeightedPool.json
│       ├── contract.py
At the moment view getNormalizedWeights() only implemented 
│       ├── contract.yaml
│       └── __init__.py
├── __init__.py
└── skills 
    ├── autonomous_fund_abci (ok)

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
