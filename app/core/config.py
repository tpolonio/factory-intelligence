from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str

    # AWS / LocalStack
    aws_endpoint_url: str | None = None
    aws_access_key_id: str = "test"
    aws_secret_access_key: str = "test"
    aws_default_region: str = "eu-west-1"

    # SQS
    sqs_queue_name: str = "factory-intelligence-reports-queue"

    # S3
    s3_bucket_name: str = "factory-intelligence-reports"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()