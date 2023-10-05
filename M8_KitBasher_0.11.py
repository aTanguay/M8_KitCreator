import os
import wave
import struct
import tkinter as tk
from tkinter import filedialog
from pydub import AudioSegment
from pydub.silence import split_on_silence

# This works for the most part. for some reason, the markers are wrong ,but damn it's close

def concatenate_audio_files(audio_files, output_file, marker_duration_ms=1000, silence_thresh=-40.0, min_silence_len=1000, retained_silence=100):
    marker = AudioSegment.silent(duration=marker_duration_ms)
    retain_silence = AudioSegment.silent(duration=retained_silence)

    concatenated_audio = AudioSegment.empty()
    cue_positions = []
    current_frame = 0

    for file in audio_files:
        audio = AudioSegment.from_wav(file)
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


