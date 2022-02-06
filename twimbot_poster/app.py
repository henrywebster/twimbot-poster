import json
import boto3
import os


def get_unposted(table, index):
    return table.scan(IndexName=index)["Items"]


def lambda_handler(event, context):
    """
    Sample pure Lambda function
    """

    table = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION")).Table(
        os.getenv("DYNAMODB_TABLE")
    )

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "hello world",
                "data": get_unposted(table, os.getenv("DYNAMODB_INDEX")),
            }
        ),
    }
