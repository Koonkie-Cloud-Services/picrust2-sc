#!/usr/bin/env python

import logging
import os
import tempfile
import unittest

"""
Test suite for PICRUSt2 logger module.
"""


from picrust2.logger import (
    PicrustLogger,
    PicrustError,
    get_picrust_logger,
    setup_logging,
    log_and_raise,
    get_log_file_path,
)


class TestPicrustLogger(unittest.TestCase):
    """Test cases for PicrustLogger class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_file = os.path.join(self.temp_dir.name, "test.log")

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()
        # Clear handlers to avoid interference between tests
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

    def test_picrust_logger_instantiation(self):
        """Test PicrustLogger can be instantiated."""
        logger = PicrustLogger("test_logger")
        self.assertIsNotNone(logger.logger)
        self.assertEqual(logger.logger.name, "test_logger")

    def test_picrust_logger_default_level(self):
        """Test PicrustLogger has correct default logging level."""
        logger = PicrustLogger("test_logger")
        self.assertEqual(logger.logger.level, logging.INFO)

    def test_picrust_logger_custom_level(self):
        """Test PicrustLogger respects custom logging level."""
        logger = PicrustLogger("test_logger", level=logging.DEBUG)
        self.assertEqual(logger.logger.level, logging.DEBUG)

    def test_picrust_logger_has_handlers(self):
        """Test PicrustLogger sets up console handler."""
        logger = PicrustLogger("test_logger_handlers")
        self.assertGreater(len(logger.logger.handlers), 0)

    def test_add_file_handler(self):
        """Test file handler can be added to logger."""
        logger = PicrustLogger("test_logger_file")
        logger.add_file_handler(self.log_file)
        self.assertTrue(
            any(isinstance(h, logging.FileHandler) for h in logger.logger.handlers)
        )

    def test_file_handler_creates_log_file(self):
        """Test that file handler actually creates and writes to log file."""
        logger = PicrustLogger("test_logger_write")
        logger.add_file_handler(self.log_file)

        logger.logger.info("Test log message")

        self.assertTrue(os.path.exists(self.log_file))
        with open(self.log_file, "r") as f:
            content = f.read()
            self.assertIn("Test log message", content)

    def test_set_logging_level(self):
        """Test setting logging level."""
        logger = PicrustLogger("test_logger_level", level=logging.INFO)
        logger.set_level(logging.DEBUG)
        self.assertEqual(logger.logger.level, logging.DEBUG)

    def test_get_logger_method(self):
        """Test get_logger returns logger instance."""
        logger = PicrustLogger("test_logger_get")
        retrieved_logger = logger.get_logger()
        self.assertIs(retrieved_logger, logger.logger)

    def test_no_duplicate_handlers(self):
        """Test that instantiating same logger doesn't create duplicate handlers."""
        logger1 = PicrustLogger("test_duplicate")
        handler_count_1 = len(logger1.logger.handlers)

        logger2 = PicrustLogger("test_duplicate")
        handler_count_2 = len(logger2.logger.handlers)

        self.assertEqual(handler_count_1, handler_count_2)


