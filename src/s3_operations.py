import boto3
from metrics import send_custom_metric
from config import Config
import time

s3_client = boto3.client('s3', region_name=Config.AWS_REGION)

def upload_file_to_s3(file_name, bucket, object_name=None):
    start_time = time.time()
    try:
        s3_client.upload_file(file_name, bucket, object_name or file_name)
    except Exception as e:
        print(e)
        return False

    elapsed = (time.time() - start_time) * 1000
    send_custom_metric("S3OperationTime", elapsed)
    return True
