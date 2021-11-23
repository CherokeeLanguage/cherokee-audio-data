#!/usr/bin/env -S conda run -n CherokeeTrainingData python
import glob
import os
import shutil

import pydub.silence
from denoiser.enhance import *
from pydub import AudioSegment
from pydub import effects
from pydub.silence import detect_leading_silence
from voicefixer import VoiceFixer


def trim_silence(audio_segment: AudioSegment) -> AudioSegment:
    silence_threshold: float = -40

    def trim_leading_silence(tmp_audio: AudioSegment):
        return tmp_audio[detect_leading_silence(tmp_audio, silence_threshold=silence_threshold):]

    def trim_trailing_silence(tmp_audio: AudioSegment):
        tmp_reversed: AudioSegment = tmp_audio.reverse()
        return tmp_reversed[detect_leading_silence(tmp_reversed):].reverse()

    return trim_trailing_silence(trim_leading_silence(audio_segment))


def squelch(audio_segment: AudioSegment, min_silence_len: int = 250, threshold: int = -50):
    silent_segments: list[list[int]] = pydub.silence.detect_silence(audio_segment, min_silence_len=min_silence_len,
                                                                    silence_thresh=threshold)
    if not silent_segments:
        return audio_segment

    new_audio = audio_segment.empty()
    prev_end: int = 0

    for segment in silent_segments:
        silent_start = segment[0]
        silent_end = segment[1]
        new_audio = (new_audio  #
                     + audio_segment[prev_end:silent_start]  #
                     + AudioSegment.silent(silent_end - silent_start + 1, frame_rate=audio_segment.frame_rate)  #
                     )
        prev_end = silent_end

    if prev_end < len(audio_segment):
        new_audio = new_audio + audio_segment[prev_end:]

    return new_audio


def main() -> None:
    argv0: str = sys.argv[0]
    if argv0:
        workdir: str = os.path.dirname(argv0)
        if workdir:
            os.chdir(workdir)

    src_noisy: str = os.path.join(os.getcwd(), "src.noisy")
    src_enhanced: str = os.path.join(os.getcwd(), "src.vf")
    src_tmp: str = os.path.join(os.getcwd(), "tmp.src.noisy")

    # clean up any previous files
    for folder in [src_enhanced, src_tmp]:
        shutil.rmtree(folder, ignore_errors=True)
        os.mkdir(folder)

    # enhance files, one at a time

    src_glob_pattern: str = os.path.join(src_noisy, "*.mp3")
    noisy_mp3s: list[str] = glob.glob(src_glob_pattern)
    noisy_mp3s.sort()

    vf: VoiceFixer = VoiceFixer()

    for noisy_mp3 in noisy_mp3s:
        basename: str = os.path.basename(noisy_mp3)
        output_mp3: str = os.path.splitext(basename)[0] + ".mp3"

        mp3_audio: AudioSegment = AudioSegment.from_file(noisy_mp3)
        mp3_audio = mp3_audio.set_channels(1)
        mp3_audio = mp3_audio.set_frame_rate(44100)
        mp3_audio = effects.normalize(mp3_audio)

        # Match reel-to-reel reported ranges
        # mp3_audio = effects.high_pass_filter(mp3_audio, cutoff=40)
        # mp3_audio = effects.low_pass_filter(mp3_audio, cutoff=20000)
        mp3_audio = trim_silence(mp3_audio)

        input_wav: str = os.path.join(src_tmp, f"input.wav")
        mp3_audio.export(input_wav, format="wav")

        print(f" - Processing {basename}")
        output_wav: str = os.path.join(src_tmp, f"output.wav")
        vf.restore(input_wav, output_wav, mode=0, cuda=True)
        mp3_audio: AudioSegment = AudioSegment.from_file(output_wav)
        #  mp3_audio = squelch(mp3_audio)
        mp3_audio.export(os.path.join(src_enhanced, f"{output_mp3}"), format="mp3", parameters=["-qscale:a", "3"])

    print()
    print("DONE")
    print()


if __name__ == "__main__":
    main()
