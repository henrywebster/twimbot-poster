import pytest
import boto3
from moto import mock_dynamodb2

from twimbot_poster import app

DYNAMODB_REGION = "us-east-1"
DYNAMODB_TABLE = "table"
DYNAMODB_INDEX = "index"


@pytest.fixture
def table():
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


@pytest.fixture()
def event():
    """Generates API GW Event"""

    return {"body": '{ "test": "body"}'}


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


# TODO: figure out integration mocks
# def test_lambda_handler(event, mocker):

#     ret = app.lambda_handler(event, "")
#     data = json.loads(ret["body"])

#     assert ret["statusCode"] == 200
#     assert "message" in ret["body"]
#     assert data["message"] == "hello world"
#     # assert "location" in data.dict_keys()
