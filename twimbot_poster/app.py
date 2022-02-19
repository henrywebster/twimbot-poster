"""
Application logic for twimbot-poster.
"""

import json
import traceback
import os
import tempfile
import random
import logging
import boto3
import tweepy

logging.basicConfig(level=logging.ERROR)

logger = logging.getLogger(__name__)


def get_unposted(table, index):
    """
    Get entries from an unposted index.
    """
    return table.scan(IndexName=index)["Items"]


def choose_image(lst):
    """
    Select an image from possible choices.
    """
    if not lst:
        raise ValueError("No unposted images returned from index.")
    return random.choice(lst)


def handle_image(bucket, filename, callback):
    """
    Process an image file from Amazon S3.
    """
    with tempfile.SpooledTemporaryFile() as file_handle:
        bucket.download_fileobj(filename, file_handle)

        # move pointer to beginning of buffer for reading
        file_handle.seek(0)
        return callback(file_handle)


def post(tweepy_api, title, file_handle):
    """
    Post an image to Twitter based on a title and given file handle.
    """
    return tweepy_api.update_status(
        title,
        media_ids=[
            tweepy_api.simple_upload(filename="image.png", file=file_handle).media_id
        ],  # warning: hardcoded PNG support
    ).id


def update_posted(table, key):
    """
    Modify the entry of a given key in the database to remove it from the unposted index.
    """
    # removing this attribute will remove the entry from the sparse index
    table.update_item(
        Key={"id": key},
        UpdateExpression="REMOVE process_time",
        ConditionExpression="attribute_exists(id) and attribute_exists(process_time)",
    )


def handle(table, index, bucket, tweepy_api):
    """
    Use the given AWS resources to post a random image to Twitter.
    """

    image = choose_image(get_unposted(table, index))
    result = handle_image(
        bucket,
        image["id"],
        lambda file_handle: post(tweepy_api, image["title"], file_handle),
    )
    update_posted(table, image["id"])
    return {"image": image["id"], "post_id": result}


def lambda_handler(event, context):
    """
    Process incoming events.
    """

    logger.debug(event)
    logger.debug(context)

    try:
        table = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION")).Table(
            os.getenv("DYNAMODB_TABLE")
        )

        bucket = boto3.resource("s3", region_name=os.getenv("AWS_REGION")).Bucket(
            os.getenv("S3_BUCKET")
        )

        auth = tweepy.OAuthHandler(
            os.getenv("CONSUMER_KEY"), os.getenv("CONSUMER_SECRET")
        )
        auth.set_access_token(
            os.getenv("ACCESS_TOKEN"), os.getenv("ACCESS_TOKEN_SECRET")
        )
        tweepy_api = tweepy.API(auth)

        result = handle(table, os.getenv("DYNAMODB_INDEX"), bucket, tweepy_api)
        return {
            "statusCode": 200,
            "body": json.dumps(
                {"image": result["image"], "post_id": result["post_id"]}
            ),
        }
    except Exception as err:  # pylint: disable=broad-except
        logger.error(traceback.format_exc())
        return {"statusCode": 500, "body": json.dumps({"message": str(err)})}
