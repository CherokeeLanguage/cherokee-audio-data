#!/usr/bin/env bash
"""true" '''\'
set -e
eval "$(conda shell.bash hook)"
conda deactivate
conda activate CherokeeTrainingData
exec python "$0" "$@"
exit $?
''"""

import glob
import os
import subprocess
import sys


def main():
    argv0: str = sys.argv[0]
    workdir: str
    if argv0:
        workdir: str = os.path.dirname(argv0)
        if workdir:
            os.chdir(workdir)
    workdir = os.getcwd()

    exec_list: list[str] = []
    exec_list.extend(glob.glob("*/create_tts_files.py"))
    exec_list.sort()
    for exec_filename in exec_list:
        print()
        print(f"=== {exec_filename}")

        script: str = f"""
                    PS1='$'
                    . ~/.bashrc
                    conda deactivate
                    conda activate CherokeeTrainingData
                    python "{exec_filename}"            
                    exit 0
                    """

        cp: subprocess.CompletedProcess = subprocess.run(script, shell=True, executable="/bin/bash", check=True)
        if cp.returncode > 0:
            raise Exception("Subprocess exited with ERROR")

    # create simple text file for use by IMS-Toucan, only selected data sets
    ims_toucan_file = "ims-toucan.txt"
    with open(ims_toucan_file, "w") as w:
        for folder in ["cno", "durbin-feeling-tones", "see-say-write", "walc-1", "wwacc"]:
            all_txt = os.path.join(folder, "all.txt")
            if not os.path.exists(all_txt):
                continue
            with open(all_txt) as r:
                for line in r:
                    line = line.strip()
                    parts = line.split("|")
                    lang = parts[2]
                    if lang != "chr":
                        continue
                    wav = parts[3]
                    text = parts[6]
                    wav = os.path.join(workdir, folder, wav)
                    w.write(f"{wav}|{text}\n")


if __name__ == "__main__":
    main()
