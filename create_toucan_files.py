#!/usr/bin/env bash
"""true" '''\'
set -e
eval "$(conda shell.bash hook)"
conda deactivate
conda activate cherokee-audio-data
exec python "$0" "$@"
exit $?
''"""
import os
import shutil

from pydub import AudioSegment
from pydub.silence import split_on_silence


def main():
    ims_toucan_basename = "ims-toucan"
    data_sets: list[str] = ["cno", "durbin-feeling-tones",
                            "michael-conrad", "michael-conrad2",
                            "walc-1"]  #, "wwacc"]
    # get list of languages
    langs: set[str] = set()
    voices: set[str] = set()
    for folder in data_sets:
        # for all_txt in ["all.txt", "all-augmented.txt"]:
        for all_txt in ["all-augmented.txt"]:
            all_txt = os.path.join(folder, all_txt)
            if not os.path.exists(all_txt):
                continue
            with open(all_txt) as r:
                for line in r:
                    line = line.strip()
                    parts = line.split("|")
                    langs.add(parts[2])
                    voices.add(parts[1])

    # create simple text file for use by IMS-Toucan, only selected data sets
    already: set[str] = set()
    for lang in langs:
        output_file = f"{ims_toucan_basename}-{lang}.txt"
        with open(output_file, "w") as w:
            for folder in data_sets:
                # for all_txt in ["all.txt", "all-augmented.txt"]:
                for all_txt in ["all-augmented.txt"]:
                    all_txt = os.path.join(folder, all_txt)
                    if not os.path.exists(all_txt):
                        continue
                    with open(all_txt) as r:
                        for line in r:
                            line = line.strip()
                            parts = line.split("|")
                            if parts[2] != lang:
                                continue
                            wav = parts[3]
                            text = parts[6]
                            if text in already:
                                continue
                            already.add(text)
                            wav = os.path.join(folder, wav)
                            w.write(f"{wav}|{text}\n")

        # create simple text file with REF audio
        # for use by IMS-Toucan, only selected data sets

        voice_files: dict[str, str] = dict()
        voice_words: dict[str, int] = dict()
        voice_text: dict[str, str] = dict()
        for voice in voices:
            for folder in data_sets:
                # for all_txt in ["all.txt", "all-augmented.txt"]:
                for all_txt in ["all-augmented.txt"]:
                    all_txt = os.path.join(folder, all_txt)
                    if not os.path.exists(all_txt):
                        continue
                    with open(all_txt) as r:
                        for line in r:
                            line = line.strip()
                            parts = line.split("|")
                            if parts[1] != voice:
                                continue
                            wav = parts[3]
                            text = parts[6]
                            wav = os.path.join(folder, wav)
                            if voice not in voice_words:
                                voice_text[voice] = text.strip()
                                voice_words[voice] = text.strip().count(" ")
                                voice_files[voice] = wav
                            word_cnt: int = text.strip().count(" ")
                            if word_cnt < voice_words[voice]:
                                continue
                            voice_text[voice] = text.strip()
                            voice_words[voice] = word_cnt
                            voice_files[voice] = wav
        shutil.rmtree("_toucan_ref_audio", ignore_errors=True)
        os.mkdir("_toucan_ref_audio")
        output_file = f"{ims_toucan_basename}-voices.txt"
        with open(output_file, "w") as w:
            for voice_file in voice_files.items():
                voice: str = voice_file[0]
                wav: str = voice_file[1]
                text: str = voice_text[voice]
                w.write(f"{voice}|{wav}|{text}")
                w.write("\n")
                ref_audio: AudioSegment = AudioSegment.from_file(wav).set_channels(1)
                ref_chunks = split_on_silence(ref_audio, min_silence_len=100, silence_thresh=-40, keep_silence=100)
                ref_audio: AudioSegment = AudioSegment.empty()
                for ref_chunk in ref_chunks:
                    ref_audio = ref_audio.append(ref_chunk, crossfade=0)
                ref_audio.export(os.path.join("_toucan_ref_audio", f"{voice}.wav"), format="wav")
                # shutil.copy(wav, os.path.join("_toucan_ref_audio", f"{voice}.wav"))


if __name__ == '__main__':
    main()
