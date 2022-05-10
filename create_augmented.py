#!/usr/bin/env bash
"""true" '''\'
set -e
eval "$(conda shell.bash hook)"
conda deactivate
conda activate cherokee-audio-data
exec python "$0" "$@"
exit $?
''"""

import glob
import os
import random
import shutil
import subprocess
import sys

from pydub import AudioSegment
from tqdm import tqdm


def main():
    argv0: str = sys.argv[0]
    workdir: str
    if argv0:
        workdir: str = os.path.dirname(argv0)
        if workdir:
            os.chdir(workdir)

    all_list: list[str] = []
    all_list.extend(glob.glob("*/all.txt"))
    all_list.sort()
    for all_filename in all_list:
        folder: str = os.path.dirname(os.path.realpath(all_filename))
        augment_folder: str = os.path.join(os.path.dirname(all_filename), "wav2")
        augment_file: str = os.path.join(os.path.dirname(all_filename), "all-augmented.txt")
        shutil.rmtree(augment_folder, ignore_errors=True)
        os.makedirs(augment_folder, exist_ok=True)
        print()
        print(f"=== {os.path.basename(folder)}")
        entries: dict[str, list[tuple[str, str]]] = dict()
        voices: list[str] = list()
        with open(all_filename, "r") as r:
            for line in r:
                line = line.strip()
                parts = line.split("|")
                entry_id = parts[0]
                entry_voice = parts[1]
                entry_lang = parts[2]
                entry_wav = parts[3]
                transcript = parts[6]
                if entry_lang != "chr":
                    continue
                if entry_voice not in entries:
                    entries[entry_voice] = list()
                entries[entry_voice].append((entry_wav, transcript))
                if entry_voice not in voices:
                    voices.append(entry_voice)
        voices.sort()
        augments: list[str] = list()
        ix: int = 0
        for voice in voices:
            print(f" - {voice}")
            for _ in tqdm(range(100)):
                if len(entries[voice]) < 32:
                    continue
                ix += 1
                samples = random.sample(entries[voice], 32)
                audio: AudioSegment = AudioSegment.silent(0, 48_000)
                new_transcript: str = ""
                for wav, transcript in samples:
                    transcript = transcript.strip()
                    append_audio = AudioSegment.from_file(os.path.join(folder, wav))
                    if append_audio.duration_seconds+audio.duration_seconds <= 20.0:
                        audio = audio.append(AudioSegment.silent(350, 48_000), 0)
                        audio = audio.append(append_audio, 0)
                        transcript = transcript[0].upper() + transcript[1:]
                        e: str = transcript[-1]
                        if e != "." and e != "!" and e != "?" and e != ",":
                            transcript += "."
                        if new_transcript:
                            new_transcript += " "
                        new_transcript += transcript
                audio_path: str = os.path.join(augment_folder, f"combined-{ix:04}.wav")
                audio.export(audio_path)
                folder_name: str = os.path.basename(folder)
                audio_name: str = os.path.basename(audio_path)
                audio_path: str = f"wav2/{audio_name}"
                augments.append(f"{ix:04}|{voice}|chr|{audio_path}|||{new_transcript}|")
        with open(augment_file, "w") as w:
            for line in augments:
                w.write(line)
                w.write("\n")


if __name__ == "__main__":
    main()
