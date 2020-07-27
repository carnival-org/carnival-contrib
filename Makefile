.PHONY: dist clean qa test todos install docs test_deps

clean:
	rm -rf carnival_contrib.egg-info dist build

test_deps:
	pip3 install -qr requirements_dev.txt
	python setup.py develop

qa:
	flake8 .
	mypy --warn-unused-ignores --package carnival_contrib

test: test_deps qa
	pytest -x --cov-report term --cov=carnival_contrib -vv tests/

todos:
	grep -r TODO carnival_contrib

install:
	pip3 install --force-reinstall .

docs:
	pip install sphinx
	make -C docs html

dist:
	python3 setup.py sdist
	twine upload dist/*
	git tag `cat setup.py | grep VERSION | grep -v version | cut -d= -f2 | tr -d "[:space:]"`
	git push --tags

