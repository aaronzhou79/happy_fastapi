#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import inspect
import logging
import os

from sys import stderr, stdout

from asgi_correlation_id import correlation_id
from loguru import logger

from src.core import path_conf
from src.core.conf import settings


class InterceptHandler(logging.Handler):
    """
    默认处理程序，来自loguru文档中的示例。

    参见https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord) -> None:
        """
        发出日志记录
        """
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging() -> None:
    """
    设置日志

    From https://pawamoy.github.io/posts/unify-logging-for-a-gunicorn-uvicorn-app/
    https://github.com/pawamoy/pawamoy.github.io/issues/17
    """
    # Intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    log_root_level = settings.LOG_ROOT_LEVEL or "NOTSET"
    logging.root.setLevel(log_root_level)

    # Remove all log handlers and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        if 'uvicorn.access' in name or 'watchfiles.main' in name:
            logging.getLogger(name).propagate = False
        else:
            logging.getLogger(name).propagate = True

        # Debug log handlers
        # logging.debug(f'{logging.getLogger(name)}, {logging.getLogger(name).propagate}')

    # Remove every other logger's handlers
    logger.remove()

    # 定义correlation_id过滤函数
    # https://github.com/snok/asgi-correlation-id?tab=readme-ov-file#configure-logging
    # https://github.com/snok/asgi-correlation-id/issues/7
    def correlation_id_filter(record: dict) -> bool:
        """设置correlation_id和trace_id"""
        current_id = correlation_id.get()
        cid = str(current_id) if current_id is not None else settings.LOG_CID_DEFAULT_VALUE
        record['correlation_id'] = cid[: settings.LOG_CID_UUID_LENGTH]   # type: ignore

        return True

    # 配置loguru日志记录器，在开始记录日志之前
    logger.configure(
        handlers=[
            {
                'sink': stdout,
                'level': settings.LOG_STDOUT_LEVEL,
                'filter': lambda record: correlation_id_filter(record) and record['level'].no <= 25,  # type: ignore
                'format': settings.LOG_STD_FORMAT,
            },
            {
                'sink': stderr,
                'level': settings.LOG_STDERR_LEVEL,
                'filter': lambda record: correlation_id_filter(record) and record['level'].no >= 30,  # type: ignore
                'format': settings.LOG_STD_FORMAT,
            },
        ]
    )


def set_customize_logfile() -> None:
    """设置自定义日志文件"""
    log_path = path_conf.LOG_DIR
    if not os.path.exists(log_path):
        os.mkdir(log_path)

    # log files
    log_stdout_file = os.path.join(log_path, settings.LOG_STDOUT_FILENAME or '')
    log_stderr_file = os.path.join(log_path, settings.LOG_STDERR_FILENAME or '')

    # loguru logger: https://loguru.readthedocs.io/en/stable/api/logger.html#loguru._logger.Logger.add
    log_config = {
        'rotation': '10 MB',
        'retention': '15 days',
        'compression': 'tar.gz',
        'enqueue': True,
        'format': settings.LOG_LOGURU_FORMAT,
    }

    # stdout file
    logger.add(
        str(log_stdout_file),
        level=settings.LOG_STDOUT_LEVEL,
        **log_config,
        backtrace=False,
        diagnose=False,
    )

    # stderr file
    logger.add(
        str(log_stderr_file),
        level=settings.LOG_STDERR_LEVEL,
        **log_config,
        backtrace=True,
        diagnose=True,
    )


log = logger
