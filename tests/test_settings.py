from app.config.settings import Settings


def test_mysql_settings():
    settings = Settings()

    assert isinstance(settings.mysql_host, str)
    assert isinstance(settings.mysql_port, int)
    assert settings.mysql_port == 3306
    assert settings.mysql_user
    assert settings.mysql_password is not None
    assert settings.mysql_database

    assert settings.mysql_pool_size == 5
    assert settings.mysql_max_overflow == 10
    assert settings.mysql_pool_timeout == 30
    assert settings.mysql_pool_recycle == 1800


def test_default_settings():
    settings = Settings()

    assert settings.app_name == "Standard Data Pipeline"
    assert settings.environment == "development"
    assert settings.log_level == "INFO"
    assert settings.batch_size == 1000


def test_batch_size_must_be_positive():
    settings = Settings(batch_size=500)

    assert settings.batch_size == 500


def test_chroma_settings():
    settings = Settings()

    assert settings.chroma_path == "data/chroma"
    assert settings.chroma_collection == "documents"
def test_ai_settings():
    settings = Settings()

    assert settings.ai_enabled is True
    assert settings.embedding_provider == "chromadb"


def test_ai_settings_can_be_configured():
    settings = Settings(
        ai_enabled=False,
        embedding_provider="custom",
    )

    assert settings.ai_enabled is False
    assert settings.embedding_provider == "custom"