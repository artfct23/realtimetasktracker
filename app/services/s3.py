import aioboto3
from fastapi import UploadFile
from app.core.config import settings
from typing import Optional

session = aioboto3.Session()

async def init_s3_bucket():
    async with session.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    ) as s3:
        try:
            await s3.head_bucket(Bucket=settings.S3_BUCKET_NAME)
        except:
            await s3.create_bucket(Bucket=settings.S3_BUCKET_NAME)
            print(f"Bucket {settings.S3_BUCKET_NAME} created")

async def upload_file_to_s3(file: UploadFile, filename: str) -> Optional[str]:
    async with session.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    ) as s3:
        try:
            await s3.upload_fileobj(
                file.file,
                settings.S3_BUCKET_NAME,
                filename,
                ExtraArgs={"ContentType": file.content_type}
            )
            return f"{settings.S3_ENDPOINT_URL}/{settings.S3_BUCKET_NAME}/{filename}"
        except Exception as e:
            print(f"S3 Upload Error: {e}")
            return None

