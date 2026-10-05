import logging

from app.logging.logger import get_logger
from app.config.settings import settings


def test_logger_creation():

    logger = get_logger(
        "test_pipeline"
    )

    assert logger is not None

    assert logger.name == "test_pipeline"

    assert logger.level > 0


def test_logger_uses_configured_level():

    logger = get_logger(
        "test_log_level"
    )

    expected_level = getattr(
        logging,
        settings.log_level.upper(),
    )

    assert logger.level == expected_level