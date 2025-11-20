"""
Audio processing module for M8 Kit Creator.

Handles all audio concatenation, silence removal, and cue point generation.
"""

import os
import struct
import wave
import logging
from typing import List, Optional, Callable, Union
from pydub import AudioSegment
from pydub.silence import split_on_silence

from m8_kitcreator import config
from m8_kitcreator.utils import get_channel_description
from m8_kitcreator.octatrack_writer import OctatrackWriter
from m8_kitcreator.exceptions import AudioProcessingError, ExportError, OctatrackError

logger = logging.getLogger(__name__)

# Configure pydub to use bundled ffmpeg if available
try:
    from staticffmpeg import run
    # Get the static ffmpeg binary path
    ffmpeg_path, ffprobe_path = run.get_or_fetch_platform_executables_else_raise()
    AudioSegment.converter = ffmpeg_path
    AudioSegment.ffprobe = ffprobe_path
    print(f"Using bundled ffmpeg: {ffmpeg_path}")
except ImportError:
    # static-ffmpeg not available, will use system ffmpeg
    logger.info("static-ffmpeg not available, using system ffmpeg")
except Exception as e:
    # Failed to get ffmpeg, will use system default
    logger.warning(f"Could not configure static ffmpeg: {e}")
    logger.info("Will attempt to use system ffmpeg")


