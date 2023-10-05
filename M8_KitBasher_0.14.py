import os
import wave
import struct
import tkinter as tk
from tkinter import filedialog
from pydub import AudioSegment
from pydub.silence import split_on_silence

# This seems to work just right. The only issue is that it converts it to mono
# I think the main code is a little wonky, but it's pretty good
# Seems to be trimming fat off the files, which is great
# Written against python 3 on 2023_10_04


def concatenate_audio_files(audio_files, output_file, marker_duration_ms=1, silence_thresh=-50.0, min_silence_len=10, retained_silence=1):
    marker = AudioSegment.silent(duration=marker_duration_ms)
    retain_silence = AudioSegment.silent(duration=retained_silence)

    concatenated_audio = AudioSegment.empty()
    cue_positions = [len(marker.get_array_of_samples())]  # Add initial marker position

    concatenated_audio += marker  # Add marker at 00 position

    for file in audio_files:
        audio = AudioSegment.from_wav(file)

        # Convert to mono
        audio = audio.set_channels(1)

        chunks = split_on_silence(audio, silence_thresh=silence_thresh, min_silence_len=min_silence_len)
        processed_audio = sum([chunk + retain_silence for chunk in chunks], AudioSegment.empty())[:-retained_silence]

        concatenated_audio += processed_audio
        cue_positions.append(len(concatenated_audio.get_array_of_samples()))
        concatenated_audio += marker

    concatenated_audio.export(output_file, format="wav")

    # Add cue points
    with wave.open(output_file, 'rb') as wf:
        params = wf.getparams()
        num_frames = params.nframes
        data = wf.readframes(num_frames)

    cue_chunk_data = struct.pack('<L', len(cue_positions))
    for i, position in enumerate(cue_positions):
        cue_id = i + 1
        cue_chunk_data += struct.pack('<LL4sLLL', cue_id, position, b'data', 0, 0, position)

    cue_chunk = b'cue ' + struct.pack('<L', len(cue_chunk_data)) + cue_chunk_data

    with wave.open(output_file, 'wb') as wf:
        wf.setparams(params)
        wf.writeframes(data)
        wf._file.write(cue_chunk)

    print(f"Concatenated audio saved as {output_file}")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    audio_files = filedialog.askopenfilenames(title="Select WAV files", filetypes=[("WAV files", "*.wav")])
    if not audio_files:
        print("No files selected. Exiting.")
        exit()

    output_file = filedialog.asksaveasfilename(title="Select the output file", defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
    if not output_file:
        print("No output file selected. Exiting.")
        exit()
    concatenate_audio_files(audio_files, output_file)


