from app.config.settings import Settings


def test_default_settings():
    settings = Settings()

    assert settings.app_name == "Standard Data Pipeline"
    assert settings.environment == "development"
    assert settings.log_level == "INFO"
    assert settings.batch_size == 1000


def test_batch_size_must_be_positive():
    settings = Settings(batch_size=500)

    assert settings.batch_size == 500