class AudioProcessor:
    """
    Handles audio processing operations for creating M8-compatible kits.

    This class manages the concatenation of multiple WAV files with
    M8-compatible cue point markers, using frame-based positioning
    to correctly handle stereo and multi-channel audio.
    """

    def __init__(self,
                 marker_duration_ms: int = config.DEFAULT_MARKER_DURATION_MS,
                 silence_thresh: float = config.DEFAULT_SILENCE_THRESHOLD,
                 min_silence_len: int = config.DEFAULT_MIN_SILENCE_LEN,
                 retained_silence: int = config.DEFAULT_RETAINED_SILENCE,
                 force_mono: bool = False):
        """
        Initialize the AudioProcessor with processing parameters.

        Args:
            marker_duration_ms: Duration of silent markers between samples (ms)
            silence_thresh: Silence detection threshold in dBFS
            min_silence_len: Minimum silence duration to detect (ms)
            retained_silence: Amount of silence to keep between chunks (ms)
            force_mono: If True, convert all audio to mono (default: False)
        """
        self.marker_duration_ms = marker_duration_ms
        self.silence_thresh = silence_thresh
        self.min_silence_len = min_silence_len
        self.retained_silence = retained_silence
        self.force_mono = force_mono

    def concatenate_audio_files(self, file_paths: List[str], output_file: str,
                                progress_callback: Optional[Callable[[int, int], None]] = None,
                                output_format: Optional[str] = None) -> bool:
        """
        Concatenate audio files with M8-compatible cue markers and optional Octatrack .ot file.

        This method takes multiple WAV files and combines them into a single
        WAV file with cue point markers at the start of each sample. The cue
        points use frame-based positioning to work correctly with stereo and
        multi-channel audio.

        Args:
            file_paths: List of WAV file paths to concatenate
            output_file: Path for the output WAV file
            progress_callback: Optional callback function for progress updates
                             Called with (current_file_index, total_files)
            output_format: Output format - M8, Octatrack, or Both (default: M8)

        Returns:
            bool: True if successful

        Raises:
            AudioProcessingError: If audio loading or processing fails
            ExportError: If export fails
            OctatrackError: If Octatrack file generation fails
        """
        # Default to M8 format if not specified
        if output_format is None:
            output_format = config.OUTPUT_FORMAT_M8
        # Initialize processing state
        marker = None
        retain_silence = None
        target_channels = None

        concatenated_audio = AudioSegment.empty()
        cue_positions = []

        total_files = len(file_paths)

        # Process each file
        for i, file_path in enumerate(file_paths):
            # Update progress if callback provided
            if progress_callback:
                progress_callback(i, total_files)

            # Load audio file
            try:
                audio = AudioSegment.from_wav(file_path)
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")
                raise AudioProcessingError(f"Failed to load {os.path.basename(file_path)}: {str(e)}")

            # On first file, determine target channel count and create markers
            if i == 0:
                target_channels = 1 if self.force_mono else audio.channels

                # Create markers with same sample rate as audio
                marker = AudioSegment.silent(
                    duration=self.marker_duration_ms,
                    frame_rate=audio.frame_rate
                )
                marker = marker.set_channels(target_channels)

                retain_silence = AudioSegment.silent(
                    duration=self.retained_silence,
                    frame_rate=audio.frame_rate
                )
                retain_silence = retain_silence.set_channels(target_channels)

                # Add initial marker and record FRAME position
                concatenated_audio += marker
                marker_samples = len(marker.get_array_of_samples())
                marker_frames = marker_samples // marker.channels
                cue_positions.append(marker_frames)

            # Convert to target channel count if needed
            if audio.channels != target_channels:
                audio = audio.set_channels(target_channels)

            # Process silence removal
            processed_audio = self._process_silence(audio, retain_silence)

            # Add processed audio
            concatenated_audio += processed_audio

            # Calculate and store FRAME position (not sample position!)
            frame_position = self._calculate_frame_position(concatenated_audio)
            cue_positions.append(frame_position)

            # Add marker
            concatenated_audio += marker

        # Update progress to completion
        if progress_callback:
            progress_callback(total_files, total_files)

        # Export audio file
        self._export_audio(concatenated_audio, output_file, target_channels)

        # Add cue points to WAV file (for M8 and Both)
        if output_format in [config.OUTPUT_FORMAT_M8, config.OUTPUT_FORMAT_BOTH]:
            self._add_cue_points(output_file, cue_positions)

        # Generate Octatrack .ot file (for Octatrack and Both)
        if output_format in [config.OUTPUT_FORMAT_OCTATRACK, config.OUTPUT_FORMAT_BOTH]:
            self._generate_ot_file(output_file, concatenated_audio, cue_positions)

        # Success!
        self._log_success_message(target_channels, cue_positions, total_files, output_format)
        return True

    def _process_silence(self, audio: AudioSegment, retain_silence: AudioSegment) -> AudioSegment:
        """
        Process audio to remove silence.

        Args:
            audio: AudioSegment to process
            retain_silence: AudioSegment of silence to retain between chunks

        Returns:
            AudioSegment: Processed audio with silence removed
        """
        chunks = split_on_silence(
            audio,
            silence_thresh=self.silence_thresh,
            min_silence_len=self.min_silence_len
        )

        if chunks:
            # Join chunks with retained silence
            processed_audio = sum(
                [chunk + retain_silence for chunk in chunks],
                AudioSegment.empty()
            )[:-self.retained_silence]
        else:
            # No silence detected, use original audio
            processed_audio = audio

        return processed_audio

    def _calculate_frame_position(self, audio: AudioSegment) -> int:
        """
        Calculate the current frame position in the audio.

        Uses frame-based positioning (samples / channels) to correctly
        handle stereo and multi-channel audio for M8 cue points.

        Args:
            audio: AudioSegment to calculate position for

        Returns:
            int: Frame position
        """
        sample_count = len(audio.get_array_of_samples())
        frame_position = sample_count // audio.channels
        return frame_position

    def _export_audio(self, audio: AudioSegment, output_file: str, target_channels: int) -> None:
        """
        Export audio to WAV file.

        Args:
            audio: AudioSegment to export
            output_file: Path for output file
            target_channels: Number of channels in output

        Raises:
            ExportError: If export fails
        """
        try:
            audio.export(output_file, format="wav")
            channel_desc = get_channel_description(target_channels)
            logger.info(f"Audio exported successfully! {channel_desc}")
        except Exception as e:
            logger.error(f"Error exporting audio: {e}")
            raise ExportError(f"Failed to export audio: {str(e)}")

    def _add_cue_points(self, wav_file: str, cue_positions: List[int]) -> None:
        """
        Add cue point markers to a WAV file.

        Args:
            wav_file: Path to WAV file to add cue points to
            cue_positions: List of frame positions for cue points

        Raises:
            ExportError: If adding cue points fails
        """
        try:
            # Read WAV file
            with wave.open(wav_file, 'rb') as wf:
                params = wf.getparams()
                num_frames = params.nframes
                data = wf.readframes(num_frames)

            # Build cue chunk
            cue_chunk_data = struct.pack('<L', len(cue_positions))
            for i, position in enumerate(cue_positions):
                cue_id = i + 1
                cue_chunk_data += struct.pack(
                    '<LL4sLLL',
                    cue_id, position, b'data', 0, 0, position
                )

            cue_chunk = b'cue ' + struct.pack('<L', len(cue_chunk_data)) + cue_chunk_data

            # Write WAV file with cue chunk
            with wave.open(wav_file, 'wb') as wf:
                wf.setparams(params)
                wf.writeframes(data)
                wf._file.write(cue_chunk)

        except Exception as e:
            logger.error(f"Error adding cue points: {e}")
            raise ExportError(f"Audio exported but failed to add cue points: {str(e)}")

    def _generate_ot_file(self, wav_file: str, audio: AudioSegment, cue_positions: List[int]) -> None:
        """
        Generate Octatrack .ot metadata file.

        Args:
            wav_file: Path to the WAV file (used to determine .ot filename)
            audio: AudioSegment containing the audio data
            cue_positions: List of frame positions for slices

        Raises:
            OctatrackError: If .ot file generation fails
        """
        try:
            # Create .ot filename by replacing .wav extension
            ot_file = os.path.splitext(wav_file)[0] + '.ot'

            # Get audio parameters
            sample_rate = audio.frame_rate
            total_samples = len(audio.get_array_of_samples()) // audio.channels

            # Create OctatrackWriter
            ot_writer = OctatrackWriter(
                output_path=ot_file,
                sample_rate=sample_rate,
                total_samples=total_samples
            )

            # Add slices based on cue positions
            # Each slice starts at the cue position and ends at the next cue position
            # (or at the end of the file for the last slice)
            for i in range(len(cue_positions) - 1):
                start_point = cue_positions[i]
                end_point = cue_positions[i + 1]
                ot_writer.add_slice(start_point, end_point)

            # Write the .ot file
            ot_writer.write()
            logger.info(f"Octatrack .ot file generated: {ot_file}")

        except Exception as e:
            logger.error(f"Error generating .ot file: {e}")
            raise OctatrackError(f"Audio exported but failed to generate .ot file: {str(e)}")

    def _log_success_message(self, target_channels: int, cue_positions: List[int],
                                   num_files: int, output_format: Optional[str] = None) -> None:
        """
        Log success message.

        Args:
            target_channels: Number of channels in output
            cue_positions: List of cue point positions
            num_files: Number of files merged
            output_format: Output format (M8, Octatrack, or Both)
        """
        # Default to M8 if not specified
        if output_format is None:
            output_format = config.OUTPUT_FORMAT_M8

        channel_desc = get_channel_description(target_channels)
        logger.info(f"Output format: {output_format}, {channel_desc}, {len(cue_positions)} cue points")
        logger.info(f"Files merged: {num_files}")
