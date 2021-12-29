import json
import os
import sys

if __name__ == "__main__":

    voice_ranges: dict = dict()
    if os.path.exists("voice-ranges.json"):
        with open("voice-ranges.json", "r") as f:
            for (range_start, voice_id) in json.loads(f.read())["ranges"]:
                voice_ranges[int(range_start)] = voice_id

    print(voice_ranges)

    aligned_text: str = "aligned.txt"
    output_text_chr: str = "data-chr.txt"
    output_text_en: str = "data-en.txt"

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
            if line.strip().lower().startswith("#end"):
                break
            if line.strip().startswith("#"):
                continue
            lines.append(line.strip())
    print(f"Loaded {len(lines):,} text aligments")

    print(f"{int(100 * len(lines) / len(mp3s)):,}%")

    entries_chr: list = list()
    entries_en: list = list()

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
        fields: list[str] = [line, "", ""]
        if "|" in line:
            fields = line.split("|")
            if len(fields) == 2:
                fields.append("")

        tts_chr_text: str = fields[0].strip()
        tts_en_text: str = fields[1].strip()
        mp3_check: str = fields[2].strip()

        if mp3_check and mp3_check != mp3:
            raise Exception(
                f"Alignment fail [{line_no}] mp3={mp3} marker={mp3_check} text={tts_chr_text}/{tts_en_text}")
        if "x" in tts_chr_text:
            continue
        if tts_chr_text:
            entries_chr.append((voice, os.path.join("mp3", mp3), tts_chr_text))
        elif tts_en_text:
            entries_en.append((voice, os.path.join("mp3", mp3), tts_en_text))
        count += 1

    with open(output_text_chr, "w") as f:
        voice: str
        mp3: str
        tts_text: str
        for (voice, mp3, tts_text) in entries_chr:
            print(f"{voice}|{mp3}|{tts_text}", file=f)

    with open(output_text_en, "w") as f:
        voice: str
        mp3: str
        tts_text: str
        for (voice, mp3, tts_text) in entries_en:
            print(f"{voice}|{mp3}|{tts_text}", file=f)
