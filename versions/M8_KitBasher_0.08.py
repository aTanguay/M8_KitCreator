import os
import wave
import struct
from pydub import AudioSegment
from pydub.silence import split_on_silence

#this version comes real close to working. It adds some markes

def concatenate_audio_files(directory, output_file, marker_duration_ms=1000, silence_thresh=-40.0, min_silence_len=1000, retained_silence=100):
    marker = AudioSegment.silent(duration=marker_duration_ms)
    retain_silence = AudioSegment.silent(duration=retained_silence)

    audio_files = [f for f in os.listdir(directory) if f.endswith('.wav')]
    audio_files.sort()

    concatenated_audio = AudioSegment.empty()
    cue_positions = []
    current_frame = 0

    for file in audio_files:
        audio_path = os.path.join(directory, file)
        audio = AudioSegment.from_wav(audio_path)

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
    directory = input("Enter the directory containing the wav files: ").strip("'").strip('"')
    output_file = input("Enter the name of the output file (e.g., output.wav): ").strip("'").strip('"')
    concatenate_audio_files(directory, output_file)
