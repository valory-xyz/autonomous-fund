# Internal audit of autonomous-fund (chore/final-audit)

This is the second internal audit. <br>
The previous audit is internal audit for v0.1.0-pre-audit [README_audit_1.md](README_audit_1.md)

The review has been performed based on the contract code in the following repository:<br>
https://github.com/valory-xyz/autonomous-fund <br>
commit: `7d6f758443a0dd4bd147bfd102dbd2e7b446597a`  or `chore/final-audit`

## Objectives
The audit is focused on [packages/balancer](https://github.com/valory-xyz/autonomous-fund/tree/main/packages/balancer) in this repo.

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
packages/balancer/agents/autonomous_fund/tests/test_agents/base.py                                               28      4    86%   93-99
packages/balancer/agents/autonomous_fund/tests/test_agents/test_autonomous_fund.py                               37      0   100%
packages/balancer/agents/autonomous_fund/tests/test_contracts/__init__.py                                         1      0   100%
packages/balancer/agents/autonomous_fund/tests/test_contracts/test_managed_pool/__init__.py                       1      0   100%
packages/balancer/agents/autonomous_fund/tests/test_contracts/test_managed_pool/test_contract.py                 30      0   100%
packages/balancer/agents/autonomous_fund/tests/test_contracts/test_managed_pool_controller/__init__.py            1      0   100%
packages/balancer/agents/autonomous_fund/tests/test_contracts/test_managed_pool_controller/test_contract.py      50      0   100%
packages/balancer/contracts/__init__.py                                                                           1      0   100%
packages/balancer/contracts/managed_pool/__init__.py                                                              3      0   100%
packages/balancer/contracts/managed_pool/contract.py                                                             27      3    89%   50, 57, 64
packages/balancer/contracts/managed_pool_controller/__init__.py                                                   3      0   100%
packages/balancer/contracts/managed_pool_controller/contract.py                                                  46      8    83%   51, 58, 65, 123, 162-173
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
...

tox -e py3.10 -- -m 'e2e'
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
packages/balancer/agents/autonomous_fund/tests/test_agents/base.py                                               28      3    89%   94-99
packages/balancer/agents/autonomous_fund/tests/test_agents/test_autonomous_fund.py                               37      0   100%
packages/balancer/agents/autonomous_fund/tests/test_contracts/__init__.py                                         1      0   100%
packages/balancer/agents/autonomous_fund/tests/test_contracts/test_managed_pool/__init__.py                       1      0   100%
packages/balancer/agents/autonomous_fund/tests/test_contracts/test_managed_pool/test_contract.py                 30      8    73%   55, 60, 64-77
packages/balancer/agents/autonomous_fund/tests/test_contracts/test_managed_pool_controller/__init__.py            1      0   100%
packages/balancer/agents/autonomous_fund/tests/test_contracts/test_managed_pool_controller/test_contract.py      50     22    56%   60-64, 69, 74, 78-103, 107
packages/balancer/contracts/__init__.py                                                                           1      0   100%
packages/balancer/contracts/managed_pool/__init__.py                                                              3      0   100%
packages/balancer/contracts/managed_pool/contract.py                                                             27      7    74%   50, 57, 64, 77-82
packages/balancer/contracts/managed_pool_controller/__init__.py                                                   3      0   100%
packages/balancer/contracts/managed_pool_controller/contract.py                                                  46     23    50%   51, 58, 65, 100-140, 162-173
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
...
========================================================================================================= short test summary info ==========================================================================================================
FAILED packages/balancer/agents/autonomous_fund/tests/test_agents/test_autonomous_fund.py::TestAutonomousFundFourAgents::test_run[4] - ValueError: unsupported hash type ripemd160
FAILED packages/balancer/agents/autonomous_fund/tests/test_agents/test_autonomous_fund.py::TestAutonomousFundTwoAgents::test_run[2] - ValueError: unsupported hash type ripemd160
FAILED packages/balancer/agents/autonomous_fund/tests/test_agents/test_autonomous_fund.py::TestAutonomousFundSingleAgent::test_run[1] - ValueError: unsupported hash type ripemd160
```
Conclusions: <br>
Everything generally works as described in the file https://github.com/valory-xyz/autonomous-fund/README.md <br>
This has not changed for the worse since the first audit. <br>
Not 100% coverage is a minor issue. <br>
Since this repository is called the `final` one, it would be good to pay attention to lines of code not covered by tests. <br>

### Review of `packages/balancer/`
A quick code review with short notes for each file in the project can be found in the file <br>
packages/balancer: [packages_balancer.md](packages_balancer.md).

WIP <br>
Update: 09-11-22. <br>
* So far, the code has been reviewed up to
```
    ├── fear_and_greed_oracle_abci
    │   ├── behaviours.py (ok)
```
### Fixing based on results first internal audit (v0.1.0-pre-audit)
Well know points from a previous audit for which there was a clear agreement with the developers that this should be corrected. <br>
https://github.com/valory-xyz/autonomous-fund/pull/37/files/eb6872bed54ae8b353ff7c6b95f64783ca831a44 <br>

### Conclusions
WIP

