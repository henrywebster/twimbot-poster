# Twimbot Poster 🐦🤖

![test](https://github.com/henrywebster/twimbot-poster/actions/workflows/test.yml/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Overview 🗒️

`twimbot-poster` is a dockerized application part of the _twimbot (twITTER imAGE bot)_ project.

It's purpose is to:

1. Retrieve a list of unposted images
2. Select one at random
3. Post the image to Twitter
4. Update the image as posted in the database

## Building 🏗️

Ensure you have [docker](https://docs.docker.com/get-docker/) installed and run the build command to create a docker image:

```
make build
```

## Running 🏃

Copy the [`.sample-env`](https://github.com/henrywebster/twimbot-poster/blob/main/.sample-env) file to `.env` and fill out the environment variables:

```
cp .sample-env .env
```

| Variable                | Value                                       |
| ----------------------- | ------------------------------------------- |
| `ACCESS_TOKEN`          | Access token from the Twitter API           |
| `ACCESS_TOKEN_SECRET`   | Access token secret from the Twitter API    |
| `CONSUMER_KEY`          | API key from the Twitter API                |
| `CONUMER_SECRET`        | API key secret from the Twitter API         |
| `AWS_REGION`            | AWS region                                  |
| `DYNAMODB_TABLE`        | DynamoDB table name                         |
| `DYNAMODB_INDEX`        | Global Secondary Index for unposted entries |
| `S3_BUCKET`             | S3 bucket name                              |
| `AWS_ACCESS_KEY_ID`     | AWS access key                              |
| `AWS_SECRET_ACCESS_KEY` | AWS access secret                           |

Make sure the `.env` file is never checked in as it contains sensitive information.

To obtain the `ACCESS_TOKEN`, `ACCESS_TOKEN_SECRET`, `CONSUMER_KEY`, and `CONUSMER_KEY_SECRET`, register an application on the [Twitter Developer](https://developer.twitter.com/en) portal.

To obtain the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`, follow the instructions provided for [AWS Credentials](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html) and ensure the account has the neccessary permissions (read and write on the S3 bucket and DynamoDB table).

Instructions for creating the AWS resources are coming in the future, but can be reverse-engineered by taking a look at the [scripts](https://github.com/henrywebster/twimbot-poster/tree/main/scripts) and [unit tests](https://github.com/henrywebster/twimbot-poster/blob/main/tests/test_journal.py).

Use the `run` target to run the docker image:

```
make run
```

A successful execution will return the Twitter status ID:

```
$ make run
docker run --env-file .env twimbot-poster
1465148781968699395
```

## Testing 🧪

To test the application, setup a python [virtual environment](https://docs.python.org/3/library/venv.html):

```
python -m venv venv
source venv/bin/activate
```

Next, install the test dependencies:

```
make install
```

Finally, run the tests:

```
make test
```

The project has [GitHub Actions](https://github.com/features/actions) setup to run the tests upon PR.

## Support 💪

Currently, the project is only integrated with Amazon Web Services, but support for other integrations in the future is possible.

### Record-keeping

-   [DynamoDB](https://aws.amazon.com/dynamodb/)

### File Storage

-   [S3](https://aws.amazon.com/s3/)

## Libraries Used

-   [`tweepy`](https://www.tweepy.org/) for Twitter integration
-   [`boto3`](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) for AWS integration
-   [`pytest`](https://github.com/pytest-dev/pytest) for testing
-   [`moto`](https://github.com/spulec/moto) for mocking AWS services
-   [`pylint`](https://github.com/PyCQA/pylint) for linting
-   [`black`](https://github.com/psf/black) for formatting
-   [`flake8`](https://github.com/pycqa/flake8) for style guide enforcement

## Future Work 📅

-   Support more implementations beyond DynamoDB and S3
-   Include detailed instructions on setting up the AWS services or provide a [CloudFormation template](https://aws.amazon.com/cloudformation/).
-   Set up a GitHub Action to publish the docker container
-   Enable project versioning
