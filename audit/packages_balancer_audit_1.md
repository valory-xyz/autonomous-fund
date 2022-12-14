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
The logic of calling contract functions needs to be explained.
The root of the problem is calling a function IControlledManagedPool(pool).updateWeightsGradually within a function updateWeightsGradually
If we look at the source code of contracts.
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
From here `pool` variable must be the address of the contract where the function updateWeightsGradually is implemented.
Accordingly, it should be a contract ManagedPool.sol.
Accordingly, it cannot be WeightedPool.sol (./pkg/pool-weighted/contracts/WeightedPool.sol).

/**
 * @dev Basic Weighted Pool with immutable weights.
 */
contract WeightedPool is BaseWeightedPool, WeightedPoolProtocolFees {
    using FixedPoint for uint256;

It is not entirely clear at the moment whether this is necessary and sufficient or only sufficient to demonstrate the idea of pool management.
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
    │   ├── behaviours.py (ok)
    │   ├── composition.py (ok)
    │   ├── dialogues.py (ok)
    │   ├── fsm_specification.yaml
    │   ├── handlers.py (ok)
    │   ├── __init__.py (ok)
    │   ├── models.py (ok)
    │   ├── skill.yaml 
    │   └── tests (ok)
    │       ├── __init__.py (ok)
    │       ├── test_behaviours.py (ok)
    │       ├── test_dialogues.py (ok)
    │       ├── test_handlers.py (ok)
    │       └── test_models.py (ok)
    ├── fear_and_greed_oracle_abci
    │   ├── behaviours.py
def get_data(self)
index_updates = json.loads(response.body)["data"]
            response_body = [
                {
                    VALUE_KEY: int(index_update[VALUE_KEY]),
                    TIMESTAMP_KEY: int(index_update[TIMESTAMP_KEY]),
                }
                for index_update in index_updates
            ]
deterministic_body = json.dumps(response_body, sort_keys=True)
The conversion logic: json->dict->json is not very clear. Is it for json validation?

timestamps = [aggregate([t_a1, t_b1]), aggregate([t_a2, t_b2])]
        for i in range(self.params.fear_and_greed_num_points):
            ith_values = values[i]
            ith_timestamps = timestamps[i]

            aggregated_values.append(aggregator_method(ith_values)) ## ith_values = values[i] => aggregator_method(ith_values) I have doubts that this is correct. Please double check this place.
            aggregated_timestamps.append(aggregator_method(ith_timestamps))

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
    │       ├── test_dialogues.py (ok)
    │       ├── test_handlers.py (ok)
    │       ├── test_models.py (ok)
    │       ├── test_payloads.py (ok)
    ├── __init__.py
    └── pool_manager_abci
        ├── behaviours.py (ok)
def get_decision
somewhere here there should be an additional check of 2 criteria:
sum(end_weights) == 1e18
start_datetime < end_datetime and end_datetime - start_datetime >= _minWeightChangeDuration

I would recommend looking at proven algorithms for "prevent flapping"
https://linuxczar.net/blog/2016/01/31/flap-detection/
https://assets.nagios.com/downloads/nagioscore/docs/nagioscore/3/en/flapping.html

        ├── dialogues.py (ok)
        ├── fsm_specification.yaml
        ├── handlers.py (ok)
        ├── __init__.py 
        ├── models.py (ok)
        ├── payloads.py (ok)
        ├── rounds.py (ok)
        ├── skill.yaml
        └── tests (ok)
            ├── __init__.py
            ├── test_behaviours.py (ok, but as far as I understand it does not work in some way testnet like goerli) 
            ├── test_dialogues.py (ok)
            ├── test_handlers.py (ok)
            ├── test_models.py (ok)
            ├── test_payloads.py (ok)
            └── test_rounds.py (ok)

```
