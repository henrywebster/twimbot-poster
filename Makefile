SHELL := /bin/bash

install:
	pip install --upgrade pip &&\
		pip install -r test-requirements.txt

test: poster tests
	flake8 poster tests &&\
		pytest -v &&\
		pylint poster/poster.py

format:
	black poster tests

.PHONY: install format