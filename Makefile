SHELL := /bin/bash

SRC_DIR = twimbot_poster
TEST_DIR = tests

install:
	pip install --upgrade pip &&\
		pip install -r tests/requirements.txt

build:
	sam build

deploy:
	sam deploy

invoke:
	sam local invoke "HelloWorldFunction" -e events/event.json --env-vars env.json

test: $(SRC_DIR) $(TEST_DIR)
	flake8 $(SRC_DIR) $(TEST_DIR) &&\
		pytest --verbose --cov=./$(SRC_DIR) --cov-report=xml $(TEST_DIR)/ &&\
		pylint $(SRC_DIR)

format:
	black $(SRC_DIR) $(TEST_DIR)

.PHONY: install build run format invoke deploy
