#!/usr/bin/env python3
import os
import pathlib
import re
import sys
import unicodedata as ud
from builtins import list
from shutil import copy2
from shutil import rmtree

include_o_form: bool = False

if __name__ == "__main__":

    skip_syllabary: bool = False
    only_syllabary: bool = True

    if skip_syllabary and only_syllabary:
        print("Can't skip Syllabary while outputting only Syllabary!")
        sys.exit(-1)

    if (sys.argv[0].strip() != ""):
        os.chdir(os.path.dirname(sys.argv[0]))

    MASTER_TEXTS: list = ["cno-training-data.txt"]

    entries: dict = {}
    for MASTER_TEXT in MASTER_TEXTS:
        with open(MASTER_TEXT, "r") as f:
            for line in f:
                fields = line.split("|")
                speaker: str = fields[0].strip()
                mp3: str = fields[1].strip()
                text: str = ud.normalize("NFC", fields[2].strip())
                dedupeKey = speaker + "|" + text + "|" + mp3
                if text == "" or "x" in text.lower():
                    continue
                if not include_o_form and "\u030a" in text:
                    continue
                has_syllabary: bool = re.search("[Ꭰ-Ᏼ]", text) != None
                if skip_syllabary and has_syllabary:
                    continue
                if only_syllabary and not has_syllabary:
                    continue
                entries[dedupeKey] = (speaker, mp3, text)

    print(f"Loaded {len(entries):,} entries with audio and text.")

    # the voice id to use for any "?" marked entries
    voiceid: str = ""
    with open("voice-id.txt", "r") as f:
        for line in f:
            voiceid = line.strip()
            break

    # to map any non "?" marked entries from annotation short hand id to ML assigned sequence id
    voiceids: dict = {}
    with open("../voice-ids.txt") as f:
        for line in f:
            mapping = line.strip()
            fields = mapping.split("|")
            if len(fields) < 2 or fields[1].strip() == "":
                break
            id = fields[0].strip()
            if id.strip() == "":
                continue
            for field in fields[1:]:
                if field.strip() == "":
                    continue
                voiceids[field.strip()] = id

    shortestLength: float = -1
    longestLength: float = 0.0
    totalLength: float = 0.0
    print("Copying audio files")
    rows: list = []
    already: dict = {}

    # cleanup any previous runs
    for dir in ["by-voice"]:
        rmtree(dir, ignore_errors=True)
    pathlib.Path(".").joinpath("by-voice").mkdir(exist_ok=True)

    for speaker, mp3, text in entries.values():
        dest = pathlib.Path(".").joinpath("by-voice").joinpath(speaker)
        dest.mkdir(exist_ok=True)
        copy2(mp3, dest)

    sys.exit()
