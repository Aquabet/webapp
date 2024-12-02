import os
import boto3
import json
from dotenv import load_dotenv

load_dotenv()

class Config:

    def load_secrets(self, secret_name):
        try:
            client = boto3.client('secretsmanager', region_name=os.getenv('AWS_REGION'))
            response = client.get_secret_value(SecretId=secret_name)
            if 'SecretString' in response:
                return json.loads(response['SecretString'])
            else:
                raise ValueError("Secrets not in expected format")
        except Exception as e:
            print(f"Error fetching secrets from Secrets Manager: {e}")
            return {}

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        db_secrets = self.load_secrets(os.getenv('DB_SECRETS_NAME'))
        db_username = db_secrets.get('username')
        db_password = db_secrets.get('password')
        db_host = os.getenv('RDS_ENDPOINT')
        db_name = os.getenv('DB_NAME')

        return f"mysql+pymysql://{db_username}:{db_password}@{db_host}/{db_name}"
        
    # SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
    S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION')
    SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN')
    BASE_URL = os.getenv('BASE_URL')
class TestConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True