"""
Classes used by the python posting script.
"""
from abc import ABC, abstractmethod


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
