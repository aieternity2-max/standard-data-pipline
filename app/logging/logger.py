import logging
import sys
from pathlib import Path


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "pipeline.log"


def get_logger(
    name: str = "standard_data_pipeline",
) -> logging.Logger:
    """
    Create and return a configured application logger.

    Logs are written to:
    1. Console
    2. logs/pipeline.log
    """

    logger = logging.getLogger(name)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # -----------------------------------------
    # Console Handler
    # -----------------------------------------

    console_handler = logging.StreamHandler(
        sys.stdout
    )

    # -----------------------------------------
    # File Handler
    # -----------------------------------------

    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8",
    )

    # -----------------------------------------
    # Common Formatter
    # -----------------------------------------

    formatter = logging.Formatter(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler.setFormatter(
        formatter
    )

    file_handler.setFormatter(
        formatter
    )

    # -----------------------------------------
    # Register handlers
    # -----------------------------------------

    logger.addHandler(
        console_handler
    )

    logger.addHandler(
        file_handler
    )

    logger.propagate = False

    return logger