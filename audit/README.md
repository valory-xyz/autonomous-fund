# Internal audit of autonomous-fund (v0.1.0-pre-audit)

The review has been performed based on the contract code in the following repository:<br>
https://github.com/valory-xyz/autonomous-fund <br>
commit: `0756c4fdc24d99c63227057a1a8766d24a774b69`  or `v0.1.0-pre-audit`

## Objectives
The audit is focused on [packages/balancer](https://github.com/valory-xyz/open-fund/tree/main/packages/balancer) in this repo.

## Checks on quick start guides
These checks were made on the basis of the following existing documentation:
  - https://github.com/valory-xyz/autonomous-fund/README.md

```
- Pull pre-built images:
      docker pull valory/autonolas-registries:latest
      docker pull valory/safe-contract-net:latest
# ok
- Create development environment:
      make new_env && pipenv shell
# ok
- Configure command line:
      autonomy init --reset --author balancer --remote --ipfs --ipfs-node "/dns/registry.autonolas.tech/tcp/443/https"
# ok
- Pull packages:
      autonomy packages sync
# ok
make formatters
# ok
make code-checks
# ok
make security
# ok
make generators
# ok
make common-checks-1
# ok
gitleaks detect --report-format json --report-path leak_report
# ok
tox -e flake8 
flake8 run-test: commands[0] | flake8 --max-complexity 12 packages/balancer scripts tests
_________________________________________________________________________________________________________________ summary __________________________________________________________________________________________________________________
  flake8: commands succeeded
  congratulations :)
# ok
tox -e py3.10 -- -m 'not e2e'
---------- coverage: platform linux, python 3.10.6-final-0 -----------
Name                                                                                                          Stmts   Miss  Cover   Missing
-------------------------------------------------------------------------------------------------------------------------------------------
packages/__init__.py                                                                                              1      0   100%
packages/balancer/__init__.py                                                                                     1      0   100%
packages/balancer/agents/__init__.py                                                                              1      0   100%
packages/balancer/agents/autonomous_fund/__init__.py                                                              3      0   100%
packages/balancer/agents/autonomous_fund/tests/__init__.py                                                        1      0   100%
packages/balancer/agents/autonomous_fund/tests/helpers/__init__.py                                                1      0   100%
packages/balancer/agents/autonomous_fund/tests/helpers/constants.py                                              15      0   100%
packages/balancer/agents/autonomous_fund/tests/helpers/docker.py                                                 78     23    71%   70, 124, 145-148, 152, 157, 161-176, 186-197
packages/balancer/agents/autonomous_fund/tests/helpers/fixtures.py                                               32      4    88%   85-92
packages/balancer/agents/autonomous_fund/tests/test_agents/__init__.py                                            1      0   100%
packages/balancer/agents/autonomous_fund/tests/test_agents/base.py                                               27      4    85%   90-96
packages/balancer/agents/autonomous_fund/tests/test_agents/test_autonomous_fund.py                               37      0   100%
packages/balancer/agents/autonomous_fund/tests/test_contracts/__init__.py                                         1      0   100%
packages/balancer/agents/autonomous_fund/tests/test_contracts/test_managed_pool_controller/__init__.py            1      0   100%
packages/balancer/agents/autonomous_fund/tests/test_contracts/test_managed_pool_controller/test_contract.py      50      0   100%
packages/balancer/agents/autonomous_fund/tests/test_contracts/test_weighted_pool/__init__.py                      1      0   100%
packages/balancer/agents/autonomous_fund/tests/test_contracts/test_weighted_pool/test_contract.py                30      0   100%
packages/balancer/contracts/__init__.py                                                                           1      0   100%
packages/balancer/contracts/managed_pool_controller/__init__.py                                                   3      0   100%
packages/balancer/contracts/managed_pool_controller/contract.py                                                  46      8    83%   51, 58, 65, 123, 162-173
packages/balancer/contracts/weighted_pool/__init__.py                                                             3      0   100%
packages/balancer/contracts/weighted_pool/contract.py                                                            27      3    89%   50, 57, 64
packages/balancer/skills/__init__.py                                                                              1      0   100%
packages/balancer/skills/autonomous_fund_abci/__init__.py                                                         3      0   100%
packages/balancer/skills/autonomous_fund_abci/behaviours.py                                                      14      0   100%
packages/balancer/skills/autonomous_fund_abci/composition.py                                                     10      0   100%
packages/balancer/skills/autonomous_fund_abci/dialogues.py                                                       21      0   100%
packages/balancer/skills/autonomous_fund_abci/handlers.py                                                        13      0   100%
packages/balancer/skills/autonomous_fund_abci/models.py                                                          34      7    79%   72-88
packages/balancer/skills/autonomous_fund_abci/tests/__init__.py                                                   1      0   100%
packages/balancer/skills/autonomous_fund_abci/tests/test_behaviours.py                                            3      0   100%
packages/balancer/skills/autonomous_fund_abci/tests/test_dialogues.py                                             3      0   100%
packages/balancer/skills/autonomous_fund_abci/tests/test_handlers.py                                              3      0   100%
packages/balancer/skills/autonomous_fund_abci/tests/test_models.py                                                6      0   100%
packages/balancer/skills/fear_and_greed_oracle_abci/__init__.py                                                   3      0   100%
packages/balancer/skills/fear_and_greed_oracle_abci/behaviours.py                                               133      5    96%   143-148, 305-310
packages/balancer/skills/fear_and_greed_oracle_abci/dialogues.py                                                 21      0   100%
packages/balancer/skills/fear_and_greed_oracle_abci/handlers.py                                                  13      0   100%
packages/balancer/skills/fear_and_greed_oracle_abci/models.py                                                    22      0   100%
packages/balancer/skills/fear_and_greed_oracle_abci/my_model.py                                                   3      0   100%
packages/balancer/skills/fear_and_greed_oracle_abci/payloads.py                                                  43      0   100%
packages/balancer/skills/fear_and_greed_oracle_abci/rounds.py                                                    81     23    72%   66, 71, 89-105, 139-161
packages/balancer/skills/fear_and_greed_oracle_abci/tests/__init__.py                                             1      0   100%
packages/balancer/skills/fear_and_greed_oracle_abci/tests/test_behaviours.py                                     83      1    99%   236
packages/balancer/skills/fear_and_greed_oracle_abci/tests/test_dialogues.py                                       3      0   100%
packages/balancer/skills/fear_and_greed_oracle_abci/tests/test_handlers.py                                        3      0   100%
packages/balancer/skills/fear_and_greed_oracle_abci/tests/test_models.py                                          6      0   100%
packages/balancer/skills/fear_and_greed_oracle_abci/tests/test_payloads.py                                       18      0   100%
packages/balancer/skills/fear_and_greed_oracle_abci/tests/tests_rounds.py                                       144    109    24%   70-77, 98-156, 160-197, 207-265, 275-338, 342-405, 409-445
packages/balancer/skills/pool_manager_abci/__init__.py                                                            3      0   100%
packages/balancer/skills/pool_manager_abci/behaviours.py                                                        109      0   100%
packages/balancer/skills/pool_manager_abci/dialogues.py                                                          25      0   100%
packages/balancer/skills/pool_manager_abci/handlers.py                                                           13      0   100%
packages/balancer/skills/pool_manager_abci/models.py                                                             20      0   100%
packages/balancer/skills/pool_manager_abci/payloads.py                                                           27      0   100%
packages/balancer/skills/pool_manager_abci/rounds.py                                                             73      0   100%
packages/balancer/skills/pool_manager_abci/tests/__init__.py                                                      1      0   100%
packages/balancer/skills/pool_manager_abci/tests/test_behaviours.py                                             104      0   100%
packages/balancer/skills/pool_manager_abci/tests/test_dialogues.py                                                3      0   100%
packages/balancer/skills/pool_manager_abci/tests/test_handlers.py                                                 3      0   100%
packages/balancer/skills/pool_manager_abci/tests/test_models.py                                                   6      0   100%
packages/balancer/skills/pool_manager_abci/tests/test_payloads.py                                                17      0   100%
packages/balancer/skills/pool_manager_abci/tests/test_rounds.py                                                  97      0   100%
========================================================================================= 37 passed, 3 deselected, 11 warnings in 73.44s (0:01:13) =========================================================================================
_________________________________________________________________________________________________________________ summary __________________________________________________________________________________________________________________
  py3.10: commands succeeded
  congratulations :)

tox -e py3.10 -- -m 'e2e'
---------- coverage: platform linux, python 3.10.6-final-0 -----------
Name                                                                                                          Stmts   Miss  Cover   Missing
-------------------------------------------------------------------------------------------------------------------------------------------
packages/__init__.py                                                                                              1      0   100%
packages/balancer/__init__.py                                                                                     1      0   100%
packages/balancer/agents/__init__.py                                                                              1      0   100%
packages/balancer/agents/autonomous_fund/__init__.py                                                              3      0   100%
packages/balancer/agents/autonomous_fund/tests/__init__.py                                                        1      0   100%
packages/balancer/agents/autonomous_fund/tests/helpers/__init__.py                                                1      0   100%
packages/balancer/agents/autonomous_fund/tests/helpers/constants.py                                              15      0   100%
packages/balancer/agents/autonomous_fund/tests/helpers/docker.py                                                 78      4    95%   70, 124, 152, 197
packages/balancer/agents/autonomous_fund/tests/helpers/fixtures.py                                               32      0   100%
packages/balancer/agents/autonomous_fund/tests/test_agents/__init__.py                                            1      0   100%
packages/balancer/agents/autonomous_fund/tests/test_agents/base.py                                               27      3    89%   91-96
packages/balancer/agents/autonomous_fund/tests/test_agents/test_autonomous_fund.py                               37      0   100%
packages/balancer/agents/autonomous_fund/tests/test_contracts/__init__.py                                         1      0   100%
packages/balancer/agents/autonomous_fund/tests/test_contracts/test_managed_pool_controller/__init__.py            1      0   100%
packages/balancer/agents/autonomous_fund/tests/test_contracts/test_managed_pool_controller/test_contract.py      50     22    56%   60-64, 69, 74, 78-103, 107
packages/balancer/agents/autonomous_fund/tests/test_contracts/test_weighted_pool/__init__.py                      1      0   100%
packages/balancer/agents/autonomous_fund/tests/test_contracts/test_weighted_pool/test_contract.py                30      8    73%   55, 60, 64-77
packages/balancer/contracts/__init__.py                                                                           1      0   100%
packages/balancer/contracts/managed_pool_controller/__init__.py                                                   3      0   100%
packages/balancer/contracts/managed_pool_controller/contract.py                                                  46     23    50%   51, 58, 65, 100-140, 162-173
packages/balancer/contracts/weighted_pool/__init__.py                                                             3      0   100%
packages/balancer/contracts/weighted_pool/contract.py                                                            27      7    74%   50, 57, 64, 77-82
packages/balancer/skills/__init__.py                                                                              1      0   100%
packages/balancer/skills/autonomous_fund_abci/__init__.py                                                         3      0   100%
packages/balancer/skills/autonomous_fund_abci/behaviours.py                                                      14      0   100%
packages/balancer/skills/autonomous_fund_abci/composition.py                                                     10      0   100%
packages/balancer/skills/autonomous_fund_abci/dialogues.py                                                       21      0   100%
packages/balancer/skills/autonomous_fund_abci/handlers.py                                                        13      0   100%
packages/balancer/skills/autonomous_fund_abci/models.py                                                          34      8    76%   68, 72-88
packages/balancer/skills/autonomous_fund_abci/tests/__init__.py                                                   1      0   100%
packages/balancer/skills/autonomous_fund_abci/tests/test_behaviours.py                                            3      0   100%
packages/balancer/skills/autonomous_fund_abci/tests/test_dialogues.py                                             3      0   100%
packages/balancer/skills/autonomous_fund_abci/tests/test_handlers.py                                              3      0   100%
packages/balancer/skills/autonomous_fund_abci/tests/test_models.py                                                6      1    83%   33
packages/balancer/skills/fear_and_greed_oracle_abci/__init__.py                                                   3      0   100%
packages/balancer/skills/fear_and_greed_oracle_abci/behaviours.py                                               133     91    32%   55, 60, 77-97, 114-158, 176-189, 208-225, 243-263, 275-288, 304-325, 329-341, 345-360
packages/balancer/skills/fear_and_greed_oracle_abci/dialogues.py                                                 21      0   100%
packages/balancer/skills/fear_and_greed_oracle_abci/handlers.py                                                  13      0   100%
packages/balancer/skills/fear_and_greed_oracle_abci/models.py                                                    22      9    59%   42, 50-63
packages/balancer/skills/fear_and_greed_oracle_abci/my_model.py                                                   3      0   100%
packages/balancer/skills/fear_and_greed_oracle_abci/payloads.py                                                  43     10    77%   58, 63, 78-79, 84, 89, 104-105, 110, 115
packages/balancer/skills/fear_and_greed_oracle_abci/rounds.py                                                    81     25    69%   61, 66, 71, 76, 89-105, 139-161
packages/balancer/skills/fear_and_greed_oracle_abci/tests/__init__.py                                             1      0   100%
packages/balancer/skills/fear_and_greed_oracle_abci/tests/test_behaviours.py                                     83     30    64%   83-89, 98-106, 172-189, 210-241, 293-294, 373-374
packages/balancer/skills/fear_and_greed_oracle_abci/tests/test_dialogues.py                                       3      0   100%
packages/balancer/skills/fear_and_greed_oracle_abci/tests/test_handlers.py                                        3      0   100%
packages/balancer/skills/fear_and_greed_oracle_abci/tests/test_models.py                                          6      1    83%   33
packages/balancer/skills/fear_and_greed_oracle_abci/tests/test_payloads.py                                       18      5    72%   68-75
packages/balancer/skills/fear_and_greed_oracle_abci/tests/tests_rounds.py                                       144    109    24%   70-77, 98-156, 160-197, 207-265, 275-338, 342-405, 409-445
packages/balancer/skills/pool_manager_abci/__init__.py                                                            3      0   100%
packages/balancer/skills/pool_manager_abci/behaviours.py                                                        109     68    38%   63, 68, 80-98, 108-125, 129-145, 149-167, 183-201, 223-243, 255-275, 282-289, 303-326
packages/balancer/skills/pool_manager_abci/dialogues.py                                                          25      0   100%
packages/balancer/skills/pool_manager_abci/handlers.py                                                           13      0   100%
packages/balancer/skills/pool_manager_abci/models.py                                                             20      7    65%   40, 48-57
packages/balancer/skills/pool_manager_abci/payloads.py                                                           27      7    74%   46-49, 54, 64, 74
packages/balancer/skills/pool_manager_abci/rounds.py                                                             73     23    68%   60, 65, 70, 75, 80, 85, 103-119, 134-149
packages/balancer/skills/pool_manager_abci/tests/__init__.py                                                      1      0   100%
packages/balancer/skills/pool_manager_abci/tests/test_behaviours.py                                             104     42    60%   88-94, 103-111, 147, 198-206, 235-249, 275, 296, 339-355, 383-400, 431-452
packages/balancer/skills/pool_manager_abci/tests/test_dialogues.py                                                3      0   100%
packages/balancer/skills/pool_manager_abci/tests/test_handlers.py                                                 3      0   100%
packages/balancer/skills/pool_manager_abci/tests/test_models.py                                                   6      1    83%   31
packages/balancer/skills/pool_manager_abci/tests/test_payloads.py                                                17      5    71%   62-66
packages/balancer/skills/pool_manager_abci/tests/test_rounds.py                                                  97     67    31%   75-130, 134-168, 178-232, 236-270
========================================================================================================= short test summary info ==========================================================================================================
FAILED packages/balancer/agents/autonomous_fund/tests/test_agents/test_autonomous_fund.py::TestAutonomousFundFourAgents::test_run[4] - ValueError: unsupported hash type ripemd160
FAILED packages/balancer/agents/autonomous_fund/tests/test_agents/test_autonomous_fund.py::TestAutonomousFundTwoAgents::test_run[2] - ValueError: unsupported hash type ripemd160
FAILED packages/balancer/agents/autonomous_fund/tests/test_agents/test_autonomous_fund.py::TestAutonomousFundSingleAgent::test_run[1] - ValueError: unsupported hash type ripemd160
```
Conclusions: <br>
Everything generally works as described in the file https://github.com/valory-xyz/autonomous-fund/README.md <br>
Not 100% coverage (perhaps I missed something) is a minor issue. <br>
```ValueError: unsupported hash type ripemd160``` requires clarification. <br>

### Review of [Log] [Autonomous Fund]
Original proposal: [RFC] Balancer Grant Proposal: Smart Managed Pools (SMPs) <br>
Gantt chart: Project Plan – Gantt Chart - Balancer Grant <br>
Spec: [WD] Balancer Smart Managed Pools Data Sources & Specification <br>

Open questions at the time of studying the documentation: <br>
The questions are arranged from more general to more specific. <br>
1. It is not entirely clear whether there are measurable economic indicators that tell whether a pool is successfully managed or not. Perhaps the answer to this question is beyond the scope of the project. <br>
2. There is no (even formal) justification for the relationship between pool weights and "Fear and Greed Index". <br>
3. There is no (even formal) justification why these tokens were chosen. Since we are talking about ERC20 tokens, it is formally correct to write WETH (less significant) and WBTC (more significant) <br>
4. The previous question is similarly about mapping range to weights <br> 
5. It is not entirely clear which functionality is actually supported. <br>
https://docs.balancer.fi/products/balancer-pools/managed-pools
```
For example:
Active Token Management
Add
Remove
```
6. Requires a detailed explanation with which of the contracts (deployed contracts) there is interaction (read/write) and why with them. <br>
This refers to two contracts that could be identified: <br>
https://github.com/balancer-labs/balancer-v2-monorepo/blob/master/pkg/pool-weighted/contracts/WeightedPool.sol <br>
https://github.com/valory-xyz/balancer-v2-monorepo/blob/master/pkg/pool-utils/contracts/controllers/ManagedPoolController.sol <br>
As well as a contact that should probably be used. <br>
https://github.com/valory-xyz/balancer-v2-monorepo/blob/master/pkg/pool-weighted/contracts/managed/ManagedPool.sol <br>


### Review of `packages/balancer/`
A quick code review with short notes for each file in the project can be found in the file <br>
packages/balancer: [packages_balancer.md](packages_balancer.md).

Conclusions: <br>
* At the moment, the code did not raise obvious security issues. <br>
There are places that require clarification and rechecking. Details are noted in the file [packages_balancer.md](packages_balancer.md)<br>
Update: 26-10-22.
* So far, the code has been reviewed up to
```
    ├── fear_and_greed_oracle_abci
    │   ├── rounds.py (WIP)

```
