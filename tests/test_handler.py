import os
import json
import pytest
import boto3
from moto import mock_dynamodb2, mock_s3
from botocore.exceptions import ClientError
from twimbot_poster import app
import unittest
from unittest.mock import MagicMock, patch
import tempfile
from dataclasses import dataclass

import tweepy

DYNAMODB_TABLE = "table"
DYNAMODB_INDEX = "index"
AWS_REGION = "us-east-1"
S3_BUCKET = "bucket"


@pytest.fixture
def table():
    mock_dynamodb = mock_dynamodb2()
    mock_dynamodb.start()
    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    dynamodb.create_table(
        TableName=DYNAMODB_TABLE,
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "process_time", "AttributeType": "N"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
        GlobalSecondaryIndexes=[
            {
                "IndexName": DYNAMODB_INDEX,
                "KeySchema": [
                    {"AttributeName": "process_time", "KeyType": "HASH"},
                ],
                "Projection": {
                    "ProjectionType": "INCLUDE",
                    "NonKeyAttributes": ["id", "title"],
                },
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 1,
                    "WriteCapacityUnits": 1,
                },
            },
        ],
    )
    yield boto3.resource("dynamodb", region_name=AWS_REGION).Table(DYNAMODB_TABLE)
    mock_dynamodb.stop()


def dynamodb_insert_entries(entries, dynamodb_table):
    # TODO: change to batch put
    for entry in entries:
        dynamodb_table.put_item(Item=entry)


@pytest.fixture
def bucket():
    s3 = mock_s3()
    s3.start()
    s3_resource = boto3.resource("s3", region_name=AWS_REGION)
    s3_resource.create_bucket(Bucket=S3_BUCKET)
    yield s3_resource.Bucket(S3_BUCKET)
    s3.stop()


def add_to_bucket(file):
    boto3.client("s3", region_name=AWS_REGION).put_object(
        Bucket=S3_BUCKET, Key=file["filename"], Body=file["data"]
    )


@dataclass
class Status:
    """Tweepy status model"""

    id: int

    def __init__(self, status_id):
        self.id = status_id


def create_media(media_id):
    return tweepy.Media({"media_key": media_id, "media_id": media_id, "type": "photo"})


@pytest.mark.parametrize(
    ("entries", "expected"),
    [
        ([], []),
        (
            [
                {"id": "test-0.png", "title": "example-0", "process_time": 1000},
            ],
            [
                {"id": "test-0.png", "title": "example-0", "process_time": 1000},
            ],
        ),
        (
            [
                {"id": "test-0.png", "title": "example-0", "process_time": 1000},
                {"id": "test-1.png", "title": "example-1"},
            ],
            [
                {"id": "test-0.png", "title": "example-0", "process_time": 1000},
            ],
        ),
    ],
)
def test_get_unposted(entries, expected, table):
    # TODO use indirect fixtures
    dynamodb_insert_entries(entries, table)

    unposted_entries = app.get_unposted(table, DYNAMODB_INDEX)

    assert expected == unposted_entries


@pytest.mark.parametrize(
    ("entries", "key", "expected"),
    [
        (
            [
                {"id": "test-0.png", "title": "example-0", "process_time": 1000},
            ],
            "test-0.png",
            [],
        ),
        (
            [
                {"id": "test-0.png", "title": "example-0", "process_time": 1000},
                {"id": "test-1.png", "title": "example-1", "process_time": 1000},
                {"id": "test-2.png", "title": "example-2"},
            ],
            "test-1.png",
            [
                {"id": "test-0.png", "title": "example-0", "process_time": 1000},
            ],
        ),
    ],
)
def test_update_posted(entries, key, expected, table):
    dynamodb_insert_entries(entries, table)
    app.update_posted(table, key)

    assert expected == table.scan(IndexName=DYNAMODB_INDEX)["Items"]


@pytest.mark.parametrize(
    ("entries", "key"),
    [
        ([], "test-0.png"),
        (
            [
                {"id": "test-0.png", "title": "example-0", "process_time": 1000},
            ],
            "test-1.png",
        ),
        (
            [
                {"id": "test-0.png", "title": "example-0"},
            ],
            "test-0.png",
        ),
    ],
)
def test_update_posted_error(entries, key, table):
    dynamodb_insert_entries(entries, table)

    with pytest.raises(ClientError):
        app.update_posted(table, key)


