#!/usr/bin/env python3
import os
import sys
import unicodedata as ud
import random
import pathlib
from shutil import rmtree
from pydub import AudioSegment
import pydub.effects as effects
from split_audio import detect_sound
from builtins import list

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
                text: str = ud.normalize("NFD", fields[2].strip())
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

    chr_shortestLength: float = -1
    chr_longestLength: float = 0.0
    chr_totalLength: float = 0.0

    en_shortestLength: float = -1
    en_longestLength: float = 0.0
    en_totalLength: float = 0.0

    print("Creating wavs")
    rows: list = []
    for speaker, lang, mp3, text in entries.values():
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
        audio.export(wav, format="wav")
        if lang == "chr":
            chr_totalLength += audio.duration_seconds
            if chr_shortestLength < 0 or chr_shortestLength > audio.duration_seconds:
                chr_shortestLength = audio.duration_seconds
            if chr_longestLength < audio.duration_seconds:
                chr_longestLength = audio.duration_seconds
        elif lang == "en":
            en_totalLength += audio.duration_seconds
            if en_shortestLength < 0 or en_shortestLength > audio.duration_seconds:
                en_shortestLength = audio.duration_seconds
            if en_longestLength < audio.duration_seconds:
                en_longestLength = audio.duration_seconds
        else:
            raise Exception(f"Language not handled: {lang}")
        vid: str = speaker
        if vid in voiceids.keys():
            vid = voiceids[vid]
        if vid == "?":
            vid = default_voice_id
        rows.append(f"{entry_id:06d}|{vid}|{lang}|{wav}|||{text}|")
        entry_id += 1

    stats: str = ""
    minutes: int
    seconds: int

    stats += "Folder: "
    stats += os.path.basename(os.path.dirname(__file__))
    stats += "\n"

    minutes = int(chr_totalLength / 60)
    seconds = int(chr_totalLength % 60 + 0.5)
    stats += f"Total duration [chr]: {minutes:,}:{seconds:02}\n"
    stats += f"Shortest duration [chr]: {chr_shortestLength:05.2f}\n"
    stats += f"Longest duration [chr]: {chr_longestLength:05.2f}\n"
    stats += "\n"

    minutes = int(en_totalLength / 60)
    seconds = int(en_totalLength % 60 + 0.5)
    stats += f"Total duration [en]: {minutes:,}:{seconds:02}\n"
    stats += f"Shortest duration [en]: {en_shortestLength:05.2f}\n"
    stats += f"Longest duration [en]: {en_longestLength:05.2f}\n"
    stats += "\n"

    trainSize: int = int(len(rows) * .95)
    valSize: int = len(rows) - trainSize

    stats += f"Train size: {trainSize}\n"
    stats += f"Val size: {valSize}\n"
    stats += f"All size: {len(rows)}\n"
    stats += "\n"
    stats += "\n"

    print(stats)
    with open("data-stats.txt", "w") as f:
        f.write(stats)

    print("Creating training files")
    # save all copy before shuffling
    with open("all.txt", "w") as f:
        for line in rows:
            f.write(line)
            f.write("\n")

    # create train/val sets
    random.Random(voice_id).shuffle(rows)

    with open("train.txt", "w") as f:
        for line in rows[:trainSize]:
            f.write(line)
            f.write("\n")

    with open("val.txt", "w") as f:
        for line in rows[trainSize:]:
            f.write(line)
            f.write("\n")

    sys.exit()
