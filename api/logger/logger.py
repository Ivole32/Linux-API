
# Logging core
import logging
from logging.handlers import RotatingFileHandler

# Path utility
from pathlib import Path

# Configuration

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"

LOG_LEVEL = logging.INFO

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(filename)s:%(lineno)d | "
    "%(message)s"
)


# Create and configure logger
def setup_logger() -> logging.Logger:
    """
    Set up the application logger with console and file handlers.
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger("app")
    logger.setLevel(LOG_LEVEL)

    # Prevents adding multiple handlers if called multiple times
    if logger.handlers:
        return logger

    formatter = logging.Formatter(LOG_FORMAT)

    # Console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# Global logger instance
logger = setup_logger()

def log(level: int, message: str) -> None:
    """
    Log a message with the specified level.
    Args:
        level (int): Logging level (e.g., logging.INFO).
        message (str): Message to log.
    """
    logger.log(level, message)