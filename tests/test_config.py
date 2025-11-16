#!/usr/bin/env python
"""
Unit tests for the config module.

Tests that all configuration constants are properly defined and have valid values.
"""

import os
import sys
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from m8_kitcreator import config


class TestUIConfiguration(unittest.TestCase):
    """Test UI configuration constants."""

    def test_window_dimensions(self):
        """Test window size constants are valid."""
        self.assertIsInstance(config.WINDOW_WIDTH, int)
        self.assertIsInstance(config.WINDOW_HEIGHT, int)
        self.assertGreater(config.WINDOW_WIDTH, 0)
        self.assertGreater(config.WINDOW_HEIGHT, 0)

    def test_window_geometry(self):
        """Test window geometry string format."""
        self.assertIsInstance(config.WINDOW_GEOMETRY, str)
        self.assertIn('x', config.WINDOW_GEOMETRY)
        # Should be in format "WIDTHxHEIGHT"
        parts = config.WINDOW_GEOMETRY.split('x')
        self.assertEqual(len(parts), 2)
        self.assertEqual(int(parts[0]), config.WINDOW_WIDTH)
        self.assertEqual(int(parts[1]), config.WINDOW_HEIGHT)

    def test_window_title(self):
        """Test window title is defined."""
        self.assertIsInstance(config.WINDOW_TITLE, str)
        self.assertGreater(len(config.WINDOW_TITLE), 0)

    def test_font_configuration(self):
        """Test font configurations are tuples."""
        fonts = [
            config.TITLE_FONT,
            config.SUBTITLE_FONT,
            config.LABEL_FONT,
            config.STATUS_LABEL_FONT
        ]
        for font in fonts:
            self.assertIsInstance(font, tuple)
            self.assertEqual(len(font), 2)
            self.assertIsInstance(font[0], str)  # Font name
            self.assertIsInstance(font[1], int)  # Font size
            self.assertGreater(font[1], 0)

    def test_padding_values(self):
        """Test padding values are valid."""
        padding_values = [
            config.FRAME_PADDING_Y,
            config.FRAME_PADDING_X,
            config.BUTTON_PADDING_X,
            config.BUTTON_PADDING_Y
        ]
        for padding in padding_values:
            self.assertIsInstance(padding, int)
            self.assertGreaterEqual(padding, 0)

    def test_progress_bar_dimensions(self):
        """Test progress bar dimensions are valid."""
        self.assertIsInstance(config.PROGRESS_BAR_WIDTH, int)
        self.assertIsInstance(config.PROGRESS_BAR_HEIGHT, int)
        self.assertGreater(config.PROGRESS_BAR_WIDTH, 0)
        self.assertGreater(config.PROGRESS_BAR_HEIGHT, 0)


class TestAudioProcessingConfiguration(unittest.TestCase):
    """Test audio processing configuration constants."""

    def test_marker_duration(self):
        """Test marker duration is valid."""
        self.assertIsInstance(config.DEFAULT_MARKER_DURATION_MS, int)
        self.assertGreater(config.DEFAULT_MARKER_DURATION_MS, 0)

    def test_silence_threshold(self):
        """Test silence threshold is valid."""
        self.assertIsInstance(config.DEFAULT_SILENCE_THRESHOLD, (int, float))
        # Silence threshold should be negative (in dBFS)
        self.assertLess(config.DEFAULT_SILENCE_THRESHOLD, 0)

    def test_silence_lengths(self):
        """Test silence length parameters are valid."""
        self.assertIsInstance(config.DEFAULT_MIN_SILENCE_LEN, int)
        self.assertIsInstance(config.DEFAULT_RETAINED_SILENCE, int)
        self.assertGreater(config.DEFAULT_MIN_SILENCE_LEN, 0)
        self.assertGreater(config.DEFAULT_RETAINED_SILENCE, 0)

    def test_channel_limits(self):
        """Test channel count limits are valid."""
        self.assertIsInstance(config.MIN_CHANNELS, int)
        self.assertIsInstance(config.MAX_CHANNELS, int)
        self.assertGreater(config.MIN_CHANNELS, 0)
        self.assertGreater(config.MAX_CHANNELS, config.MIN_CHANNELS)

    def test_sample_width_limits(self):
        """Test sample width limits are valid."""
        self.assertIsInstance(config.MIN_SAMPLE_WIDTH, int)
        self.assertIsInstance(config.MAX_SAMPLE_WIDTH, int)
        self.assertGreater(config.MIN_SAMPLE_WIDTH, 0)
        self.assertGreater(config.MAX_SAMPLE_WIDTH, config.MIN_SAMPLE_WIDTH)

    def test_sample_rate_limits(self):
        """Test sample rate limits are valid."""
        self.assertIsInstance(config.MIN_SAMPLE_RATE, int)
        self.assertIsInstance(config.MAX_SAMPLE_RATE, int)
        self.assertGreater(config.MIN_SAMPLE_RATE, 0)
        self.assertGreater(config.MAX_SAMPLE_RATE, config.MIN_SAMPLE_RATE)


