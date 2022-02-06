import json
import boto3
import os
import tempfile


def get_unposted(table, index):
    return table.scan(IndexName=index)["Items"]


def handle_image(bucket, filename, callback):
    with tempfile.SpooledTemporaryFile() as file_handle:
        bucket.download_fileobj(filename, file_handle)

        # move pointer to beginning of buffer for reading
        file_handle.seek(0)
        return callback(file_handle)


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
                "data": get_unposted(table, os.getenv("DYNAMODB_INDEX"))[0]["title"],
            }
        ),
    }
