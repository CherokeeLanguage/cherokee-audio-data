import glob
import os
import subprocess
import sys


def main():
    argv0: str = sys.argv[0]
    if argv0:
        workdir: str = os.path.dirname(argv0)
        if workdir:
            os.chdir(workdir)

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


if __name__ == "__main__":
    main()
