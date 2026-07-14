from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    app_environment: str = Field(default="dev", alias="APP_ENVIRONMENT")
    database_url: str = Field(..., alias="DATABASE_URL")

    aws_endpoint_url: str | None = Field(default=None, alias="AWS_ENDPOINT_URL")
    aws_access_key_id: str = Field(default="test", alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(default="test", alias="AWS_SECRET_ACCESS_KEY")
    aws_default_region: str = Field(default="eu-west-1", alias="AWS_DEFAULT_REGION")

    sqs_queue_name: str = Field(default="factory-intelligence-reports-queue", alias="SQS_QUEUE_NAME")
    s3_bucket_name: str = Field(default="factory-intelligence-reports-bucket", alias="S3_BUCKET_NAME")

    @field_validator("app_environment")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("app_environment cannot be empty")
        return normalized

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        if not value.startswith(("postgresql://", "postgresql+psycopg2://", "postgresql+asyncpg://")):
            raise ValueError("database_url must be a PostgreSQL connection string")
        return value

    @property
    def is_development(self) -> bool:
        return self.app_environment == "dev"


settings = Settings()