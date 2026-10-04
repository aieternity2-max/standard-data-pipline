from app.logging.logger import get_logger


def test_logger_creation():

    logger = get_logger(
        "test_pipeline"
    )

    assert logger is not None

    assert logger.name == "test_pipeline"

    assert logger.level > 0