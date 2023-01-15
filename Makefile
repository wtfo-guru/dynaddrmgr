SHELL:=/usr/bin/env bash
PROJECT_VERSION ?= $(shell grep ^current_version .bumpversion.cfg | awk '{print $$NF'} | tr '-' '.')
WHEELS ?= /home/jim/dev/ansible/wtfplaybooks/wheels

.PHONY: black mypy lint unit package test publish publish-test vars build
vars:
	echo "PROJECT_VERSION: $(PROJECT_VERSION)"

black:
	poetry run isort .
	poetry run black .

mypy: black
	poetry run mypy dynaddrmgr tests/*.py

lint: mypy
	poetry run flake8 .
	poetry run doc8 -q docs

unit:
	poetry run pytest tests

package:
	poetry check
	poetry run pip check
	poetry run safety check --full-report

test: lint package unit

build: test
	poetry build
	cp dist/dynaddrmgr-$(PROJECT_VERSION)-py3-none-any.whl $(WHEELS)
	sync-wheels

publish: build
	poetry publish

publish-test: test build
	poetry publish -r test-pypi


.DEFAULT:
	@cd docs && $(MAKE) $@

