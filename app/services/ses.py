import boto3
from app.core.config import settings

async def send_email(to_email: str, subject: str, content: str):
    print(f"--- MOCK EMAIL TO {to_email} ---")
    print(f"Subject: {subject}")
    print(content)
    print("--------------------------------")
    return True

async def send_email_aws(to_email: str, subject: str, content: str):
    client = boto3.client(
        'ses',
        region_name='us-east-1',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    try:
        response = client.send_email(
            Source='noreply@yourdomain.com',
            Destination={'ToAddresses': [to_email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': content}}
            }
        )
        return True
    except Exception as e:
        print(f"SES Error: {e}")
        return False
