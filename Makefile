.PHONY: clean
clean: clean-test clean-build clean-pyc clean-docs

.PHONY: clean-build
clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	rm -fr pip-wheel-metadata
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -fr {} +
	find . -type d -name __pycache__ -exec rm -rv {} +
	rm -fr Pipfile.lock

.PHONY: clean-docs
clean-docs:
	rm -fr site/

.PHONY: clean-pyc
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	find . -name '.DS_Store' -exec rm -fr {} +

.PHONY: clean-test
clean-test:
	rm -fr .tox/
	rm -f .coverage
	find . -name ".coverage*" -not -name ".coveragerc" -exec rm -fr "{}" \;
	rm -fr coverage.xml
	rm -fr htmlcov/
	rm -fr .hypothesis
	rm -fr .pytest_cache
	rm -fr .mypy_cache/
	rm -fr .hypothesis/
	find . -name 'log.txt' -exec rm -fr {} +
	find . -name 'log.*.txt' -exec rm -fr {} +

# isort: fix import orders
# black: format files according to the pep standards
.PHONY: formatters
formatters:
	tomte format-code

# black-check: check code style
# isort-check: check for import order
# flake8: wrapper around various code checks, https://flake8.pycqa.org/en/latest/user/error-codes.html
# mypy: static type checker
# pylint: code analysis for code smells and refactoring suggestions
# darglint: docstring linter
.PHONY: code-checks
code-checks:
	tomte check-code

# safety: checks dependencies for known security vulnerabilities
# bandit: security linter
.PHONY: security
security:
	tomte check-security
	gitleaks detect --report-format json --report-path leak_report

# generate latest abci docstrings
# generate latest hashes for updated packages
# update copyright headers
.PHONY: generators
generators:
	tox -e abci-docstrings
	tomte format-copyright --author balancer
	autonomy hash all
	autonomy packages lock
	tox -e fix-doc-hashes

.PHONY: common-checks-1
common-checks-1:
	tomte check-copyright --author balancer
	tomte check-doc-links
	tox -p -e check-hash -e check-packages -e check-doc-hashes

.PHONY: test
test:
	pytest -rfE tests/ --cov-report=html --cov=packages --cov-report=xml --cov-report=term --cov-report=term-missing --cov-config=.coveragerc
	find . -name ".coverage*" -not -name ".coveragerc" -exec rm -fr "{}" \;

v := $(shell pip -V | grep virtualenvs)

.PHONY: new_env
new_env: clean
	if [ ! -z "$(which svn)" ];\
	then\
		echo "The development setup requires SVN, exit";\
		exit 1;\
	fi;\

	if [ -z "$v" ];\
	then\
		pipenv --rm;\
		pipenv --clear;\
		pipenv --python 3.10;\
		pipenv install --dev --skip-lock;\
		echo "Enter virtual environment with all development dependencies now: 'pipenv shell'.";\
	else\
		echo "In a virtual environment! Exit first: 'exit'.";\
	fi

.PHONY: fix-abci-app-specs
fix-abci-app-specs:
	export PYTHONPATH=${PYTHONPATH}:${PWD} && autonomy analyse fsm-specs --app-class FearAndGreedOracleAbciApp --package packages/balancer/skills/fear_and_greed_oracle_abci || (echo "Failed to check fear_and_greed_oracle_abci abci consistency" && exit 1)
	export PYTHONPATH=${PYTHONPATH}:${PWD} && autonomy analyse fsm-specs --app-class PoolManagerAbciApp --package packages/balancer/skills/pool_manager_abci || (echo "Failed to check pool_manager_abci abci consistency" && exit 1)
	export PYTHONPATH=${PYTHONPATH}:${PWD} && autonomy analyse fsm-specs --app-class AutonomousFundAbciApp --package packages/balancer/skills/autonomous_fund_abci || (echo "Failed to check fear_and_greed_oracle_abci abci consistency" && exit 1)
