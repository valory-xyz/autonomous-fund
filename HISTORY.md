# Release History - `Autonomous Fund`
## v0.2.0 (2023-01-20)
- Adds missing Tendermint Dialogues.
- Adds validate and finalize timeouts.
- Add check for seeing whether a weight update is in progress.
- Remove `ManagedPoolController` from the repo.
- Adds support for service termination.
- doc: initial MkDocs commit.
- Bump to `open-autonomy@v0.7.0`.

## v0.1.0.post3 (2022-11-24)
- Utilizes the latest interface for the `ManagedPoolController` contract.

## v0.1.0.post2 (2022-11-23)
- Adds environment variables to the autonomous-fund agent. 

## v0.1.0.post1 (2022-11-22)
- Bumps to `open-autonomy@v0.4.0.post1`. 

## v0.1.0 (2022-11-18)

- The first release of the Autonomous Fund, configured to run on Goerli with 4 agents. It utilizes the Fear and Greed Index to adjust the weights of a pool containing BTC, ETH and USDC.
