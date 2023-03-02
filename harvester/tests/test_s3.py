import boto3
import moto
import pytest

from harvester.s3_methods import load_s3

@pytest.fixture
def empty_bucket():
    moto_fake = moto.mock_s3()
    try:
        moto_fake.start()
        conn = boto3.resource('s3')
        conn.create_bucket(Bucket="test-bucket-name")  # or the name of the bucket you use
        yield conn
    finally:
        moto_fake.stop()

def test_upload_object(empty_bucket):
    mock_config = {"S3_PROVIDERS":['AWS'], "AWS_BUCKET_NAME":"test-bucket-name"}
    buckets = load_s3(mock_config).s3Clients
    file_bytes = b'Test_text'
    object_name = '/test_object/name'
    for producer in buckets:
        buckets[producer].write_object_s3(file_bytes=file_bytes, object_name=object_name)
    
