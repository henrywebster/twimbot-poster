import os
import sys
import logging
import boto3
import tweepy
from poster import Poster, DynamoDBJournal, S3ImageHandler, TweepyTweeter

logging.basicConfig(level=logging.ERROR)

logger = logging.getLogger(__name__)


def wrapper():
    auth = tweepy.OAuthHandler(os.getenv("CONSUMER_KEY"), os.getenv("CONSUMER_SECRET"))
    auth.set_access_token(os.getenv("ACCESS_TOKEN"), os.getenv("ACCESS_TOKEN_SECRET"))
    tweepy_api = tweepy.API(auth)
    tweeter = TweepyTweeter(tweepy_api)

    logger.info("AWS region - {}", os.getenv("AWS_REGION"))

    dynamodb_table = boto3.resource(
        "dynamodb", region_name=os.getenv("AWS_REGION")
    ).Table(os.getenv("DYNAMODB_TABLE"))
    journal = DynamoDBJournal(dynamodb_table, os.getenv("DYNAMODB_INDEX"))

    s3_bucket = boto3.resource("s3", region_name=os.getenv("REGION_NAME")).Bucket(
        os.getenv("S3_BUCKET")
    )
    image_handler = S3ImageHandler(s3_bucket)

    poster = Poster(journal, image_handler, tweeter)
    return poster.run()


if __name__ == "__main__":
    try:
        print(wrapper())
    except Exception as ex:
        print(ex, sys.stderr)
        sys.exit(1)
