import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # LLM Settings
    LLM_BASE_URL: str = "http://127.0.0.1:8080/v1"
    LLM_MODEL: str = "Qwen2.5-Coder-7B-Instruct"
    LLM_TEMPERATURE: float = 0.0
    LLM_MAX_TOKENS: int = 512
    LLM_CONTEXT_SIZE: int = 8192
    MAX_CONCURRENT_LLM_REQUESTS: int = 1

    # Database Settings
    DB_HOST: str = "10.150.19.153"
    DB_USER: str = "epdatalake"
    DB_PASSWORD: str = "glummonkey60"
    DB_NAME: str = "epdatalake"
    DB_PORT: int = 8123

    CLICKHOUSE_URL: str = "http://10.150.19.153:8123/"
    DATABASE_URL: str = "http://epdatalake:glummonkey60@10.150.19.153:8123/epdatalake"
    ADMIN_DATABASE_URL: str = "http://epdatalake:glummonkey60@10.150.19.153:8123/epdatalake"
    SQL_STATEMENT_TIMEOUT_MS: int = 5000

    # Query Limits
    MAX_RESULT_ROWS: int = 1000
    MAX_SQL_LENGTH: int = 5000
    MAX_JOINS: int = 5
    MAX_SQL_RETRIES: int = 2
    MAX_QUERY_COST: float = 10000.0

    # Environment
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
