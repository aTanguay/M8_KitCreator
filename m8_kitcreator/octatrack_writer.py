"""
Octatrack .ot file writer module.

Generates Elektron Octatrack .ot metadata files for sliced audio samples.
Based on the reverse-engineered format from OctaChainer by KaiDrange.
"""

import struct
import logging
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)


class OctatrackWriter:
    """
    Writer for Elektron Octatrack .ot metadata files.

    The .ot format is a proprietary binary format that stores sample metadata
    including slice positions, tempo, loop settings, and other parameters.

    File Structure (832 bytes total):
    - 16-byte header: "FORM" magic + file type "DPS1SMPA"
    - Tempo, trim, loop, and gain settings
    - Up to 64 slices (start, end, loop points)
    - 16-bit checksum for validation
    """

    # Constants
    FILE_SIZE = 832
    HEADER_SIZE = 16
    MAX_SLICES = 64
    HEADER_MAGIC = b'FORM\x00\x00\x03,DPS1SMPA'

    # Default values
    DEFAULT_TEMPO = 120.0
    DEFAULT_GAIN = 0  # dB offset
    DEFAULT_LOOP_TYPE = 0  # 0=Off, 1=On, 2=PingPong
    DEFAULT_STRETCH = 0  # 0=Off, 1=Normal, 2=Beat
    DEFAULT_QUANTIZE = 0  # Trigger quantization

    def __init__(self, output_path: str, sample_rate: int = 44100, total_samples: int = 0,
                 tempo: Optional[float] = None, gain: Optional[int] = None,
                 loop_type: Optional[int] = None, stretch: Optional[int] = None,
                 quantize: Optional[int] = None):
        """
        Initialize the Octatrack writer.

        Args:
            output_path: Path for the output .ot file
            sample_rate: Sample rate of the audio (default: 44100)
            total_samples: Total number of samples in the audio file
            tempo: BPM (default: 120.0)
            gain: Gain in dB (default: 0)
            loop_type: Loop mode 0=Off, 1=On, 2=PingPong (default: 0)
            stretch: Time stretch mode 0=Off, 1=Normal, 2=Beat (default: 0)
            quantize: Trigger quantization setting (default: 0)
        """
        self.output_path = output_path
        self.sample_rate = sample_rate
        self.total_samples = total_samples

        # Parameters with defaults
        self.tempo = tempo if tempo is not None else self.DEFAULT_TEMPO
        self.gain = gain if gain is not None else self.DEFAULT_GAIN
        self.loop_type = loop_type if loop_type is not None else self.DEFAULT_LOOP_TYPE
        self.stretch = stretch if stretch is not None else self.DEFAULT_STRETCH
        self.quantize = quantize if quantize is not None else self.DEFAULT_QUANTIZE

        # Slice data
        self.slices: List[Dict[str, int]] = []

    def add_slice(self, start_point: int, end_point: int, loop_point: Optional[int] = None) -> None:
        """
        Add a slice to the .ot file.

        Args:
            start_point: Sample position where slice starts
            end_point: Sample position where slice ends
            loop_point: Sample position for loop (None = no loop)
        """
        if len(self.slices) >= self.MAX_SLICES:
            raise ValueError(f"Maximum of {self.MAX_SLICES} slices allowed")

        # Convert None to 0xFFFFFFFF (no loop indicator)
        if loop_point is None:
            loop_point = 0xFFFFFFFF

        self.slices.append({
            'start': int(start_point),
            'end': int(end_point),
            'loop': int(loop_point)
        })

    def write(self) -> bool:
        """
        Write the .ot file to disk.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Build the binary data
            data = bytearray(self.FILE_SIZE)

            # Write header
            data[0:16] = self.HEADER_MAGIC

            # Calculate derived values
            tempo_value = int(self.tempo * 6)  # Tempo stored as BPM × 6
            bars_length = self._calculate_bars_length()
            loop_length = bars_length  # For now, loop length = trim length

            # Write tempo (32-bit, big-endian at offset 0x10)
            struct.pack_into('>I', data, 0x10, tempo_value)

            # Write trim length (32-bit, big-endian at offset 0x14)
            trim_length_value = int(bars_length * 384)
            struct.pack_into('>I', data, 0x14, trim_length_value)

            # Write loop length (32-bit, big-endian at offset 0x18)
            loop_length_value = int(loop_length * 384)
            struct.pack_into('>I', data, 0x18, loop_length_value)

            # Write stretch mode (32-bit, big-endian at offset 0x1C)
            struct.pack_into('>I', data, 0x1C, self.stretch)

            # Write loop type (32-bit, big-endian at offset 0x20)
            struct.pack_into('>I', data, 0x20, self.loop_type)

            # Write gain (16-bit, big-endian at offset 0x24)
            gain_value = int(self.gain + 48)  # Gain offset by 48
            struct.pack_into('>H', data, 0x24, gain_value)

            # Write quantize (8-bit at offset 0x26)
            data[0x26] = self.quantize

            # Write trim start (32-bit, big-endian at offset 0x28)
            struct.pack_into('>I', data, 0x28, 0)  # Always start at 0

            # Write trim end (32-bit, big-endian at offset 0x2C)
            struct.pack_into('>I', data, 0x2C, self.total_samples)

            # Write loop point (32-bit, big-endian at offset 0x30)
            struct.pack_into('>I', data, 0x30, 0)  # Loop from start

            # Write slice count (32-bit, big-endian at offset 0x34)
            slice_count = len(self.slices)
            struct.pack_into('>I', data, 0x34, slice_count)

            # Write slice data starting at offset 0x38
            offset = 0x38
            for slice_data in self.slices:
                # Each slice: start (32-bit), end (32-bit), loop (32-bit)
                struct.pack_into('>I', data, offset, slice_data['start'])
                struct.pack_into('>I', data, offset + 4, slice_data['end'])
                struct.pack_into('>I', data, offset + 8, slice_data['loop'])
                offset += 12

            # Calculate and write checksum (16-bit at offset 0x33E)
            checksum = self._calculate_checksum(data)
            struct.pack_into('>H', data, 0x33E, checksum)

            # Write to file
            with open(self.output_path, 'wb') as f:
                f.write(data)

            print(f"Octatrack .ot file written: {self.output_path}")
            print(f"  Slices: {slice_count}")
            print(f"  Tempo: {self.tempo} BPM")
            return True

        except Exception as e:
            logger.error(f"Error writing .ot file: {e}")
            return False

    def _calculate_bars_length(self) -> float:
        """
        Calculate the length in bars based on sample count and tempo.

        Returns:
            Length in bars (rounded to nearest 0.25)
        """
        if self.total_samples == 0 or self.sample_rate == 0:
            return 1.0

        # Calculate duration in seconds
        duration_seconds = self.total_samples / self.sample_rate

        # Calculate number of beats
        beats_per_second = self.tempo / 60.0
        total_beats = duration_seconds * beats_per_second

        # Convert to bars (4 beats per bar)
        bars = total_beats / 4.0

        # Round to nearest 0.25
        bars_rounded = round(bars * 4) / 4.0

        return max(0.25, bars_rounded)  # Minimum 0.25 bars

    def _calculate_checksum(self, data: bytearray) -> int:
        """
        Calculate the checksum for the .ot file.

        The checksum is the sum of all bytes from offset 16 to end-2,
        masked to 16 bits.

        Args:
            data: The complete file data as bytearray

        Returns:
            16-bit checksum value
        """
        checksum = 0
        # Sum bytes from 16 to FILE_SIZE-2 (excluding checksum itself)
        for i in range(16, self.FILE_SIZE - 2):
            checksum += data[i]

        # Mask to 16 bits
        return checksum & 0xFFFF