class TestFileHandlingConfiguration(unittest.TestCase):
    """Test file handling configuration constants."""

    def test_wav_extension(self):
        """Test WAV extension is properly formatted."""
        self.assertIsInstance(config.WAV_EXTENSION, str)
        self.assertTrue(config.WAV_EXTENSION.startswith('.'))
        self.assertEqual(config.WAV_EXTENSION.lower(), '.wav')

    def test_wav_file_types(self):
        """Test WAV file types tuple is valid."""
        self.assertIsInstance(config.WAV_FILE_TYPES, list)
        self.assertGreater(len(config.WAV_FILE_TYPES), 0)

        # Each entry should be a tuple of (description, pattern)
        for entry in config.WAV_FILE_TYPES:
            self.assertIsInstance(entry, tuple)
            self.assertEqual(len(entry), 2)
            self.assertIsInstance(entry[0], str)  # Description
            self.assertIsInstance(entry[1], str)  # Pattern


class TestOutputFormatConfiguration(unittest.TestCase):
    """Test output format configuration constants."""

    def test_output_format_constants(self):
        """Test output format constants are defined."""
        formats = [
            config.OUTPUT_FORMAT_M8,
            config.OUTPUT_FORMAT_OCTATRACK,
            config.OUTPUT_FORMAT_BOTH
        ]
        for fmt in formats:
            self.assertIsInstance(fmt, str)
            self.assertGreater(len(fmt), 0)

    def test_default_output_format(self):
        """Test default output format is valid."""
        self.assertIsInstance(config.DEFAULT_OUTPUT_FORMAT, str)
        # Should be one of the defined formats
        self.assertIn(config.DEFAULT_OUTPUT_FORMAT, [
            config.OUTPUT_FORMAT_M8,
            config.OUTPUT_FORMAT_OCTATRACK,
            config.OUTPUT_FORMAT_BOTH
        ])


class TestMessageConfiguration(unittest.TestCase):
    """Test message text configuration constants."""

    def test_status_messages(self):
        """Test status messages are defined."""
        messages = [
            config.STATUS_READY,
            config.STATUS_PROCESSING
        ]
        for msg in messages:
            self.assertIsInstance(msg, str)
            self.assertGreater(len(msg), 0)

    def test_dialog_titles(self):
        """Test dialog titles are defined."""
        titles = [
            config.DIALOG_SELECT_FILES,
            config.DIALOG_SAVE_OUTPUT
        ]
        for title in titles:
            self.assertIsInstance(title, str)
            self.assertGreater(len(title), 0)

    def test_message_titles(self):
        """Test message box titles are defined."""
        titles = [
            config.MSG_SUCCESS_TITLE,
            config.MSG_NO_FILES_TITLE,
            config.MSG_PERMISSION_DENIED_TITLE
        ]
        for title in titles:
            self.assertIsInstance(title, str)
            self.assertGreater(len(title), 0)

    def test_error_messages(self):
        """Test error message templates are defined."""
        errors = [
            config.ERROR_NOT_WAV,
            config.ERROR_FILE_NOT_FOUND,
            config.ERROR_FILE_EMPTY,
            config.ERROR_PERMISSION_DENIED,
        ]
        for error in errors:
            self.assertIsInstance(error, str)
            self.assertGreater(len(error), 0)

    def test_format_string_errors(self):
        """Test error messages with format placeholders."""
        format_errors = [
            (config.ERROR_INVALID_CHANNELS, 2),
            (config.ERROR_INVALID_SAMPLE_WIDTH, 2),
            (config.ERROR_INVALID_SAMPLE_RATE, 44100),
            (config.ERROR_INVALID_WAV, "test error"),
            (config.ERROR_CANNOT_READ, "test error"),
        ]
        for template, value in format_errors:
            self.assertIsInstance(template, str)
            # Should be formattable
            try:
                formatted = template.format(value)
                self.assertIsInstance(formatted, str)
            except (KeyError, IndexError) as e:
                self.fail(f"Error message template failed to format: {template}")


class TestConfigurationConsistency(unittest.TestCase):
    """Test configuration values are consistent with each other."""

    def test_window_size_reasonable(self):
        """Test window size is reasonable for desktop use."""
        self.assertLess(config.WINDOW_WIDTH, 2000)
        self.assertLess(config.WINDOW_HEIGHT, 2000)
        self.assertGreater(config.WINDOW_WIDTH, 100)
        self.assertGreater(config.WINDOW_HEIGHT, 100)

    def test_progress_bar_fits_window(self):
        """Test progress bar width fits in window."""
        self.assertLess(config.PROGRESS_BAR_WIDTH, config.WINDOW_WIDTH)

    def test_sample_rate_ranges_realistic(self):
        """Test sample rate ranges are realistic for audio."""
        # Typical audio sample rates range from ~8kHz to ~192kHz
        self.assertGreaterEqual(config.MIN_SAMPLE_RATE, 8000)
        self.assertLessEqual(config.MAX_SAMPLE_RATE, 200000)

    def test_channel_count_realistic(self):
        """Test channel count limits are realistic."""
        # Most audio is 1-8 channels
        self.assertGreaterEqual(config.MIN_CHANNELS, 1)
        self.assertLessEqual(config.MAX_CHANNELS, 8)


if __name__ == '__main__':
    unittest.main()
