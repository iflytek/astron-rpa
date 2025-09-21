import logging
import os
from logging.handlers import RotatingFileHandler

from app.config import get_settings
from app.middlewares.tracing import RequestIdFilter

LOG_LEVEL = get_settings().LOG_LEVEL


def get_logger(name=None, log_level=LOG_LEVEL):
    logger = logging.getLogger(name or __name__)

    if logger.handlers:
        return logger

    logger.setLevel(log_level)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - [%(request_id)s] - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    filter = RequestIdFilter()

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(filter)
    logger.addHandler(console_handler)

    log_dir = get_settings().LOG_DIR
    os.makedirs(log_dir, exist_ok=True)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=10,
    )
    file_handler.setFormatter(formatter)
    file_handler.addFilter(filter)
    logger.addHandler(file_handler)

    return logger
