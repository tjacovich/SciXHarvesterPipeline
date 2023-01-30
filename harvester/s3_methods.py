import boto3
from botocore.exceptions import ClientError
import logging

class s3_methods:
    def __init__(self, s3):
        self.s3 = s3
        
    def write_file_object_s3(self, s3_client, file_obj, bucket, object_name):
        try:
            response = self.s3.upload_fileobj(file_obj, bucket, object_name)
        except ClientError as e:
            logging.error(e)
            return False

        return response