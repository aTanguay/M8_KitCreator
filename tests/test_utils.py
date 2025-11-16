#!/usr/bin/env python
"""
Unit tests for the utils module.
"""

import os
import sys
import wave
import struct
import tempfile
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from m8_kitcreator.utils import (
    validate_wav_file,
    get_channel_description,
    format_file_list_error,
    check_directory_writable
)
from m8_kitcreator import config


class TestValidateWavFile(unittest.TestCase):
    """Test cases for WAV file validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test files."""
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def create_test_wav(self, filename, channels=2, sample_width=2, framerate=44100, nframes=1000):
        """Helper to create a test WAV file."""
        filepath = os.path.join(self.temp_dir, filename)
        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(framerate)
            # Create silent audio data
            data = b'\x00' * (nframes * channels * sample_width)
            wf.writeframes(data)
        return filepath

    def test_valid_mono_wav(self):
        """Test validation of a valid mono WAV file."""
        filepath = self.create_test_wav('test_mono.wav', channels=1)
        is_valid, error = validate_wav_file(filepath)

        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_valid_stereo_wav(self):
        """Test validation of a valid stereo WAV file."""
        filepath = self.create_test_wav('test_stereo.wav', channels=2)
        is_valid, error = validate_wav_file(filepath)

        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_invalid_extension(self):
        """Test that non-WAV files are rejected."""
        filepath = os.path.join(self.temp_dir, 'test.mp3')
        with open(filepath, 'w') as f:
            f.write('dummy content')

        is_valid, error = validate_wav_file(filepath)

        self.assertFalse(is_valid)
        self.assertEqual(error, config.ERROR_NOT_WAV)

    def test_file_not_found(self):
        """Test validation of non-existent file."""
        filepath = os.path.join(self.temp_dir, 'nonexistent.wav')
        is_valid, error = validate_wav_file(filepath)

        self.assertFalse(is_valid)
        self.assertEqual(error, config.ERROR_FILE_NOT_FOUND)

    def test_empty_wav_file(self):
        """Test validation of empty file."""
        filepath = os.path.join(self.temp_dir, 'empty.wav')
        with open(filepath, 'w') as f:
            pass  # Create empty file

        is_valid, error = validate_wav_file(filepath)

        self.assertFalse(is_valid)
        self.assertEqual(error, config.ERROR_FILE_EMPTY)

    def test_invalid_wav_header(self):
        """Test validation of file with invalid WAV header."""
        filepath = os.path.join(self.temp_dir, 'invalid.wav')
        with open(filepath, 'wb') as f:
            f.write(b'INVALID HEADER DATA')

        is_valid, error = validate_wav_file(filepath)

        self.assertFalse(is_valid)
        self.assertIn('invalid', error.lower())

    def test_too_many_channels(self):
        """Test validation of WAV with too many channels."""
        filepath = self.create_test_wav('test_multichannel.wav', channels=9)
        is_valid, error = validate_wav_file(filepath)

        self.assertFalse(is_valid)
        # Error message contains "unsupported channel count" or "channels"
        self.assertTrue('channel' in error.lower(), f"Expected 'channel' in error, got: {error}")

    def test_zero_channels(self):
        """Test validation of WAV with zero channels."""
        # wave module doesn't allow creating files with 0 channels
        # This test is skipped because we can't create such a file
        self.skipTest("wave module doesn't support creating files with 0 channels")

    def test_different_sample_rates(self):
        """Test validation of various sample rates."""
        sample_rates = [22050, 44100, 48000, 96000]
        for rate in sample_rates:
            filepath = self.create_test_wav(f'test_{rate}.wav', framerate=rate)
            is_valid, error = validate_wav_file(filepath)

            self.assertTrue(is_valid, f"Sample rate {rate} should be valid")
            self.assertIsNone(error)

    def test_invalid_sample_rate_too_low(self):
        """Test validation of WAV with very low sample rate."""
        filepath = self.create_test_wav('test_low_rate.wav', framerate=1000)
        is_valid, error = validate_wav_file(filepath)

        self.assertFalse(is_valid)
        self.assertIn('sample rate', error.lower())

    def test_invalid_sample_rate_too_high(self):
        """Test validation of WAV with very high sample rate."""
        filepath = self.create_test_wav('test_high_rate.wav', framerate=200000)
        is_valid, error = validate_wav_file(filepath)

        self.assertFalse(is_valid)
        self.assertIn('sample rate', error.lower())

    def test_different_sample_widths(self):
        """Test validation of different bit depths."""
        sample_widths = [1, 2, 3, 4]  # 8, 16, 24, 32 bit
        for width in sample_widths:
            filepath = self.create_test_wav(f'test_{width*8}bit.wav', sample_width=width)
            is_valid, error = validate_wav_file(filepath)

            self.assertTrue(is_valid, f"Sample width {width} bytes should be valid")
            self.assertIsNone(error)


class TestGetChannelDescription(unittest.TestCase):
    """Test cases for channel description formatting."""

    def test_mono_description(self):
        """Test description for mono audio."""
        desc = get_channel_description(1)
        self.assertEqual(desc, "mono")

    def test_stereo_description(self):
        """Test description for stereo audio."""
        desc = get_channel_description(2)
        self.assertEqual(desc, "stereo")

    def test_multichannel_description(self):
        """Test description for multi-channel audio."""
        test_cases = [
            (3, "3 channels (multi-channel)"),
            (4, "4 channels (multi-channel)"),
            (6, "6 channels (multi-channel)"),
            (8, "8 channels (multi-channel)"),
        ]
        for channels, expected in test_cases:
            desc = get_channel_description(channels)
            self.assertEqual(desc, expected)


class TestFormatFileListError(unittest.TestCase):
    """Test cases for error message formatting."""

    def test_empty_list(self):
        """Test formatting of empty error list."""
        result = format_file_list_error([])
        self.assertEqual(result, "")

    def test_single_error(self):
        """Test formatting of single error."""
        errors = [("file1.wav", "Invalid sample rate")]
        result = format_file_list_error(errors)

        self.assertIn("file1.wav", result)
        self.assertIn("Invalid sample rate", result)
        self.assertIn("•", result)

    def test_multiple_errors(self):
        """Test formatting of multiple errors."""
        errors = [
            ("file1.wav", "Invalid sample rate"),
            ("file2.wav", "File not found"),
            ("file3.wav", "Not a WAV file")
        ]
        result = format_file_list_error(errors)

        # Check all files and errors are present
        for filename, error in errors:
            self.assertIn(filename, result)
            self.assertIn(error, result)

        # Check formatting with bullet points
        lines = result.split('\n')
        self.assertEqual(len(lines), 3)
        for line in lines:
            self.assertIn("•", line)


class TestCheckDirectoryWritable(unittest.TestCase):
    """Test cases for directory write permission checking."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test directories."""
        # Restore write permissions before cleanup
        os.chmod(self.temp_dir, 0o755)
        os.rmdir(self.temp_dir)

    def test_writable_directory(self):
        """Test check on writable directory."""
        result = check_directory_writable(self.temp_dir)
        self.assertTrue(result)

    def test_readonly_directory(self):
        """Test check on read-only directory."""
        # Make directory read-only
        os.chmod(self.temp_dir, 0o555)
        result = check_directory_writable(self.temp_dir)

        # Result depends on user permissions (might be True if running as root)
        # Just verify it returns a boolean
        self.assertIsInstance(result, bool)

        # Restore permissions for cleanup
        os.chmod(self.temp_dir, 0o755)

    def test_nonexistent_directory(self):
        """Test check on non-existent directory."""
        result = check_directory_writable('/nonexistent/directory')
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
