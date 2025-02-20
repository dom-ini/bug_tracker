.DEFAULT_GOAL := all

bandit:
	poetry run bandit -r ./bug_tracker -x ./bug_tracker/tests
toml_sort:
	poetry run toml-sort pyproject.toml --all --in-place
flake8:
	poetry run flake8 ./bug_tracker
isort:
	poetry run isort ./bug_tracker
ruff:
	poetry run ruff check ./bug_tracker
black:
	poetry run black ./bug_tracker
check_pytestmark:
	poetry run python ./scripts/check_pytestmark.py ./bug_tracker/tests
lint: black flake8 isort ruff toml_sort check_pytestmark
test_unit:
	poetry run pytest ./bug_tracker/tests -m unit
test_integration:
	poetry run pytest ./bug_tracker/tests -m integration
test_e2e:
	poetry run pytest ./bug_tracker/tests -m e2e
test_all:
	poetry run pytest ./bug_tracker/tests
