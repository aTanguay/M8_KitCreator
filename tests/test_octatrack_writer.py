#!/usr/bin/env python
"""
Unit tests for the Octatrack .ot file writer module.
"""

import os
import sys
import struct
import tempfile
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from m8_kitcreator.octatrack_writer import OctatrackWriter


class TestOctatrackWriter(unittest.TestCase):
    """Test cases for OctatrackWriter class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_path = os.path.join(self.temp_dir, 'test_kit.ot')

    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.output_path):
            os.remove(self.output_path)
        os.rmdir(self.temp_dir)

    def test_file_creation(self):
        """Test that .ot file is created with correct size."""
        writer = OctatrackWriter(
            output_path=self.output_path,
            sample_rate=44100,
            total_samples=44100
        )
        result = writer.write()

        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_path))
        self.assertEqual(os.path.getsize(self.output_path), 832)

    def test_header_magic(self):
        """Test that file header contains correct magic bytes."""
        writer = OctatrackWriter(
            output_path=self.output_path,
            sample_rate=44100,
            total_samples=44100
        )
        writer.write()

        with open(self.output_path, 'rb') as f:
            header = f.read(16)

        expected_header = b'FORM\x00\x00\x03,DPS1SMPA'
        self.assertEqual(header, expected_header)

    def test_tempo_encoding(self):
        """Test that tempo is correctly encoded (BPM × 6)."""
        tempo = 120.0
        writer = OctatrackWriter(
            output_path=self.output_path,
            sample_rate=44100,
            total_samples=44100,
            tempo=tempo
        )
        writer.write()

        with open(self.output_path, 'rb') as f:
            f.seek(0x10)
            tempo_value = struct.unpack('>I', f.read(4))[0]

        expected_tempo = int(tempo * 6)
        self.assertEqual(tempo_value, expected_tempo)

    def test_slice_addition(self):
        """Test adding slices to the writer."""
        writer = OctatrackWriter(
            output_path=self.output_path,
            sample_rate=44100,
            total_samples=44100 * 10
        )

        # Add test slices
        writer.add_slice(0, 44100)
        writer.add_slice(44100, 88200)
        writer.add_slice(88200, 132300)

        self.assertEqual(len(writer.slices), 3)
        self.assertEqual(writer.slices[0]['start'], 0)
        self.assertEqual(writer.slices[0]['end'], 44100)
        self.assertEqual(writer.slices[1]['start'], 44100)
        self.assertEqual(writer.slices[1]['end'], 88200)

    def test_slice_count_in_file(self):
        """Test that slice count is correctly written to file."""
        writer = OctatrackWriter(
            output_path=self.output_path,
            sample_rate=44100,
            total_samples=44100 * 10
        )

        writer.add_slice(0, 44100)
        writer.add_slice(44100, 88200)
        writer.add_slice(88200, 132300)
        writer.add_slice(132300, 176400)
        writer.write()

        with open(self.output_path, 'rb') as f:
            f.seek(0x34)
            slice_count = struct.unpack('>I', f.read(4))[0]

        self.assertEqual(slice_count, 4)

    def test_max_slices_limit(self):
        """Test that adding more than 64 slices raises an error."""
        writer = OctatrackWriter(
            output_path=self.output_path,
            sample_rate=44100,
            total_samples=44100 * 100
        )

        # Add 64 slices (the maximum)
        for i in range(64):
            writer.add_slice(i * 1000, (i + 1) * 1000)

        # Adding one more should raise ValueError
        with self.assertRaises(ValueError):
            writer.add_slice(64000, 65000)

    def test_default_loop_point(self):
        """Test that default loop point is 0xFFFFFFFF (no loop)."""
        writer = OctatrackWriter(
            output_path=self.output_path,
            sample_rate=44100,
            total_samples=44100
        )

        writer.add_slice(0, 44100)

        self.assertEqual(writer.slices[0]['loop'], 0xFFFFFFFF)

    def test_custom_loop_point(self):
        """Test that custom loop point is stored correctly."""
        writer = OctatrackWriter(
            output_path=self.output_path,
            sample_rate=44100,
            total_samples=44100
        )

        writer.add_slice(0, 44100, loop_point=22050)

        self.assertEqual(writer.slices[0]['loop'], 22050)

    def test_checksum_calculation(self):
        """Test that checksum is calculated and written."""
        writer = OctatrackWriter(
            output_path=self.output_path,
            sample_rate=44100,
            total_samples=44100
        )
        writer.write()

        with open(self.output_path, 'rb') as f:
            data = f.read()

        # Verify checksum exists at offset 0x33E
        checksum = struct.unpack('>H', data[0x33E:0x340])[0]

        # Checksum should be non-zero
        self.assertGreater(checksum, 0)

        # Manually calculate checksum
        expected_checksum = sum(data[16:-2]) & 0xFFFF
        self.assertEqual(checksum, expected_checksum)

    def test_bars_length_calculation(self):
        """Test that bars length is calculated correctly."""
        writer = OctatrackWriter(
            output_path=self.output_path,
            sample_rate=44100,
            total_samples=44100 * 4,  # 4 seconds at 120 BPM = 2 bars
            tempo=120.0
        )

        bars = writer._calculate_bars_length()

        # 4 seconds at 120 BPM = 8 beats = 2 bars
        self.assertEqual(bars, 2.0)

    def test_different_sample_rates(self):
        """Test that different sample rates are handled correctly."""
        for sample_rate in [22050, 44100, 48000, 96000]:
            output_path = os.path.join(self.temp_dir, f'test_{sample_rate}.ot')
            writer = OctatrackWriter(
                output_path=output_path,
                sample_rate=sample_rate,
                total_samples=sample_rate * 2
            )
            result = writer.write()

            self.assertTrue(result)
            self.assertEqual(os.path.getsize(output_path), 832)
            os.remove(output_path)

    def test_gain_encoding(self):
        """Test that gain is correctly encoded."""
        gain = 0  # Default gain
        writer = OctatrackWriter(
            output_path=self.output_path,
            sample_rate=44100,
            total_samples=44100,
            gain=gain
        )
        writer.write()

        with open(self.output_path, 'rb') as f:
            f.seek(0x24)
            gain_value = struct.unpack('>H', f.read(2))[0]

        # Gain is stored as gain + 48
        expected_gain = int(gain + 48)
        self.assertEqual(gain_value, expected_gain)

    def test_total_samples_storage(self):
        """Test that total samples count is stored correctly."""
        total_samples = 220500  # 5 seconds at 44.1kHz
        writer = OctatrackWriter(
            output_path=self.output_path,
            sample_rate=44100,
            total_samples=total_samples
        )
        writer.write()

        with open(self.output_path, 'rb') as f:
            f.seek(0x2C)
            stored_samples = struct.unpack('>I', f.read(4))[0]

        self.assertEqual(stored_samples, total_samples)


class TestOctatrackWriterEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_path = os.path.join(self.temp_dir, 'test_kit.ot')

    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.output_path):
            os.remove(self.output_path)
        os.rmdir(self.temp_dir)

    def test_zero_total_samples(self):
        """Test handling of zero total samples."""
        writer = OctatrackWriter(
            output_path=self.output_path,
            sample_rate=44100,
            total_samples=0
        )
        result = writer.write()

        self.assertTrue(result)
        self.assertEqual(os.path.getsize(self.output_path), 832)

    def test_no_slices(self):
        """Test file generation with no slices."""
        writer = OctatrackWriter(
            output_path=self.output_path,
            sample_rate=44100,
            total_samples=44100
        )
        result = writer.write()

        self.assertTrue(result)

        with open(self.output_path, 'rb') as f:
            f.seek(0x34)
            slice_count = struct.unpack('>I', f.read(4))[0]

        self.assertEqual(slice_count, 0)

    def test_invalid_output_path(self):
        """Test that invalid output path is handled."""
        invalid_path = '/nonexistent/directory/test.ot'
        writer = OctatrackWriter(
            output_path=invalid_path,
            sample_rate=44100,
            total_samples=44100
        )
        result = writer.write()

        # Should return False on error
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
