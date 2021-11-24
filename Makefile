.PHONY: clean
clean:
	rm -rf dist .mypy_cache .pytest_cache docs/build/*

.PHONY: qa
qa:
	poetry run flake8 .
	poetry run mypy --package carnival_contrib

.PHONY: test
test: qa
	poetry run pytest -x --cov-report term --cov=carnival_contrib -vv tests/

.PHONY: todos
todos:
	grep -r TODO carnival_contrib

.PHONY: docs
docs:
	poetry run make -C docs html

.PHONY: dist
dist:
	poetry publish --build
	git tag `poetry version -s`
	git push --tags
