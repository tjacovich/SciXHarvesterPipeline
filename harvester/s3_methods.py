from botocore.exceptions import ClientError
import logging

class s3_methods:
    def __init__(self, s3):
        self.s3 = s3
        
    def write_object_s3(self, file_bytes, bucket, object_name):
        try:
            response = self.s3.put_object(Bucket=bucket, Body=file_bytes, Key=object_name)
        except ClientError as e:
            logging.error(e)
            raise e
        return response.json().get('ETag')
    
    def get_object_s3(self, bucket, object_name):
        try:
            response = self.s3.get_object(Bucket=bucket, Key=object_name)
        except ClientError as e:
            logging.error(e)
            raise e
        return response