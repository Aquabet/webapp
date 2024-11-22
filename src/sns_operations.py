import boto3
import json
from src.config import Config

sns_client = boto3.client(
    "sns",
    region_name=Config.AWS_REGION,
    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
)
# TODO add SNS_TOPIC_ARN, base_url in Terraform

def send_verification_email(email, verification_token):
    topic_arn = Config.SNS_TOPIC_ARN
    base_url = Config.BASE_URL
    verification_link = f"{base_url}/verify?token={verification_token}"
    message = {"email": email, "verification_link": verification_link}
    try:
        response = sns_client.publish(TopicArn=topic_arn, Message=json.dumps(message))
        print(f"SNS message sent: {response['MessageId']}")
    except Exception as e:
        print(f"Failed to send SNS message: {e}")
