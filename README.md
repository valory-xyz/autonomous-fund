# autonomous-fund

Checkout the [spec](https://drive.google.com/file/d/1_WuEODpEKV7BR3LMKVLxyZUWjcGhHNRS/view) of the autonomous-fund, and the [grant announcement](https://medium.com/@BalancerGrants/valory-is-building-smart-managed-pools-on-balancer-1b03a2f4cc89) by Balancer. 

## Developing

- Clone the repository:

      git clone git@github.com:valory-xyz/autonomous-fund.git

- System requirements:

    - Python `>=3.7`
    - [Tendermint](https://docs.tendermint.com/v0.34/introduction/install.html) `==0.34.19`
    - [IPFS node](https://docs.ipfs.io/install/command-line/#official-distributions) `==0.6.0`
    - [Pipenv](https://pipenv.pypa.io/en/latest/installation.html) `>=2021.x.xx`
    - [Docker Engine](https://docs.docker.com/engine/install/)
    - [Docker Compose](https://docs.docker.com/compose/install/)

- Pull pre-built images:

      docker pull valory/autonolas-registries:latest
      docker pull valory/safe-contract-net:latest
      docker pull valory/autonomous-fund-contracts:latest

- Create development environment:

      make new_env && pipenv shell

- Configure command line:

      autonomy init --reset --author balancer --remote --ipfs --ipfs-node "/dns/registry.autonolas.tech/tcp/443/https"

- Pull packages:

      autonomy packages sync --update-packages

- During development use `make formatters`, `make code-checks` and `make generators`

- After building your development environment and pulling the packages, you can conduct an end-to-end test with a local network and 4 agents by running
      
      pytest packages/balancer/agents/autonomous_fund/tests/test_agents/test_autonomous_fund.py::TestAutonomousFundFourAgents
