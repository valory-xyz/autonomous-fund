# Release History - `Autonomous Fund`
## v0.2.0 (2023-01-20)
- Adds missing Tendermint Dialogues.
- Adds validate and finalize timeouts.
- Add check for seeing whther a weight update is in progress.
- Remove `ManagedPoolController` from the repo.
- Adds support for service termination.
- doc: initial mkdocs commit.
- Bump to `open-autonomy@v0.7.0`.

## v0.1.0.post3 (2022-11-24)
- Utilizes the latest interface for the `ManagedPoolController` contract.

## 0.1.0.post2 (2022-11-23)
- Adds env vars to the autonomous-fund agent. 

## 0.1.0.post1 (2022-11-22)
- Bumps to `open-autonomy@v0.4.0.post1`. 

## 0.1.0 (2022-11-18)

- The first release of the Autonomous Fund, configured to run on Goerli with 4 agents. It utilizes the Fear and Greed Index to adjust the weights of a pool containing BTC, ETH and USDC.
