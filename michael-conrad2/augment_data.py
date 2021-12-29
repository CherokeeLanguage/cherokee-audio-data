#!/usr/bin/env python3
import os
import pathlib
import random
import re
import sys
import unicodedata as ud
from random import Random
from shutil import rmtree

from pydub import AudioSegment

rand: Random = random.Random(1234)


def duration_txt(seconds: float) -> str:
    seconds = int(seconds)
    hours: int = int(seconds / 3600)
    minutes: int = int(seconds % 3600 / 60)
    seconds = int(seconds % 60)
    return f"{hours:,}:{minutes:02d}:{seconds:02d}"


if __name__ == "__main__":

    aligned_txt: str = "cno-training-data.txt"
    augmented_txt: str = "augmented.txt"
    augmented_dir: str = "mp3-augmented"

    skip_syllabary: bool = True
    only_syllabary: bool = False

    minLength: int = 60 * 60 * 5  # 5 hours

    if sys.argv[0]:
        dname = os.path.dirname(sys.argv[0])
        if dname:
            os.chdir(dname)

    print("Cleaning up from previous session")
    rmtree(augmented_dir, ignore_errors=True)
    pathlib.Path(".").joinpath(augmented_dir).mkdir(exist_ok=True)

    print("Loading list and calculating total audio length")

    haveLength: int = 0
    with open(aligned_txt, "r") as f:
        entriesDict: dict = {}
        for line in f:
            spkr: str = line.split("|")[0].strip()
            mp3: str = line.split("|")[1].strip()
            text: str = ud.normalize("NFC", line.split("|")[2].strip())
            if text == "":
                continue

            if skip_syllabary and re.search("(?i)[Ꭰ-Ᏼ]", text):
                continue
            if only_syllabary and re.search("(?i)[a-z]", text):
                continue

            if not text[-1] in ".,!?:\"'":
                text += "."
            entriesDict[text + "|" + mp3] = (mp3, text, spkr)

    for e in entriesDict.values():
        haveLength += AudioSegment.from_mp3(e[0]).duration_seconds

    if minLength - haveLength > haveLength:
        minLength -= haveLength
    else:
        minLength = haveLength

    entries: list = [e for e in entriesDict.values()]

    speakers: list = list(set([e[2] for e in entries]))
    if len(speakers) > 1:
        print("Speakers:", speakers)

    print(f"Have {len(entries):,} starting entries with {len(speakers):,} speakers.")
    print(f"Starting duration: {duration_txt(haveLength)}")
    print(f"Need augmented duration: {duration_txt(minLength)}")

    with open(augmented_txt, "w") as f:
        f.write("")

    totalTime: float = 0
    totalCount: int = 0
    already: set = set()

    ix: int = 0
    speaker: str = rand.choice(speakers)
    text: str = ""
    track: AudioSegment = AudioSegment.silent(125, 22050)
    current_txt: str = ""
    total_duration: float = 0.0
    while total_duration < minLength:
        entry = rand.choice(entries)
        if entry[2] != speaker:
            continue
        segment: AudioSegment = AudioSegment.from_mp3(entry[0])
        if segment.duration_seconds + track.duration_seconds < 10:
            track = track.append(AudioSegment.silent(750, 22050))
            track = track.append(segment, 0)
            current_txt += " " + entry[1]
        else:
            if current_txt.strip() and not (speaker + "|" + current_txt) in already:
                already.add(speaker + "|" + current_txt)
                if track.duration_seconds <= 10:
                    totalCount += 1
                    ix += 1
                    track = track.append(AudioSegment.silent(125, 22050))
                    mp3_output: str = f"{augmented_dir}/{int(ix):09d}-{speaker}.mp3"
                    track.export(mp3_output)
                    total_duration += track.duration_seconds

                    with open(augmented_txt, "a") as f:
                        f.write(f"{speaker}")
                        f.write("|")
                        f.write(f"{mp3_output}")
                        f.write("|")
                        f.write(ud.normalize("NFC", current_txt.strip()))
                        f.write("\n")

            speaker: str = rand.choice(speakers)
            track = AudioSegment.silent(125, 22050)
            current_txt = ""

    print(f"Total time: {duration_txt(total_duration + haveLength)}")
    print(f"Augmented tracks: {totalCount:,}.")
    print("Folder:", pathlib.Path(".").resolve().name)

    sys.exit(0)
