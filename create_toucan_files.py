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


def main():
    ims_toucan_basename = "ims-toucan"
    data_sets: list[str] = ["cno", "durbin-feeling-tones", "michael-conrad", "michael-conrad2", "see-say-write", "walc-1", "wwacc"]
    # get list of languages
    langs: set[str] = set()
    voices: set[str] = set()
    for folder in data_sets:
        all_txt = os.path.join(folder, "all.txt")
        if not os.path.exists(all_txt):
            continue
        with open(all_txt) as r:
            for line in r:
                line = line.strip()
                parts = line.split("|")
                langs.add(parts[2])
                voices.add(parts[1])

    # create simple text file for use by IMS-Toucan, only selected data sets
    for lang in langs:
        output_file = f"{ims_toucan_basename}-{lang}.txt"
        with open(output_file, "w") as w:
            for folder in data_sets:
                all_txt = os.path.join(folder, "all.txt")
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
                        wav = os.path.join(folder, wav)
                        w.write(f"{wav}|{text}\n")

        # create simple text file with REF audio
        # for use by IMS-Toucan, only selected data sets

        voice_files: dict[str, str] = dict()
        voice_words: dict[str, int] = dict()
        voice_text: dict[str, str] = dict()
        for voice in voices:
            for folder in data_sets:
                all_txt = os.path.join(folder, "all.txt")
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
                shutil.copy(wav, os.path.join("_toucan_ref_audio", f"{voice}.wav"))


if __name__ == '__main__':
    main()
