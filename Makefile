SHELL := /bin/bash

SRC_DIR = twimbot_poster
TEST_DIR = tests

install:
	pip install --upgrade pip &&\
		pip install -r test-requirements.txt

build:
	sam build

deploy:
	sam deploy

# TODO: make docker image name variable
run:
	docker run --env-file .env twimbot-poster

test: $(SRC_DIR) $(TEST_DIR)
	flake8 $(SRC_DIR) $(TEST_DIR) &&\
		pytest -v $(TEST_DIR)/ &&\
		pylint $(SRC_DIR)

format:
	black $(SRC_DIR) $(TEST_DIR)

.PHONY: install build run format
