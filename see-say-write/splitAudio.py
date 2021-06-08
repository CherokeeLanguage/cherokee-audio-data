#!/usr/bin/env python3

import os
import sys
import string
import unicodedata as ud
import random
import re
import pathlib
import subprocess
from shutil import rmtree
from pydub.effects import normalize

workdir:str = os.path.dirname(sys.argv[0])
if workdir.strip() != "":
    os.chdir(workdir)
workdir = os.getcwd()

# https://stackoverflow.com/questions/45526996/split-audio-files-using-silence-detection

# Import the AudioSegment class for processing audio and the 
# split_on_silence function for separating out silent chunks.
from pydub import AudioSegment
from pydub.silence import split_on_silence

# From https://stackoverflow.com/questions/29547218/
# remove-silence-at-the-beginning-and-at-the-end-of-wave-files-with-pydub
from pydub import AudioSegment


def detect_leading_silence(sound, silence_threshold=-50.0, chunk_size=10):
    '''
    sound is a pydub.AudioSegment
    silence_threshold in dB
    chunk_size in ms
    iterate over chunks until you find the first one with sound
    '''
    trim_ms = 0  # ms
    while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold:
        trim_ms += chunk_size

    return trim_ms

#clean up any previous files
rmtree("mp3", ignore_errors=True)
os.mkdir("mp3")

from os import walk
mp3s = []
for (dirpath, dirnames, filenames) in walk("src"):
    mp3s.extend(filenames)
    break
mp3s.sort()
splits:list=[]
for mp3 in mp3s:
    if os.path.splitext(mp3)[1].lower()!=".mp3":
        continue
    print(f"Processing {mp3}")
    data = AudioSegment.from_mp3("src/" + mp3)
    mp3=os.path.splitext(mp3)[0]
    print(f" - silence hunting")
    segments = split_on_silence(normalize(data), 900, -40, keep_silence=400)
    
    if len(segments)==0:
        print(f"=== NO SPLITS FROM: {mp3}")
        splits.append("src/"+mp3)
        continue
    
    for i, segment in enumerate(segments):
        # Normalize the entire chunk.
        normalized = normalize(segment)
        
        # Trim off leading and trailing silence
        start_trim = detect_leading_silence(normalized, silence_threshold=-45)
        end_trim = detect_leading_silence(normalized.reverse(), silence_threshold=-45)
        duration = len(normalized)
        trimmed = normalized[start_trim:duration-end_trim]
        
        print(f"Saving mp3/{mp3}-{i:03d}.mp3.")
        trimmed.export(f"mp3/{mp3}-{i:03d}.mp3",bitrate="192k",format="mp3")
        splits.append(f"mp3/{mp3}-{i:03d}.mp3")

with open("see-say-write.txt", "w") as f:
    for mp3 in splits:
        if os.path.splitext(mp3)[1].lower()!=".mp3":
            continue
        f.write("df3") #speaker
        f.write("|")
        f.write(mp3) #audio file
        f.write("|")
        f.write("\n")
        
sys.exit()