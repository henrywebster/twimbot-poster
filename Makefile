SHELL := /bin/bash

test: poster tests
	flake8 poster tests &&\
	pytest -v &&\
	pylint poster/poster.py

format:
	black poster tests

.PHONY: format