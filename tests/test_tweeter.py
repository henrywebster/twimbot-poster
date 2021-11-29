from unittest.mock import MagicMock, patch
import tempfile
from dataclasses import dataclass

import tweepy
from poster import TweepyTweeter


@dataclass
class Status:
    """Tweepy status model"""

    id: int

    def __init__(self, status_id):
        self.id = status_id


def create_media(media_id):
    return tweepy.Media({"media_key": media_id, "media_id": media_id, "type": "photo"})


@patch.multiple(
    "tweepy.API",
    simple_upload=MagicMock(return_value=create_media("123")),
    update_status=MagicMock(return_value=Status(456)),
)
def test_tweepy_tweeter(**mocks):
    tweeter = TweepyTweeter(tweepy.API())
    with tempfile.SpooledTemporaryFile("test-0.png") as file_handle:
        assert tweeter.post("test-0.png", file_handle)
