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


def main():
    ims_toucan_basename = "ims-toucan"
    # data_sets: list[str] = ["cno", "durbin-feeling-tones", "michael-conrad", "see-say-write", "walc-1", "wwacc"]
    data_sets: list[str] = ["cno", "durbin-feeling-tones", "michael-conrad", "michael-conrad2", "walc-1"]
    # get list of languages
    langs: set[str] = set()
    for folder in data_sets:
        all_txt = os.path.join(folder, "all.txt")
        if not os.path.exists(all_txt):
            continue
        with open(all_txt) as r:
            for line in r:
                line = line.strip()
                parts = line.split("|")
                langs.add(parts[2])

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


if __name__ == '__main__':
    main()
