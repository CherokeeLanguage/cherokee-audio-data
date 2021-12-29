#!/usr/bin/env python3
import os
import pathlib
import random
import sys
import unicodedata as ud
from builtins import list
from shutil import rmtree

import pydub.effects as effects
from pydub import AudioSegment

from split_audio import detect_sound

if __name__ == "__main__":

    os.chdir(os.path.dirname(__file__))

    MASTER_TEXTS: list = ["data-chr.txt", "data-en.txt"]
    max_duration: float = 10.0

    # cleanup any previous runs
    for folder in ["linear_spectrograms", "spectrograms", "wav"]:
        rmtree(folder, ignore_errors=True)

    pathlib.Path(".").joinpath("wav").mkdir(exist_ok=True)

    entries: dict = {}
    MASTER_TEXT: str
    for MASTER_TEXT in MASTER_TEXTS:
        with open(MASTER_TEXT, "r") as f:
            lang: str = "chr"
            if MASTER_TEXT.endswith("-en.txt"):
                lang = "en"
            for line in f:
                fields = line.split("|")
                speaker: str = fields[0].strip()
                mp3: str = fields[1].strip()
                text: str = ud.normalize("NFC", fields[2].strip())
                dedupeKey = speaker + "|" + mp3 + "|" + text
                if not text.strip():
                    continue
                entries[dedupeKey] = (speaker, lang, mp3, text)

    print(f"Loaded {len(entries):,} entries with audio and text.")

    # the voice id to use for any "?" marked entries
    default_voice_id: str = ""
    with open("voice-id.txt", "r") as f:
        for line in f:
            default_voice_id = line.strip()
            break

    # to map any non "?" marked entries from annotation short hand id to ML assigned sequence id
    voiceids: dict = {}
    with open("../voice-ids.txt") as f:
        for line in f:
            mapping = line.strip()
            fields = mapping.split("|")
            if len(fields) < 2 or fields[1].strip() == "":
                break
            voice_id: str = fields[0].strip()
            if voice_id.strip() == "":
                continue
            for field in fields[1:]:
                if field.strip() == "":
                    continue
                voiceids[field.strip()] = voice_id

    entry_id: int = 1

    shortestLength: float = -1
    longestLength: float = 0.0
    totalLength: float = 0.0
    print("Creating wavs")
    rows: list = []
    for speaker, lang, mp3, text in entries.values():
        wav: str = "wav/" + os.path.splitext(os.path.basename(mp3))[0] + ".wav"
        text: str = ud.normalize('NFC', text)
        mp3_segment: AudioSegment = AudioSegment.from_file(mp3)
        segments: list = detect_sound(mp3_segment)
        if len(segments) > 1:
            mp3_segment = mp3_segment[segments[0][0]:segments[-1][1]]
        if mp3_segment.duration_seconds > max_duration:
            continue
        audio: AudioSegment = AudioSegment.silent(125, 22050)
        audio = audio.append(mp3_segment, crossfade=0)
        audio = audio.append(AudioSegment.silent(125, 22050))
        audio = effects.normalize(audio)
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(22050)
        audio.export(wav, format="wav")
        totalLength += audio.duration_seconds
        if shortestLength < 0 or shortestLength > audio.duration_seconds:
            shortestLength = audio.duration_seconds
        if longestLength < audio.duration_seconds:
            longestLength = audio.duration_seconds
        vid: str = speaker
        if vid in voiceids.keys():
            vid = voiceids[vid]
        if vid == "?":
            vid = default_voice_id
        rows.append(f"{entry_id:06d}|{vid}|{lang}|{wav}|||{text}|")
        entry_id += 1

    minutes = int(totalLength / 60)
    seconds = int(totalLength % 60 + 0.5)
    print(f"Total duration: {minutes:,}:{seconds:02}")

    seconds = shortestLength
    print(f"Shortest duration: {seconds:05.2f}")

    seconds = longestLength
    print(f"Longest duration: {seconds:05.2f}")

    print("Creating training files")
    # save all copy before shuffling
    with open("all.txt", "w") as f:
        for line in rows:
            f.write(line)
            f.write("\n")

    # create train/val sets
    random.Random(voice_id).shuffle(rows)
    trainSize: int = (int)(len(rows) * .95)
    valSize: int = len(rows) - trainSize

    with open("train.txt", "w") as f:
        for line in rows[:trainSize]:
            f.write(line)
            f.write("\n")

    with open("val.txt", "w") as f:
        for line in rows[trainSize:]:
            f.write(line)
            f.write("\n")

    print(f"Train size: {trainSize}")
    print(f"Val size: {valSize}")
    print(f"All size: {len(rows)}")
    print("Folder:", pathlib.Path(".").resolve().name)

    sys.exit()
