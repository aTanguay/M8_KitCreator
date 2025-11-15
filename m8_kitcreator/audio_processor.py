"""
Audio processing module for M8 Kit Creator.

Handles all audio concatenation, silence removal, and cue point generation.
"""

import os
import struct
import wave
from tkinter import messagebox
from pydub import AudioSegment
from pydub.silence import split_on_silence

from m8_kitcreator import config
from m8_kitcreator.utils import get_channel_description


class AudioProcessor:
    """
    Handles audio processing operations for creating M8-compatible kits.

    This class manages the concatenation of multiple WAV files with
    M8-compatible cue point markers, using frame-based positioning
    to correctly handle stereo and multi-channel audio.
    """

    def __init__(self,
                 marker_duration_ms=config.DEFAULT_MARKER_DURATION_MS,
                 silence_thresh=config.DEFAULT_SILENCE_THRESHOLD,
                 min_silence_len=config.DEFAULT_MIN_SILENCE_LEN,
                 retained_silence=config.DEFAULT_RETAINED_SILENCE,
                 force_mono=False):
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

    def concatenate_audio_files(self, file_paths, output_file, progress_callback=None):
        """
        Concatenate audio files with M8-compatible cue markers.

        This method takes multiple WAV files and combines them into a single
        WAV file with cue point markers at the start of each sample. The cue
        points use frame-based positioning to work correctly with stereo and
        multi-channel audio.

        Args:
            file_paths: List of WAV file paths to concatenate
            output_file: Path for the output WAV file
            progress_callback: Optional callback function for progress updates
                             Called with (current_file_index, total_files)

        Returns:
            bool: True if successful, False if an error occurred
        """
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
                print(f"Error loading {file_path}: {e}")
                messagebox.showerror(
                    "File Load Error",
                    f"Failed to load {os.path.basename(file_path)}:\n{str(e)}"
                )
                return False

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
        if not self._export_audio(concatenated_audio, output_file, target_channels):
            return False

        # Add cue points to WAV file
        if not self._add_cue_points(output_file, cue_positions):
            return False

        # Success!
        self._show_success_message(target_channels, cue_positions, total_files)
        return True

    def _process_silence(self, audio, retain_silence):
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

    def _calculate_frame_position(self, audio):
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

    def _export_audio(self, audio, output_file, target_channels):
        """
        Export audio to WAV file.

        Args:
            audio: AudioSegment to export
            output_file: Path for output file
            target_channels: Number of channels in output

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            audio.export(output_file, format="wav")
            channel_desc = get_channel_description(target_channels)
            print(f"Audio exported successfully! {channel_desc}")
            return True
        except Exception as e:
            print(f"Error exporting audio: {e}")
            messagebox.showerror(
                "Export Error",
                f"Failed to export audio:\n{str(e)}"
            )
            return False

    def _add_cue_points(self, wav_file, cue_positions):
        """
        Add cue point markers to a WAV file.

        Args:
            wav_file: Path to WAV file to add cue points to
            cue_positions: List of frame positions for cue points

        Returns:
            bool: True if successful, False otherwise
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

            return True

        except Exception as e:
            print(f"Error adding cue points: {e}")
            messagebox.showerror(
                "Cue Point Error",
                f"Audio exported but failed to add cue points:\n{str(e)}"
            )
            return False

    def _show_success_message(self, target_channels, cue_positions, num_files):
        """
        Display success message to user.

        Args:
            target_channels: Number of channels in output
            cue_positions: List of cue point positions
            num_files: Number of files merged
        """
        channel_desc = get_channel_description(target_channels)
        print(f"Output format: {channel_desc}, {len(cue_positions)} cue points")

        messagebox.showinfo(
            config.MSG_SUCCESS_TITLE,
            f"Files have been merged successfully!\n\n"
            f"Output: {channel_desc}\n"
            f"Cue points: {len(cue_positions)}\n"
            f"Files merged: {num_files}"
        )
