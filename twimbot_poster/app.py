import os
import json
import boto3

import requests


def lambda_handler(event, context):
    """
    Sample pure Lambda function
    """

    try:
        ip = requests.get("http://checkip.amazonaws.com/")
    except requests.RequestException as e:
        # Send some context about this error to Lambda Logs
        print(e)

        raise e

    dynamodb_table = boto3.resource(
        "dynamodb", region_name=os.getenv("AWS_REGION")
    ).Table(os.getenv("DYNAMODB_TABLE"))

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "hello world",
                "data": dynamodb_table.scan()["Items"][0]["title"],
            }
        ),
    }
