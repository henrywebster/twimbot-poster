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

# TODO: make docker image name variable
run:
	docker run --env-file .env twimbot-poster

test: $(SRC_DIR) $(TEST_DIR)
	flake8 $(SRC_DIR) $(TEST_DIR) &&\
		pytest -v $(TEST_DIR)/ &&\
		pylint $(SRC_DIR)

format:
	black $(SRC_DIR) $(TEST_DIR)

.PHONY: install build run format invoke deploy
