from unittest.mock import MagicMock, patch
import tempfile


import tweepy
from poster import TweepyTweeter


def create_media(media_id):
    return tweepy.Media({"media_key": media_id, "media_id": media_id, "type": "photo"})


# TODO
def create_status(status_id):
    return tweepy.models.Status({"id": status_id})


@patch.multiple(
    "tweepy.API",
    simple_upload=MagicMock(return_value=create_media("123")),
    update_status=MagicMock(return_value=create_status(456)),
)
def test_tweepy_tweeter(**mocks):
    tweeter = TweepyTweeter(tweepy.API())
    with tempfile.SpooledTemporaryFile("test-0.png") as file_handle:
        assert tweeter.post("test-0.png", file_handle)
