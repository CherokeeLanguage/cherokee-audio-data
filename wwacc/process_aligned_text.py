#!/usr/bin/env python3
import re

import json
import os
import sys
import numpy as np
from sklearn.cluster import AffinityPropagation
from fuzzy_match import algorithims

if __name__ == "__main__":

    voice_ranges: dict = dict()
    if os.path.exists("voice-ranges.json"):
        with open("voice-ranges.json", "r") as f:
            for (range_start, voice_id) in json.loads(f.read())["ranges"]:
                voice_ranges[int(range_start)] = voice_id

    print(voice_ranges)

    aligned_text: str = "aligned.txt"
    output_text: str = "selected.txt"
    training1_text: str = "training1.txt"
    training2_text: str = "training2.txt"

    workdir: str = os.path.dirname(sys.argv[0])
    if workdir.strip() != "":
        os.chdir(workdir)
    workdir = os.getcwd()

    mp3s: list = []
    for (dirpath, dirnames, filenames) in os.walk("mp3"):
        mp3s.extend(filenames)
    mp3s.sort()
    print(f"Loaded {len(mp3s):,} MP3s")

    lines: list = []
    with open(aligned_text, "r") as f:
        for line in f:
            if len(line.strip()) == 0:
                break
            lines.append(line.strip())
    print(f"Loaded {len(lines):,} text aligments")

    entries: list = list()
    count: int = 0

    line_no: int = 0
    mp3: str
    line: str
    voice: str = "?"
    for mp3, line in zip(mp3s, lines):
        line_no += 1
        if line_no in voice_ranges.keys():
            voice = voice_ranges[line_no]
        line = line.strip()
        mp3 = mp3.replace("mp3/", "")
        if "|" in line:
            parts: list = line.split("|")
            if len(parts) != 2:
                continue
            if parts[1].strip() != mp3:
                raise Exception(f"Alignment fail [{line_no}] mp3={mp3} marker={parts[1]} text={parts[0]}")
        if "x" in line.lower():
            continue
        entries.append((voice, os.path.join("mp3", mp3), line))
        count += 1

    with open(output_text, "w") as f:
        voice: str
        mp3: str
        line: str
        for (voice, mp3, line) in entries:
            print(f"{voice}|{mp3}|{line}", file=f)

    prev = ""
    pset: int = 0
    line_no = 0
    with open(training1_text, "w") as t1:
        with open(training2_text, "w") as t2:
            voice: str
            mp3: str
            line: str
            print("ID|PSET|DIALOG|PRONOUN|VERB|GENDER|SYLLABARY|PRONOUNCE|ENGLISH|AUDIO FILE", file=t1)
            print("ID|PSET|DIALOG|PRONOUN|VERB|GENDER|SYLLABARY|PRONOUNCE|ENGLISH|AUDIO FILE", file=t2)
            buckets: dict = dict([])
            voice: str
            mp3: str
            text: str
            for (voice, mp3, text) in entries:
                text = text.lower().strip()
                text = re.sub("(?i)[^a-z ]", "", text)
                text = re.sub("\\s+", " ", text)
                gender: str = ""
                if "-f-" in voice:
                    gender = "female"
                if "-m-" in voice:
                    gender = "male"
                d = algorithims.trigram(prev, text)
                prev = text
                if d < 0.17:
                    pset += 1
                    buckets[pset] = list()
                line_no += 1
                text = f"{line_no:04d}|{pset}||||{gender}||{text}||{mp3}"
                buckets[pset].append(text)
                print(text, file=t1)
            keep_going: bool = True
            ix: int = 0
            while keep_going:
                keep_going = False
                for bucket in buckets.keys():
                    if len(buckets[bucket]) > ix:
                        keep_going = True
                        print(f"{buckets[bucket][ix]}", file=t2)
                ix += 1

    print(f"Output {len(entries):,} {aligned_text} TTS training entries")



