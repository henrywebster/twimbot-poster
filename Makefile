SHELL := /bin/bash

install:
	pip install --upgrade pip &&\
		pip install -r test-requirements.txt

build:
	docker build -t twimbot-poster .

# TODO: make docker image name variable
run:
	docker run --env-file .env twimbot-poster

test: poster tests
	flake8 poster tests &&\
		pytest -v tests/ &&\
		pylint poster/poster.py


format:
	black poster tests

.PHONY: install build run format
