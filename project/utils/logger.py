from loguru import logger
from pathlib import Path


class Logger:
    log_dir = Path("logs")
    log_file = log_dir / "app.log"
    logger_configured = False

    @staticmethod
    def _configure_logger():
        if Logger.logger_configured:
            return

        Logger.log_dir.mkdir(exist_ok=True)

        logger.add(
            Logger.log_file,
            format="{time} | {level} | {file}:{line} | {message}",
            level="DEBUG",
            rotation="900MB",
            retention="10 days",
            enqueue=True,
            backtrace=True
        )

        Logger.logger_configured = True

    @staticmethod
    def info(msg):
        Logger._configure_logger()
        logger.opt(depth=1).info(msg)

    @staticmethod
    def debug(msg):
        Logger._configure_logger()
        logger.opt(depth=1).debug(msg)

    @staticmethod
    def warning(msg):
        Logger._configure_logger()
        logger.opt(depth=1).warning(msg)

    @staticmethod
    def error(msg):
        Logger._configure_logger()
        logger.opt(depth=1).error(msg)

    @staticmethod
    def exception(msg):
        Logger._configure_logger()
        logger.opt(depth=1).exception(msg)
