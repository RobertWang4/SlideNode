from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SlideNode API"
    env: str = "dev"
    api_prefix: str = "/v1"

    postgres_dsn: str = "sqlite:///./slidenode.db"
    redis_dsn: str = "redis://localhost:6379/0"

    storage_backend: str = "s3"
    local_storage_dir: str = "./data"

    s3_endpoint_url: str = "http://localhost:9000"
    s3_region: str = "us-east-1"
    s3_access_key: str = "minio"
    s3_secret_key: str = "minio123"
    s3_bucket: str = "slidenode"

    gcs_bucket: str = ""

    auth0_domain: str = ""
    auth0_audience: str = ""
    auth0_algorithms: str = "RS256"
    auth0_skip_verify: bool = True

    llm_provider: str = "openai"
    llm_api_key: str = ""
    llm_model: str = "stepfun/step-3.5-flash:free"
    llm_base_url: str = "https://openrouter.ai/api/v1"
    anthropic_base_url: str = "https://api.anthropic.com"
    anthropic_auth_token: str = ""
    anthropic_version: str = "2023-06-01"
    llm_timeout_seconds: int = 60
    llm_max_retries: int = 2

    max_pages: int = 200
    chunk_size_tokens: int = 1200
    chunk_overlap_tokens: int = 120
    dedupe_threshold: float = 0.86
    quality_coverage_threshold: float = 0.85
    task_timeout_minutes: int = 20

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
