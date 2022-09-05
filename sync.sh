rm -rf packages/open_aea
rm -rf packages/valory
mkdir packages/open_aea
cp -r ../open-autonomy/packages/open_aea/__init__.py packages/open_aea
cp -r ../open-autonomy/packages/open_aea/protocols packages/open_aea
mkdir packages/valory
cp -r ../open-autonomy/packages/valory/__init__.py packages/valory
mkdir packages/valory/connections
cp -r ../open-autonomy/packages/valory/connections/__init__.py packages/valory/connections
cp -r ../open-autonomy/packages/valory/connections/abci packages/valory/connections
cp -r ../open-autonomy/packages/valory/connections/http_client packages/valory/connections
cp -r ../open-autonomy/packages/valory/connections/ledger packages/valory/connections
cp -r ../open-autonomy/packages/valory/connections/p2p_libp2p_client packages/valory/connections
mkdir packages/valory/contracts
cp -r ../open-autonomy/packages/valory/contracts/__init__.py packages/valory/contracts
cp -r ../open-autonomy/packages/valory/contracts/gnosis_safe packages/valory/contracts
cp -r ../open-autonomy/packages/valory/contracts/gnosis_safe_proxy_factory packages/valory/contracts
cp -r ../open-autonomy/packages/valory/contracts/multisend packages/valory/contracts
cp -r ../open-autonomy/packages/valory/contracts/service_registry packages/valory/contracts
mkdir packages/valory/protocols
cp -r ../open-autonomy/packages/valory/protocols/__init__.py packages/valory/protocols
cp -r ../open-autonomy/packages/valory/protocols/abci packages/valory/protocols
cp -r ../open-autonomy/packages/valory/protocols/acn packages/valory/protocols
cp -r ../open-autonomy/packages/valory/protocols/contract_api packages/valory/protocols
cp -r ../open-autonomy/packages/valory/protocols/http packages/valory/protocols
cp -r ../open-autonomy/packages/valory/protocols/ledger_api packages/valory/protocols
cp -r ../open-autonomy/packages/valory/protocols/tendermint packages/valory/protocols
mkdir packages/valory/skills
cp -r ../open-autonomy/packages/valory/skills/__init__.py packages/valory/skills
cp -r ../open-autonomy/packages/valory/skills/abstract_abci packages/valory/skills
cp -r ../open-autonomy/packages/valory/skills/abstract_round_abci packages/valory/skills
cp -r ../open-autonomy/packages/valory/skills/registration_abci packages/valory/skills
cp -r ../open-autonomy/packages/valory/skills/reset_pause_abci packages/valory/skills
cp -r ../open-autonomy/packages/valory/skills/safe_deployment_abci packages/valory/skills
cp -r ../open-autonomy/packages/valory/skills/transaction_settlement_abci packages/valory/skills
cp -r ../open-autonomy/scripts/__init__.py scripts/
cp -r ../open-autonomy/scripts/check_copyright.py scripts/
cp -r ../open-autonomy/scripts/check_packages.py scripts/
