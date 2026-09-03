import logging
import os
from logging.handlers import RotatingFileHandler

from app.config import get_settings
from app.middlewares.tracing import RequestIdFilter
from app.utils.sensitive_logging import SensitiveDataFilter, SensitiveFormatter

LOG_LEVEL = get_settings().LOG_LEVEL
SENSITIVE_DATA_FILTER = SensitiveDataFilter()


def _add_sensitive_filter(filter_target):
    if not any(isinstance(item, SensitiveDataFilter) for item in filter_target.filters):
        filter_target.addFilter(SENSITIVE_DATA_FILTER)


def get_logger(name=None, log_level=LOG_LEVEL):
    logger = logging.getLogger(name or __name__)

    if logger.handlers:
        return logger

    logger.setLevel(log_level)

    default_formatter = SensitiveFormatter(
        "%(asctime)s - %(name)s - [%(request_id)s] - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # uvicorn_logger = logging.getLogger("uvicorn")
    # # 一行式写法
    # uvicorn_formatter = (
    #     uvicorn_logger.handlers[0].formatter
    #     if uvicorn_logger.handlers and uvicorn_logger.handlers[0].formatter
    #     else default_formatter
    # )

    request_id_filter = RequestIdFilter()

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(default_formatter)

    console_handler.addFilter(request_id_filter)
    _add_sensitive_filter(console_handler)

    logger.addHandler(console_handler)

    log_dir = get_settings().LOG_DIR
    os.makedirs(log_dir, exist_ok=True)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=10,
    )
    file_handler.setFormatter(default_formatter)
    file_handler.addFilter(request_id_filter)
    _add_sensitive_filter(file_handler)
    logger.addHandler(file_handler)

    # Uvicorn owns its access handlers. Attach the same redactor so a legacy
    # MCP ?key= query cannot be written by the application server access log.
    for external_logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        external_logger = logging.getLogger(external_logger_name)
        _add_sensitive_filter(external_logger)
        for handler in external_logger.handlers:
            _add_sensitive_filter(handler)

    return logger