class TestGetPicrustLogger(unittest.TestCase):
    """Test cases for get_picrust_logger function."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_file = os.path.join(self.temp_dir.name, "test.log")

        # Create a logger with a file handler for testing using default parameters
        self.picrust_logger = setup_logging(
            log_file=self.log_file
        )

    def tearDown(self):
        """Clean up handlers after tests."""
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        self.temp_dir.cleanup()

    def test_get_picrust_logger_returns_logger(self):
        """Test get_picrust_logger returns a logger instance."""
        log_file_path = os.path.join(self.temp_dir.name, "test_module.log")
        logger = get_picrust_logger(
            "test_module",
            level=logging.WARNING,
            log_file_level=logging.DEBUG,
            log_file=log_file_path,
        )
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test_module")
        self.assertEqual(logger.level, logging.WARNING, "Expected logger to have WARNING level")

        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                self.assertEqual(handler.baseFilename, log_file_path)
                self.assertEqual(handler.level, logging.DEBUG, "Expected file handler to have DEBUG level")
            elif isinstance(handler, logging.StreamHandler):
                self.assertEqual(handler.level, logging.INFO, "Expected stream handler to have INFO level")
            else:
                self.fail("Unexpected handler type found in logger handlers")

    def test_get_picrust_logger_with_verbose_level(self):
        """Test get_picrust_logger respects custom level."""
        logger = get_picrust_logger("test_module_info", verbose=True)
        self.assertEqual(logger.level, logging.INFO, "Expected logger to have INFO level when verbose=True")
        self.assertEqual(logger.name, "test_module_info")
        self.assertEqual(
            1, len(logger.handlers), "Expected one stream handler for the logger"
        )
        self.assertEqual(logger.handlers[0].level, logging.INFO)

    def test_get_picrust_logger(self):
        logger = get_picrust_logger()
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.level, logging.WARNING, "Expected logger to have WARNING level")
        self.assertEqual(logger.name, "picrust2")

        # Check that the file handler is correct
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                self.assertEqual(handler.baseFilename, self.log_file)
                self.assertEqual(handler.level, logging.DEBUG, "Expected file handler to have DEBUG level")
                break


class TestSetupLogging(unittest.TestCase):
    """Test cases for setup_logging function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

    def test_setup_logging_default(self):
        """Test setup_logging with default parameters."""
        logger = setup_logging()
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.level, logging.WARNING)

    def test_setup_logging_verbose(self):
        """Test setup_logging with verbose flag."""
        logger = setup_logging(verbose=True)
        self.assertEqual(logger.level, logging.INFO)

    def test_setup_logging_debug(self):
        """Test setup_logging with debug flag."""
        logger = setup_logging(debug=True)
        self.assertEqual(logger.level, logging.DEBUG)

    def test_setup_logging_with_logfile(self):
        """Test setup_logging creates log file."""
        log_file = os.path.join(self.temp_dir.name, "test_setup.log")
        logger = setup_logging(
            log_file=log_file, debug=True, log_file_level=logging.DEBUG
        )
        logger.info("Test info message")
        logger.debug("Test debug message")

        self.assertTrue(
            any(isinstance(h, logging.FileHandler) for h in logger.handlers)
        )
        self.assertTrue(os.path.exists(log_file))
        with open(log_file, "r") as f:
            content = f.read()
            self.assertIn("Test debug message", content)

        return


class TestLogAndRaise(unittest.TestCase):
    """Test cases for log_and_raise function."""

    def test_log_and_raise_default_exception(self):
        """Test log_and_raise raises PicrustError by default."""
        logger = get_picrust_logger("test_error")
        with self.assertRaises(PicrustError):
            log_and_raise(logger, "Test error message")

    def test_log_and_raise_custom_exception(self):
        """Test log_and_raise with custom exception class."""
        logger = get_picrust_logger("test_custom_error")
        with self.assertRaises(ValueError):
            log_and_raise(logger, "Test error", exception_class=ValueError)


class TestGetLogFilePath(unittest.TestCase):
    """Test cases for get_log_file_path function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()

    def test_get_log_file_path_default(self):
        """Test get_log_file_path with default filename."""
        output_dir = self.temp_dir.name
        log_path = get_log_file_path(output_dir)
        expected = os.path.join(output_dir, "picrust2.log")
        self.assertEqual(log_path, expected)

    def test_get_log_file_path_custom_filename(self):
        """Test get_log_file_path with custom filename."""
        output_dir = self.temp_dir.name
        test_log_filename = "custom.log"

        log_path = get_log_file_path(output_dir, log_filename=test_log_filename)
        self.assertEqual(log_path, os.path.join(output_dir, test_log_filename))

    def test_get_log_file_path_creates_directory(self):
        """Test get_log_file_path creates output directory if missing."""
        nested_dir = os.path.join(self.temp_dir.name, "nested", "path")
        log_path = get_log_file_path(nested_dir)
        self.assertTrue(os.path.exists(os.path.dirname(log_path)))

    def test_get_log_file_path_custom_default(self):
        """Test get_log_file_path with custom default filename."""
        output_dir = self.temp_dir.name
        log_path = get_log_file_path(output_dir, default_filename="custom_default.log")
        expected = os.path.join(output_dir, "custom_default.log")
        self.assertEqual(log_path, expected)


class TestPicrustError(unittest.TestCase):
    """Test cases for PicrustError exception."""

    def test_picrust_error_is_exception(self):
        """Test PicrustError is an Exception subclass."""
        self.assertTrue(issubclass(PicrustError, Exception))

    def test_picrust_error_can_be_raised(self):
        """Test PicrustError can be raised and caught."""
        with self.assertRaises(PicrustError):
            raise PicrustError("Test error")


if __name__ == "__main__":
    unittest.main()
