import pytest
import boto3
from botocore.exceptions import ClientError
from moto import mock_s3
from poster import S3ImageHandler


S3_REGION = "us-east-1"
S3_BUCKET = "bucket"


@pytest.fixture
def s3_bucket():
    s3 = mock_s3()
    s3.start()
    s3_resource = boto3.resource("s3", region_name=S3_REGION)
    s3_resource.create_bucket(Bucket=S3_BUCKET)
    yield s3_resource.Bucket(S3_BUCKET)
    s3.stop()


def add_to_bucket(file):
    boto3.client("s3", region_name=S3_REGION).put_object(
        Bucket=S3_BUCKET, Key=file["filename"], Body=file["data"]
    )


@pytest.mark.parametrize("file", [{"filename": "test-0.png", "data": b"testdata"}])
def test_s3_image_handler(file, s3_bucket):
    handler = S3ImageHandler(s3_bucket)
    add_to_bucket(file)
    assert file["data"] == handler.handle(
        "test-0.png", lambda file_handle: file_handle.read()
    )


def test_s3_image_handler_image_error(s3_bucket):
    handler = S3ImageHandler(s3_bucket)
    with pytest.raises(ClientError):
        handler.handle("test-0.png", lambda file_handle: file_handle.read())


@pytest.mark.parametrize(
    ("file", "callback"),
    [({"filename": "test-0.png", "data": b"testdata"}, lambda file_handler: 1 / 0)],
)
def test_s3_image_handler_callback_error(file, callback, s3_bucket):
    handler = S3ImageHandler(s3_bucket)
    add_to_bucket(file)
    with pytest.raises(ZeroDivisionError):
        handler.handle("test-0.png", callback)
