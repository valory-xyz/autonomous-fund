![SMPKit](images/smpkit.svg){ align=left }
The SMPKit helps you build services that execute investment strategies on liquidity pools. This functionality can be fed, for example, from the output produced by an APY Prediction service, or from external indicators such as the [Crypto Fear & Greed Index](https://cfgi.io/) (the demo below is based on the latter). Pool management services are in charge of building and submitting the appropriate transactions according to the investment strategy and execute these orders. Such services can take a number of actions depending on the input strategy. For example, at a given time point, the service could:

* Do nothing, because the funds are currently distributed according to the optimal investment strategy published.
* Do nothing, because the fees of executing the operations would exceed the benefits.
* Execute a capital swap between liquidity pools to benefit from a more advantageous position. E.g., withdrawing from one liquidity pool and depositing into another that is more profitable, or swapping between assets.

## Demo

!!! warning "Important"

    This section is under active development - please report issues in the [Autonolas Discord](https://discord.com/invite/z2PT65jKqQ).

In order to run a local demo based on the SMPKit:

1. [Set up your system](https://docs.autonolas.network/open-autonomy/guides/set_up/) to work with the Open Autonomy framework. We recommend that you use these commands:

    ```bash
    mkdir your_workspace && cd your_workspace
    touch Pipfile && pipenv --python 3.10 && pipenv shell

    pipenv install open-autonomy[all]==0.11.1
    autonomy init --remote --ipfs --reset --author=your_name
    ```

2. Fetch the Smart Managed Pools service.

    ```bash
    autonomy fetch balancer/autonomous_fund_goerli:0.1.0:bafybeia2jhq7b4chkepbobmg5if3iispxkiuo2fwo5s4jkxzuoq3jkvfra --service
    ```

3. Build the Docker image of the service agents

    ```bash
    cd autonomous_fund_goerli
    autonomy build-image
    ```

4. Prepare the `keys.json` file containing the wallet address and the private key for each of the agents.

    ??? example "Example of a `keys.json` file"

        <span style="color:red">**WARNING: Use this file for testing purposes only. Never use the keys or addresses provided in this example in a production environment or for personal use.**</span>

        ```json
        [
          {
              "address": "0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65",
              "private_key": "0x47e179ec197488593b187f80a00eb0da91f1b9d0b13f8733639f19c30a34926a"
          },
          {
              "address": "0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc",
              "private_key": "0x8b3a350cf5c34c9194ca85829a2df0ec3153be0318b5e2d3348e872092edffba"
          },
          {
              "address": "0x976EA74026E726554dB657fA54763abd0C3a0aa9",
              "private_key": "0x92db14e403b83dfe3df233f83dfa3a0d7096f21ca9b0d6d6b8d88b2b4ec1564e"
          },
          {
              "address": "0x14dC79964da2C08b23698B3D3cc7Ca32193d9955",
              "private_key": "0x4bbbf85ce3377467afe5d46f804f221813b2bb87f24d81f60f1fcdbf7cbf4356"
          }
        ]
        ```

5. Export the necessary environment variables.

    ```bash
    # set the Goerli RPC endpoint for all the agents in the service
    export SERVICE_AUTONOMOUS_FUND_RPC_0=YOUR_RPC_ENDPOINT
    export SERVICE_AUTONOMOUS_FUND_RPC_1=YOUR_RPC_ENDPOINT
    export SERVICE_AUTONOMOUS_FUND_RPC_2=YOUR_RPC_ENDPOINT
    export SERVICE_AUTONOMOUS_FUND_RPC_3=YOUR_RPC_ENDPOINT
    
    # set all participants
    export ALL_PARTICIPANTS='["0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65","0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc","0x976EA74026E726554dB657fA54763abd0C3a0aa9","0x14dC79964da2C08b23698B3D3cc7Ca32193d9955"]'
   
    # set the on chain id for the service 
    export ON_CHAIN_SERVICE_ID=1 
    ```

    !!! warning "Important"

        The keys provided in this example are for testing purposes. You must ensure to use your own keys in the `keys.json` file, and ensure that the environment variable `ALL_PARTICIPANTS` matches their addresses.

6. Build the service deployment.

    ```bash
    autonomy deploy build keys.json --aev -ltm
    ```

7. Run the service.

    ```bash
    cd abci_build
    autonomy deploy run
    ```

    You can cancel the local execution at any time by pressing ++ctrl+c++.

Note:
The safe contract on Goerli associated with the autonomous-fund is configured to run with a specific set of keys (not the ones provided above). Running the service without those keys will result in failed on-chain transactions.

## Build

1. Fork the [SMPKit repository](https://github.com/valory-xyz/autonomous-fund).
2. Make the necessary adjustments to tailor the service to your needs. This could include:
    * Adjust configuration parameters (e.g., in the `service.yaml` file).
    * Expand the service finite-state machine with your custom states.
3. Run your service as detailed above.

!!! tip "Looking for help building your own?"

    Refer to the [Autonolas Discord community](https://discord.com/invite/z2PT65jKqQ), or consider ecosystem services like [Valory Propel](https://propel.valory.xyz) for the fastest way to get your first autonomous service in production.
