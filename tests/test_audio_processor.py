#!/usr/bin/env python
"""
Unit tests for the audio processor module.

These tests focus on the logic and structure without requiring
actual audio processing (which would need pydub/ffmpeg).
"""

import os
import sys
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from m8_kitcreator import config


class TestAudioProcessorInit(unittest.TestCase):
    """Test AudioProcessor initialization."""

    def test_import(self):
        """Test that AudioProcessor can be imported."""
        try:
            # Import without actually using (to avoid tkinter dependency)
            from m8_kitcreator.audio_processor import AudioProcessor
            self.assertTrue(True)
        except ImportError as e:
            # If import fails due to missing optional dependencies, that's OK
            if 'tkinter' in str(e) or 'pydub' in str(e):
                self.skipTest(f"Optional dependency not available: {e}")
            else:
                raise

    def test_class_exists(self):
        """Test that AudioProcessor class exists and can be instantiated."""
        try:
            from m8_kitcreator.audio_processor import AudioProcessor

            # Test with default parameters
            processor = AudioProcessor()
            self.assertIsNotNone(processor)

            # Test with custom parameters
            processor = AudioProcessor(
                marker_duration_ms=2,
                silence_thresh=-40.0,
                min_silence_len=20,
                retained_silence=2,
                force_mono=True
            )
            self.assertIsNotNone(processor)
            self.assertEqual(processor.marker_duration_ms, 2)
            self.assertEqual(processor.silence_thresh, -40.0)
            self.assertEqual(processor.min_silence_len, 20)
            self.assertEqual(processor.retained_silence, 2)
            self.assertTrue(processor.force_mono)

        except ImportError as e:
            if 'tkinter' in str(e) or 'pydub' in str(e):
                self.skipTest(f"Optional dependency not available: {e}")
            else:
                raise

    def test_default_parameters(self):
        """Test that default parameters match config values."""
        try:
            from m8_kitcreator.audio_processor import AudioProcessor

            processor = AudioProcessor()

            self.assertEqual(processor.marker_duration_ms, config.DEFAULT_MARKER_DURATION_MS)
            self.assertEqual(processor.silence_thresh, config.DEFAULT_SILENCE_THRESHOLD)
            self.assertEqual(processor.min_silence_len, config.DEFAULT_MIN_SILENCE_LEN)
            self.assertEqual(processor.retained_silence, config.DEFAULT_RETAINED_SILENCE)
            self.assertFalse(processor.force_mono)

        except ImportError as e:
            if 'tkinter' in str(e) or 'pydub' in str(e):
                self.skipTest(f"Optional dependency not available: {e}")
            else:
                raise

    def test_methods_exist(self):
        """Test that expected methods exist on AudioProcessor."""
        try:
            from m8_kitcreator.audio_processor import AudioProcessor

            processor = AudioProcessor()

            # Check public method exists
            self.assertTrue(hasattr(processor, 'concatenate_audio_files'))
            self.assertTrue(callable(processor.concatenate_audio_files))

            # Check private methods exist
            for method in ['concatenate_audio_files', '_process_silence',
                      '_calculate_frame_position', '_export_audio',
                      '_add_cue_points', '_generate_ot_file',
                      '_log_success_message']:
                self.assertTrue(hasattr(processor, method), f"Method {method} not found")
                self.assertTrue(callable(getattr(processor, method)), f"Method {method} not callable")

        except ImportError as e:
            if 'tkinter' in str(e) or 'pydub' in str(e):
                self.skipTest(f"Optional dependency not available: {e}")
            else:
                raise


class TestAudioProcessorSignatures(unittest.TestCase):
    """Test method signatures and parameter handling."""

    def test_concatenate_signature(self):
        """Test concatenate_audio_files method signature."""
        try:
            from m8_kitcreator.audio_processor import AudioProcessor
            import inspect

            processor = AudioProcessor()
            sig = inspect.signature(processor.concatenate_audio_files)

            # Check expected parameters exist
            params = list(sig.parameters.keys())
            self.assertIn('file_paths', params)
            self.assertIn('output_file', params)
            self.assertIn('progress_callback', params)
            self.assertIn('output_format', params)

            # Check defaults
            self.assertIsNone(sig.parameters['progress_callback'].default)
            self.assertIsNone(sig.parameters['output_format'].default)

        except ImportError as e:
            if 'tkinter' in str(e) or 'pydub' in str(e):
                self.skipTest(f"Optional dependency not available: {e}")
            else:
                raise


class TestModuleStructure(unittest.TestCase):
    """Test module structure and dependencies."""

    def test_module_imports(self):
        """Test that required modules are imported."""
        try:
            import m8_kitcreator.audio_processor as ap

            # Check expected imports
            self.assertTrue(hasattr(ap, 'os'))
            self.assertTrue(hasattr(ap, 'struct'))
            self.assertTrue(hasattr(ap, 'wave'))
            self.assertTrue(hasattr(ap, 'AudioSegment'))
            self.assertTrue(hasattr(ap, 'split_on_silence'))
            self.assertTrue(hasattr(ap, 'config'))
            self.assertTrue(hasattr(ap, 'OctatrackWriter'))

        except ImportError as e:
            if 'tkinter' in str(e) or 'pydub' in str(e):
                self.skipTest(f"Optional dependency not available: {e}")
            else:
                raise

    def test_ffmpeg_configuration(self):
        """Test that static-ffmpeg configuration is attempted."""
        # This just ensures the configuration block runs without error
        try:
            import m8_kitcreator.audio_processor
            # If we get here, the module loaded successfully
            self.assertTrue(True)
        except ImportError as e:
            if 'tkinter' in str(e) or 'pydub' in str(e) or 'staticffmpeg' in str(e):
                self.skipTest(f"Optional dependency not available: {e}")
            else:
                raise


class TestAudioProcessorDocumentation(unittest.TestCase):
    """Test that methods have proper documentation."""

    def test_class_docstring(self):
        """Test that AudioProcessor has a docstring."""
        try:
            from m8_kitcreator.audio_processor import AudioProcessor

            self.assertIsNotNone(AudioProcessor.__doc__)
            self.assertGreater(len(AudioProcessor.__doc__), 0)

        except ImportError as e:
            if 'tkinter' in str(e) or 'pydub' in str(e):
                self.skipTest(f"Optional dependency not available: {e}")
            else:
                raise

    def test_method_docstrings(self):
        """Test that public methods have docstrings."""
        try:
            from m8_kitcreator.audio_processor import AudioProcessor

            processor = AudioProcessor()

            # Check public method has docstring
            self.assertIsNotNone(processor.concatenate_audio_files.__doc__)
            self.assertGreater(len(processor.concatenate_audio_files.__doc__), 0)

        except ImportError as e:
            if 'tkinter' in str(e) or 'pydub' in str(e):
                self.skipTest(f"Optional dependency not available: {e}")
            else:
                raise


if __name__ == '__main__':
    unittest.main()
