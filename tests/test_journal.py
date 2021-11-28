import pytest
import boto3
from botocore.exceptions import ClientError
from moto import mock_dynamodb2
from poster import DynamoDBJournal

DYNAMODB_REGION = "us-east-1"
DYNAMODB_TABLE = "table"
DYNAMODB_INDEX = "index"


@pytest.fixture
def dynamodb_table():
    mock_dynamodb = mock_dynamodb2()
    mock_dynamodb.start()
    dynamodb = boto3.resource("dynamodb", region_name=DYNAMODB_REGION)
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
    yield boto3.resource("dynamodb", region_name=DYNAMODB_REGION).Table(DYNAMODB_TABLE)
    mock_dynamodb.stop()


def dynamodb_insert_entries(entries, dynamodb_table):
    # TODO: change to batch put
    for entry in entries:
        dynamodb_table.put_item(Item=entry)


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
def test_dynamodb_journal_get_unposted(entries, expected, dynamodb_table):
    # TODO use indirect fixtures
    dynamodb_insert_entries(entries, dynamodb_table)
    journal = DynamoDBJournal(dynamodb_table, DYNAMODB_INDEX)
    unposted_entries = journal.get_unposted()

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
def test_dynamodb_journal_update_posted(entries, key, expected, dynamodb_table):
    dynamodb_insert_entries(entries, dynamodb_table)
    journal = DynamoDBJournal(dynamodb_table, DYNAMODB_INDEX)
    journal.update_posted(key)

    assert expected == dynamodb_table.scan(IndexName=DYNAMODB_INDEX)["Items"]


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
def test_dynamodb_journal_update_posted_error(entries, key, dynamodb_table):
    dynamodb_insert_entries(entries, dynamodb_table)
    journal = DynamoDBJournal(dynamodb_table, DYNAMODB_INDEX)

    with pytest.raises(ClientError):
        journal.update_posted(key)
