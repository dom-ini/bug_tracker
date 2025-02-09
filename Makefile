.DEFAULT_GOAL := all

bandit:
	poetry run bandit -r ./bug_tracker
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
lint: black flake8 isort ruff toml_sort
