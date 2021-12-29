#!/usr/bin/env python3
import os
import pathlib
import re
import sys
from builtins import list
from shutil import rmtree

import progressbar
import pydub.effects as effects
from pydub import AudioSegment

if __name__ == "__main__":

    if sys.argv[0].strip() != "" and os.path.dirname(sys.argv[0]) != "":
        os.chdir(os.path.dirname(sys.argv[0]))

    training_text = "training1.txt"
    wavs_dir = "training_wavs"

    rmtree(wavs_dir, ignore_errors=True)
    pathlib.Path(".").joinpath(wavs_dir).mkdir(exist_ok=True)

    lines: list = list()
    with open(training_text, "r") as f:
        for line in f:
            lines.append(line.strip())

    bar = progressbar.ProgressBar(len(lines))
    bar.start()
    for line in lines:
        fields = line.split("|")
        if len(fields) < 10:
            continue
        # ID|PSET|DIALOG|PRONOUN|VERB|GENDER|SYLLABARY|PRONOUNCE|ENGLISH|AUDIO FILE
        audio_file = fields[9]
        if not os.path.exists(audio_file):
            continue
        output_file: str = fields[7].lower().strip()
        output_file = re.sub("(?i)[^a-z\\s_]", "", output_file)
        output_file = re.sub("(?i)(.):", "\\1\\1", output_file)
        output_file = re.sub("(?i)\\s+", "_", output_file)
        segment: AudioSegment = AudioSegment.from_file(audio_file)
        segment = segment.set_frame_rate(22050)
        segment = segment.set_channels(1)
        segment = effects.normalize(segment)
        segment.export(os.path.join(wavs_dir, output_file + ".wav"), format="wav")
        bar.update(bar.currval + 1)
    bar.finish()
    sys.exit()
