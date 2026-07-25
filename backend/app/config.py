from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    google_cse_api_key: str = ""
    google_cse_engine_id: str = ""
    youtube_api_key: str = ""
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "pr-monitor/1.0"
    guardian_api_key: str = ""
    currents_api_key: str = ""
    huggingface_api_key: str = ""

    resend_api_key: str = ""
    alert_from_email: str = "alerts@yourdomain.com"

    ingest_batch_size: int = 2
    ingest_rotation_hours: int = 5

    class Config:
        env_file = ".env"


settings = Settings()
