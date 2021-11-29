"""
Classes used by the python posting script.
"""
from abc import ABC, abstractmethod
import tempfile
import logging
import random

logger = logging.getLogger(__name__)


class Journal(ABC):
    """
    Logs which images are posted.
    """

    @abstractmethod
    def get_unposted(self):
        """
        Retrieve all unposted keys (files).
        """

    @abstractmethod
    def update_posted(self, key):
        """
        Mark selected key (file) as posted.
        """


class DynamoDBJournal(Journal):
    """
    DynamoDB implementation of Journal.
    """

    def __init__(self, dynamodb_table, index):
        logger.info(f"DynamoDB table (index) - {dynamodb_table.name} ({index})")
        self.dynamodb_table = dynamodb_table
        self.index = index

    def get_unposted(self):
        return self.dynamodb_table.scan(IndexName=self.index)["Items"]

    def update_posted(self, key):
        # removing this attribute will remove the entry from the sparse index
        self.dynamodb_table.update_item(
            Key={"id": key},
            UpdateExpression="REMOVE process_time",
            ConditionExpression="attribute_exists(id) and attribute_exists(process_time)",
        )


class ImageHandler(ABC):  # pylint: disable=too-few-public-methods
    """
    Retrieves and operates on images files.
    """

    @abstractmethod
    def handle(self, filename, callback):
        """
        Retrieve and perform an operation and the file.
        """


class S3ImageHandler(ImageHandler):  # pylint: disable=too-few-public-methods
    """
    Amazon S3 implementation of ImageHandler.
    """

    def __init__(self, s3_bucket):
        logger.info(f"S3 bucket - {s3_bucket.name}")
        self.s3_bucket = s3_bucket

    def handle(self, filename, callback):
        with tempfile.SpooledTemporaryFile() as file_handle:
            self.s3_bucket.download_fileobj(filename, file_handle)

            # move pointer to beginning of buffer for reading
            file_handle.seek(0)

            return callback(file_handle)


class Tweeter(ABC):  # pylint: disable=too-few-public-methods
    """
    Interface for the Twitter API.
    """

    @abstractmethod
    def post(self, title, file_handle):
        """
        Post image to Twitter and return Tweet ID.
        """


class TweepyTweeter(Tweeter):  # pylint: disable=too-few-public-methods
    """
    Tweepy implementation of Tweeter.
    """

    def __init__(self, tweepy):
        self.tweepy = tweepy

    def post(self, title, file_handle):
        return self.tweepy.update_status(
            title,
            media_ids=[
                self.tweepy.simple_upload(
                    filename="image.png", file=file_handle
                ).media_id
            ],  # warning: hardcoded PNG support
        ).id


class Poster:
    """
    Runs the posting job.
    """

    def __init__(self, journal, image_handler, tweeter):
        self.journal = journal
        self.image_handler = image_handler
        self.tweeter = tweeter

    def run(self):
        """
        Execute the posting job.
        """
        images = self.journal.get_unposted()
        image = random.choice(images)
        result = self.image_handler.handle(
            image["id"],
            lambda file_handle: self.tweeter.post(image["title"], file_handle),
        )
        self.journal.update_posted(image["id"])
        return result
