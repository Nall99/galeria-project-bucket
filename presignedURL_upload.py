from botocore.exceptions import ClientError
from botocore.config import Config
import logging
import dotenv
import boto3
import os

dotenv.load_dotenv()

def create_presigned_post(
        bucket_name,
        object_name,
        region_name='us-east-1',
        fields=None,
        conditions=None,
        expiration=60
):
    # Generate a presigned S3 POST URL
    s3_client = boto3.client('s3',
                             endpoint_url=os.getenv('MINIO_ENDPOINT'),
                             aws_access_key_id=os.getenv("MINIO_KEY_ACCESS"),
                             aws_secret_access_key=os.getenv('MINIO_KEY_SECRET'),
                             region_name=region_name,
                             config=Config(
                                 signature_version='s3v4',
                                 s3={'addressing_style': 'path'}
                             ))
    try:
        response = s3_client.generate_presigned_post(
            Bucket=bucket_name,
            Key=object_name,
            Fields=fields,
            Conditions=conditions,
            ExpiresIn=expiration
        )
    except ClientError as e:
        logging.error(e)
        return None

    internal_endpoint = os.getenv('MINIO_ENDPOINT')
    public_endpoint = os.getenv('MINIO_PUBLIC_ENDPOINT', internal_endpoint)
    response['url'] = response['url'].replace(internal_endpoint, public_endpoint)

    return response