#!/usr/bin/env python3
import os
import pathlib
import random
import re
import sys
import unicodedata as ud
from builtins import list
from shutil import rmtree

import pydub.effects as effects
from pydub import AudioSegment

from split_audio import detect_sound

import progressbar

if __name__ == "__main__":

    if sys.argv[0].strip() != "":
        os.chdir(os.path.dirname(sys.argv[0]))

    max_duration: float = 10.0
    MASTER_TEXTS: list = ["cno-training-data.txt"]

    # cleanup any previous runs
    for folder in ["linear_spectrograms", "spectrograms", "wav"]:
        rmtree(folder, ignore_errors=True)

    pathlib.Path(".").joinpath("wav").mkdir(exist_ok=True)

    entries: dict = {}
    for MASTER_TEXT in MASTER_TEXTS:
        with open(MASTER_TEXT, "r") as f:
            for line in f:
                fields = line.split("|")
                speaker: str = fields[0].strip()
                lang: str = fields[1].strip()
                mp3: str = fields[2].strip()
                text: str = ud.normalize("NFD", fields[3].strip())
                dedupe_key = speaker + "|" + lang + "|" + text + "|" + mp3
                if text == "" or "x" in text.lower():
                    continue
                entries[dedupe_key] = (speaker, lang, mp3, text)

    print(f"Loaded {len(entries):,} entries with audio and text.")

    # the voice id to use for any "?" marked entries
    voiceid: str = ""
    with open("voice-id.txt", "r") as f:
        for line in f:
            voiceid = line.strip()
            break

    # to map any non "?" marked entries from annotation short hand id to ML assigned sequence id
    voice_ids: dict = {}
    with open("../voice-ids.txt") as f:
        for line in f:
            mapping = line.strip()
            fields = mapping.split("|")
            if len(fields) < 2 or fields[1].strip() == "":
                break
            voice_id = fields[0].strip()
            if voice_id.strip() == "":
                continue
            for field in fields[1:]:
                if field.strip() == "":
                    continue
                voice_ids[field.strip()] = voice_id

    bar = progressbar.ProgressBar(maxval=len(entries))
    bar.start()

    field_id: int = 1
    shortestLength: float = -1
    longestLength: float = 0.0
    totalLength: float = 0.0
    print("Creating wavs")
    rows: list = []
    already: dict = {}
    idx: int = 0
    for speaker, lang, mp3, text in entries.values():
        idx += 1
        bar.update(idx)
        wav: str = "wav/" + os.path.splitext(os.path.basename(mp3))[0] + ".wav"
        text: str = ud.normalize('NFD', text)
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
        if wav not in already:
            audio.export(wav, format="wav")
            already[wav] = True
        totalLength += audio.duration_seconds
        if shortestLength < 0 or shortestLength > audio.duration_seconds:
            shortestLength = audio.duration_seconds
        if longestLength < audio.duration_seconds:
            longestLength = audio.duration_seconds
        vid: str = speaker
        if vid in voice_ids.keys():
            vid = voice_ids[vid]
        if vid == "?":
            vid = voiceid
        rows.append(f"{field_id:06d}|{vid}|{lang}|{wav}|||{text}|")
        field_id += 1
    bar.finish()

    with open("stats.txt", "w") as f:
        print(f"Output {len(rows):,} entries.", file=f)

        print(file=f)

        totalLength = int(totalLength)
        hours = int(totalLength / 3600)
        minutes = int(totalLength % 3600 / 60)
        seconds = int(totalLength % 60)
        print(f"Total duration: {hours:,}:{minutes:02}:{seconds:02}", file=f)

        shortestLength = int(shortestLength)
        minutes = int(shortestLength / 60)
        seconds = int(shortestLength % 60)
        print(f"Shortest duration: {minutes:,}:{seconds:02}", file=f)

        longestLength = int(longestLength)
        minutes = int(longestLength / 60)
        seconds = int(longestLength % 60)
        print(f"Longest duration: {minutes:,}:{seconds:02}", file=f)

        print(file=f)

    print("Creating training files")
    # save all copy before shuffling
    with open("all.txt", "w") as f:
        for line in rows:
            f.write(line)
            f.write("\n")

    # create train/val sets
    random.Random(field_id).shuffle(rows)
    trainSize: int = int(len(rows) * .95)
    valSize: int = len(rows) - trainSize

    with open("train.txt", "w") as f:
        for line in rows[:trainSize]:
            f.write(line)
            f.write("\n")

    with open("val.txt", "w") as f:
        for line in rows[trainSize:]:
            f.write(line)
            f.write("\n")

    with open("stats.txt", "a") as f:
        print(f"All size: {len(rows)}", file=f)
        print(f"Train size: {trainSize}", file=f)
        print(f"Val size: {valSize}", file=f)
        print(file=f)
        print("Folder:", pathlib.Path(".").resolve().name, file=f)
        print(file=f)

    sys.exit()
