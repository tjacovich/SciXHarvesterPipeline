import logging

import boto3
from botocore.exceptions import ClientError, ParamValidationError


class s3_methods:
    def write_object_s3(self, file_bytes, object_name):
        try:
            response = self.bucket.put_object(Body=file_bytes, Key=object_name)
            logging.info(response)
        except (ClientError, ParamValidationError) as e:
            logging.exception(e)
            raise e
        return response.e_tag


class s3_provider(s3_methods):
    def __init__(self, provider, config):
        if provider == "AWS":
            self.s3 = boto3.resource("s3")
            self.bucket = self.s3.Bucket(config.get("AWS_BUCKET_NAME"))
        else:
            self.s3 = boto3.resource(
                "s3",
                endpoint_url=config.get(str(provider) + "_S3_URL"),
                aws_access_key_id=config.get(str(provider) + "_ACCESS_KEY_ID"),
                aws_secret_access_key=config.get(str(provider) + "_SECRET_ACCESS_KEY"),
                aws_session_token=None,
            )
            self.bucket = self.s3.Bucket(config.get(str(provider) + "_BUCKET_NAME"))


class load_s3:
    def __init__(self, config):
        self.s3Clients = self.load_s3_providers(config)

    def load_s3_providers(self, config):
        provider_dict = {}
        for provider in config.get("S3_PROVIDERS", ["AWS"]):
            provider_dict[provider] = s3_provider(provider, config)
        return provider_dict
