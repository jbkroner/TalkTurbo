import unittest
import logging
import os
from TalkTurbo.LoggerGenerator import LoggerGenerator
from logging.handlers import RotatingFileHandler


@unittest.skip("Skip LoggerGenerator tests")
class TestLoggerGenerator(unittest.TestCase):
    def setUp(self):
        self.logger_name = "TestLogger"
        if self.logger_name in logging.Logger.manager.loggerDict:
            del logging.Logger.manager.loggerDict[self.logger_name]

    def test_create_logger(self):
        logger = LoggerGenerator.create_logger(logger_name="TestLogger")
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "TestLogger")
        self.assertEqual(logger.level, logging.INFO)

    def test_create_logger_with_custom_level(self):
        logger = LoggerGenerator.create_logger(
            logger_name="TestLogger", log_level=logging.DEBUG
        )
        self.assertEqual(logger.level, logging.DEBUG)

    def test_create_logger_with_custom_format(self):
        log_format = "%(asctime)s - %(levelname)s - %(message)s"
        logger = LoggerGenerator.create_logger(
            logger_name="TestLogger", log_format=log_format
        )
        console_handler = logger.handlers[0]
        self.assertEqual(console_handler.formatter._fmt, log_format)

    def test_create_logger_with_log_file(self):
        filename = "test.log"
        logger = LoggerGenerator.create_logger(
            logger_name="TestLogger", filename=filename
        )
        file_handler = logger.handlers[1]
        self.assertEqual(file_handler.baseFilename, os.path.abspath(filename))
        if os.path.exists(filename):
            os.remove(filename)

    def test_create_logger_console_handler_presence(self):
        logger = LoggerGenerator.create_logger(logger_name="TestLogger")
        console_handler_exists = any(
            isinstance(handler, logging.StreamHandler) for handler in logger.handlers
        )
        self.assertTrue(
            console_handler_exists, "Console handler not found in the logger handlers"
        )

    def test_create_logger_rotating_file_handler_presence(self):
        logger = LoggerGenerator.create_logger(logger_name="TestLogger")
        file_handler_exists = any(
            isinstance(handler, RotatingFileHandler) for handler in logger.handlers
        )
        self.assertTrue(
            file_handler_exists,
            "Rotating file handler not found in the logger handlers",
        )

    def test_create_logger_rotating_file_handler_config(self):
        max_bytes = 20 * 1024 * 1024
        backup_count = 10
        logger = LoggerGenerator.create_logger(
            logger_name="TestLogger", max_bytes=max_bytes, backup_count=backup_count
        )
        file_handler = next(
            handler
            for handler in logger.handlers
            if isinstance(handler, RotatingFileHandler)
        )

        self.assertEqual(
            file_handler.maxBytes,
            max_bytes,
            "File handler max_bytes configuration mismatch",
        )
        self.assertEqual(
            file_handler.backupCount,
            backup_count,
            "File handler backup_count configuration mismatch",
        )

    def test_create_logger_log_output(self):
        from io import StringIO

        logger_name = "TestLogger"
        log_message = "This is a test log message"
        log_output = StringIO()

        logger = LoggerGenerator.create_logger(logger_name=logger_name)
        logger.handlers[0].stream = (
            log_output  # Replace the console handler's output stream with log_output
        )
        logger.info(log_message)

        log_output.seek(0)  # Reset the log_output stream position
        log_contents = log_output.read()

        self.assertIn(logger_name, log_contents, "Logger name not found in log output")
        self.assertIn(log_message, log_contents, "Log message not found in log output")


if __name__ == "__main__":
    unittest.main()
