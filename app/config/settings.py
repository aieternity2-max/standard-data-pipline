from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    app_name: str = "Standard Data Pipeline"
    environment: str = "development"
    log_level: str = "INFO"

    # Pipeline
    batch_size: int = Field(
        default=1000,
        gt=0,
    )

    # ChromaDB
    chroma_path: str = "data/chroma"
    chroma_collection: str = "documents"

    # AI
    ai_enabled: bool = True
    embedding_provider: str = "chromadb"


    # MySQL
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str | None = None
    mysql_password: str | None = None
    mysql_database: str | None = None

    mysql_pool_size: int = Field(
        default=5,
        gt=0,
    )

    mysql_max_overflow: int = Field(
        default=10,
        ge=0,
    )

    mysql_pool_timeout: int = Field(
        default=30,
        gt=0,
    )

    mysql_pool_recycle: int = Field(
        default=1800,
        gt=0,
    )

    # ChromaDB
    chroma_path: str = "data/chroma"
    chroma_collection: str = "documents"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
