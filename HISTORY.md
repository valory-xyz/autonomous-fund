# Release History - `Autonomous Fund`
## v0.2.0 (2022-12-29)
- Fix/tm dialogues by @0xArdi in https://github.com/valory-xyz/autonomous-fund/pull/56
- fix: add validate and finalize timeouts by @0xArdi in https://github.com/valory-xyz/autonomous-fund/pull/57
- Bump/oa v0.6.0 by @0xArdi in https://github.com/valory-xyz/autonomous-fund/pull/58
- Feat/add update in progress check by @0xArdi in https://github.com/valory-xyz/autonomous-fund/pull/59
- fix/ remove `ManagedPoolController` from the repo by @0xArdi in https://github.com/valory-xyz/autonomous-fund/pull/60
- feat/add lp allowlist to contract by @0xArdi in https://github.com/valory-xyz/autonomous-fund/pull/62
- feat/ Add `get_allowlist` to `ManagedPool` by @0xArdi in https://github.com/valory-xyz/autonomous-fund/pull/65
- Feat/implement lp abci behaviour by @0xArdi in https://github.com/valory-xyz/autonomous-fund/pull/64
- Feat/implement abci round by @0xArdi in https://github.com/valory-xyz/autonomous-fund/pull/63
- fix: pre-conditions by @DavidMinarsch in https://github.com/valory-xyz/autonomous-fund/pull/66
- Feat/ Liquidity Provision Abci by @0xArdi in https://github.com/valory-xyz/autonomous-fund/pull/61
- Feat/chain lp abci by @0xArdi in https://github.com/valory-xyz/autonomous-fund/pull/67
- chore: update service by @0xArdi in https://github.com/valory-xyz/autonomous-fund/pull/68
- Feat/mainnet service by @0xArdi in https://github.com/valory-xyz/autonomous-fund/pull/69
- Feat/add termination by @0xArdi in https://github.com/valory-xyz/autonomous-fund/pull/72

## v0.1.0.post3 (2022-11-24)
- Utilizes the latest interface for the `ManagedPoolController` contract.

## 0.1.0.post2 (2022-11-23)
- Adds env vars to the autonomous-fund agent. 

## 0.1.0.post1 (2022-11-22)
- Bumps to `open-autonomy@v0.4.0.post1`. 

## 0.1.0 (2022-11-18)

- The first release of the Autonomous Fund, configured to run on Goerli with 4 agents. It utilizes the Fear and Greed Index to adjust the weights of a pool containing BTC, ETH and USDC.