@pytest.mark.parametrize(
    ("file", "callback", "expected"),
    [
        (
            {"filename": "test-0.png", "data": b"testdata"},
            lambda file_handle: file_handle.read(),
            b"testdata",
        ),
    ],
)
def test_s3_image_handler(file, callback, expected, bucket):
    add_to_bucket(file)
    assert expected == app.handle_image(bucket, "test-0.png", callback)


def test_s3_image_handler_image_error(bucket):
    with pytest.raises(ClientError):
        app.handle_image(bucket, "test-0.png", lambda file_handle: file_handle.read())


@pytest.mark.parametrize(
    ("file", "callback"),
    [({"filename": "test-0.png", "data": b"testdata"}, lambda file_handler: 1 / 0)],
)
def test_s3_image_handler_callback_error(file, callback, bucket):
    add_to_bucket(file)
    with pytest.raises(ZeroDivisionError):
        app.handle_image(bucket, "test-0.png", callback)


@patch.multiple(
    "tweepy.API",
    simple_upload=MagicMock(return_value=create_media("123")),
    update_status=MagicMock(return_value=Status(456)),
)
def test_post(**mocks):
    with tempfile.SpooledTemporaryFile("test-0.png") as file_handle:
        assert app.post(tweepy.API(), "test-0.png", file_handle)


def test_choose_image():
    assert app.choose_image([1]) == 1


def test_choose_image_empty_list_error():
    with pytest.raises(ValueError):
        app.choose_image([])


@patch.multiple(
    "tweepy.API",
    simple_upload=MagicMock(return_value=create_media("123")),
    update_status=MagicMock(return_value=Status(456)),
)
def test_handler_success(bucket, table, **mocks):
    add_to_bucket({"filename": "test-0.png", "data": b"testdata"})
    dynamodb_insert_entries(
        [{"id": "test-0.png", "title": "example-0", "process_time": 1000}], table
    )
    result = app.handle(table, DYNAMODB_INDEX, bucket, tweepy.API())
    assert result["image"] == "test-0.png"
    assert result["post_id"] == 456


@patch.multiple(
    "tweepy.API",
    simple_upload=MagicMock(return_value=create_media("123")),
    update_status=MagicMock(return_value=Status(456)),
)
def test_handler_exception(bucket, table, **mocks):
    with pytest.raises(ValueError):
        app.handle(table, DYNAMODB_INDEX, bucket, tweepy.API())


class LambdaHandlerTests(unittest.TestCase):
    def setUp(self):
        os.environ["AWS_REGION"] = AWS_REGION
        os.environ["S3_BUCKET"] = S3_BUCKET
        os.environ["DYNAMODB_TABLE"] = DYNAMODB_TABLE
        os.environ["DYNAMODB_INDEX"] = DYNAMODB_INDEX

    def tearDown(self):
        os.environ.pop("AWS_REGION", None)
        os.environ.pop("S3_BUCKET", None)
        os.environ.pop("DYNAMODB_TABLE", None)
        os.environ.pop("DYNAMODB_INDEX", None)

    @patch("tweepy.OAuthHandler")
    @patch.object(tweepy.OAuthHandler, "set_access_token", return_value="")
    @patch.object(app, "handle", return_value={"image": "test.png", "post_id": 123})
    @mock_dynamodb2
    @mock_s3
    def test_lambda_handler_success(
        self, tweepy_ctor_mock, tweepy_access_token_mock, handle_mock
    ):
        response = app.lambda_handler({}, {})

        assert response["statusCode"] == 200

        body = json.loads(response["body"])

        assert body["image"] == "test.png"
        assert body["post_id"] == 123

    @patch("tweepy.OAuthHandler")
    @patch.object(tweepy.OAuthHandler, "set_access_token", return_value="")
    @patch.object(
        app,
        "handle",
        side_effect=lambda *args: (_ for _ in ()).throw(
            ValueError("No entries found in the index.")
        ),
    )
    @mock_dynamodb2
    @mock_s3
    def test_lambda_handler_failure(
        self, tweepy_ctor_mock, tweepy_access_token_mock, handle_mock
    ):
        response = app.lambda_handler({}, {})

        assert response["statusCode"] == 500
        body = json.loads(response["body"])

        assert body["message"] == "No entries found in the index."
