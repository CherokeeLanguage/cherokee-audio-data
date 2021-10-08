#!/usr/bin/env python3

if __name__ == "__main__":

    import os
    import sys
    import unicodedata as ud
    import re
    import random

    ced_text: str = "../ced-mco.txt"
    output_text: str = "ced-flat-short-fs.txt"

    workdir: str = os.path.dirname(sys.argv[0])
    if workdir.strip() != "":
        os.chdir(workdir)
    workdir = os.getcwd()

    from os import walk
    
    entries:list=[]
    with open(ced_text, "r") as f:
        for line in f:
            line = ud.normalize("NFC", line)
            fields:list
            fields = line.split("|")
            if len(fields)<8:
                continue
            field:str
            for field in fields[1:8]:
                if len(field.strip())==0:
                    continue
                while field and field[-1].lower() in "aeiouvhw:.,?!":
                    field = field[:-1]
                if not field:
                    continue
                if not re.search("(?i)[aeiouv]", field):
                    continue
                if re.match("(?i)^[a-z.?!,; ]+$", field):
                    entries.append(field)

    random.Random(len(entries)).shuffle(entries)
    count:int=0
    with open(output_text, "w") as file:
        buffer:str=""
        for line in entries:
            line=line.strip()
            if not line[-1] in ";,.?!\"'":
                line += "."
            if len(buffer) > 0 and len(buffer) + len(line) + 1 > 80:
                count += 1
                print(buffer, file=file)
                buffer = line[0].upper()+line[1:]
            else:
                if buffer:
                    buffer += " "
                buffer += line[0].upper()+line[1:]
        if buffer:
            count += 1
            print(buffer, file=file)

    print(f"Output {len(entries):,} entries as {count:,} lines.")
