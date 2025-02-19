import logging


def get_main_logger() -> logging.Logger:
    return logging.getLogger("django")
