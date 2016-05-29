.PHONY: clean-pyc clean-build docs

help:
	@echo "run - run the flask test server"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "test- run python unittest"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "sdist - package"

run:
	python run.py -td --host 0.0.0.0:8000 --live-reload

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

test:
	pip install -e .
	py.test

coverage:
	coverage run --source app nosetests tests
	coverage report -m
	coverage html
	open htmlcov/index.html

docs:
	rm -f docs/journal.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ journal
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	open docs/_build/html/index.html

release: clean
	python setup.py sdist upload

sdist: clean
	python setup.py sdist
	ls -l dist
