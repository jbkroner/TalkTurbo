import logging
from logging.handlers import RotatingFileHandler


class LoggerGenerator:
    @staticmethod
    def create_logger(
        logger_name,
        log_level=logging.INFO,
        log_format="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s",
        filename="discord.log",
        max_bytes=10 * 1024 * 1024,
        backup_count=5,
    ):
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)

        console_handler = logging.StreamHandler()
        file_handler = RotatingFileHandler(
            filename=filename,
            encoding="utf-8",
            mode="w",
            maxBytes=max_bytes,
            backupCount=backup_count,
        )

        formatter = logging.Formatter(log_format)
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.info(f"Logging level set to {log_level}")

        return logger
