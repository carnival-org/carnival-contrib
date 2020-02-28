.PHONY: dist clean qa test dev nodev todos install docs

clean:
	rm -rf carnival_contrib.egg-info dist build

test_deps:
	pip3 install -qr requirements_dev.txt
	pip3 install -qe .

qa:
	flake8 .
	mypy --warn-unused-ignores --package carnival

test: qa docs
	pytest -x --cov-report term --cov=carnival -vv tests/

todos:
	grep -r TODO carnival

install:
	python3 setup.py install -f

docs:
	pip install sphinx
	make -C docs html

dist:
	python3 setup.py sdist
	twine upload dist/*
	git tag `cat setup.py | grep VERSION | grep -v version | cut -d= -f2 | tr -d "[:space:]"`
	git push --tags
