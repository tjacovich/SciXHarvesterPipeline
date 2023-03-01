import boto3
from botocore.exceptions import ClientError
import logging

class s3_methods:
    def write_object_s3(self, file_bytes, bucket, object_name):
        try:
            response = self.s3.put_object(Bucket=bucket, Body=file_bytes, Key=object_name)
            logging.info(response)
        except ClientError as e:
            logging.error(e)
            raise e
        return response.get('ETag')
    
    def get_object_s3(self, bucket, object_name):
        try:
            response = self.s3.get_object(Bucket=bucket, Key=object_name)
        except ClientError as e:
            logging.error(e)
            raise e
        return response

class s3_provider(s3_methods):
    def __init__(self, provider, config):
        if provider == 'AWS':
            self.s3 = boto3.client(s3_methods(boto3.client('s3')))
            self.bucket = config.get('AWS_BUCKET_NAME')

class load_s3:
    def __init__(self, config):
        self.load_s3_providers(config)
    
    def load_s3_providers(self, config):
        provider_dict = {}
        for provider in config.get("S3_PROVIDERS", ['AWS']):
            provider_dict[provider] = s3_provider(provider, config)