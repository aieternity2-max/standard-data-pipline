from app.config.settings import settings


def test_application_configuration():
    assert settings.app_name == "Standard Data Pipeline"
    assert settings.environment == "development"