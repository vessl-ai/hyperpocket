import logging
import os
import pathlib
from logging.handlers import RotatingFileHandler
from pathlib import Path

import hyperpocket
from hyperpocket.config.settings import config


class ColorFormatter(logging.Formatter):
    """Custom formatter to add colors based on log level."""

    # ANSI escape codes for text colors
    LEVEL_COLORS = {
        logging.DEBUG: "\033[36m",  # Cyan
        logging.INFO: "\033[32m",  # Green
        logging.WARNING: "\033[33m",  # Yellow
        logging.ERROR: "\033[31m",  # Red
        logging.CRITICAL: "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        log_color = self.LEVEL_COLORS.get(record.levelno, self.RESET)
        message = super().format(record)
        return f"{log_color}{message}{self.RESET}"


def get_logger():
    log_dir = pathlib.Path(os.getcwd()) / ".log"
    os.makedirs(log_dir, exist_ok=True)
    log_file = log_dir / "pocket.log"
    if not log_file.exists():
        print(f"created log file in {log_file}")
        with open(log_file, "w"):
            pass

    # set log level
    log_level = logging.INFO
    logger = logging.getLogger("pocket_logger")
    if config().log_level.lower() == "debug":
        log_level = logging.DEBUG
    elif config().log_level.lower() == "info":
        log_level = logging.INFO
    elif config().log_level.lower() == "warning":
        log_level = logging.WARNING
    elif config().log_level.lower() == "error":
        log_level = logging.ERROR
    elif config().log_level.lower() == "critical":
        log_level = logging.CRITICAL
    elif config().log_level.lower() == "fatal":
        log_level = logging.FATAL

    # set formatter
    logger.setLevel(log_level)
    color_formatter = ColorFormatter(
        "[%(asctime)s] [%(levelname)s] [%(processName)s(%(process)d):%(threadName)s(%(thread)d)] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(processName)s(%(process)d):%(threadName)s(%(thread)d)] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # add console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)  # 콘솔 출력 레벨 설정
    console_handler.setFormatter(color_formatter)
    logger.addHandler(console_handler)

    # add rotating file handler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=100,  # 파일 크기 5MB, 백업 파일 3개
    )
    file_handler.setLevel(logging.DEBUG)  # 파일 출력 레벨 설정
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


pocket_logger = get_logger()
