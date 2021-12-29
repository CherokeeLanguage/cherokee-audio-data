#!/usr/bin/env python3

if __name__ == "__main__":
    import os
    import sys
    import csv
    import re

    dname = os.path.dirname(sys.argv[0])
    if len(dname) > 0:
        os.chdir(dname)

    syllabaryList: tuple = (
    "syllabaryb", 'nounadjpluralsyllf', 'vfirstpresh', 'vsecondimpersylln', 'vthirdinfsyllp', 'vthirdpressylll',
    'vthirdpastsyllj')
    pronounceList: tuple = (
    "entrytone", 'nounadjpluraltone', 'vfirstprestone', 'vsecondimpertone', 'vthirdinftone', 'vthirdprestone',
    'vthirdpasttone')

    ced: str = "ced_202010301607.csv"
    rrd: str = "rrd_202010301608.csv"
    cno: str = "cnos_202010301611.csv"

    ced_lookup: dict = dict()
    rrd_lookup: dict = dict()
    cno_lookup: dict = dict()
    mp3_lookup: dict = dict()

    ambig: dict = dict()

    with open(ced, mode='r', encoding='utf-8-sig') as csvfile:
        records = csv.DictReader(csvfile)
        for record in records:
            for fields in zip(syllabaryList, pronounceList):
                sfield: str = fields[0]
                pfield: str = fields[1]
                value: str = record[sfield].strip().strip(",")
                pronounce: str = record[pfield].strip().strip(",")
                if "-" in value or "-" in pronounce:
                    continue
                if len(value) == 0:
                    continue
                if len(pronounce) == 0:
                    continue
                if value in ambig.keys():
                    continue
                if value in ced_lookup.keys() and pronounce != ced_lookup[value]:
                    ambig[value] = True
                    ced_lookup.pop(value)
                    continue
                ced_lookup[value] = pronounce

    for key in [*ced_lookup]:
        if " " not in key and "," not in key:
            continue
        pronounce = ced_lookup[key]
        if " " not in pronounce and "," not in pronounce:
            continue
        if len(key.split(",")) != len(pronounce.split(",")):
            continue
        if len(key.split(" ")) != len(pronounce.split(" ")):
            continue
        for new_key, new_pronounce in zip(key.split(","), pronounce.split(",")):
            new_key = new_key.strip()
            new_pronounce = new_pronounce.strip()
            if new_key in ced_lookup.keys():
                continue
            ced_lookup[new_key] = new_pronounce
        for new_key, new_pronounce in zip(key.split(" "), pronounce.split(" ")):
            new_key = new_key.strip().strip(" ,")
            new_pronounce = new_pronounce.strip().strip(" ,")
            if new_key in ced_lookup.keys():
                continue
            ced_lookup[new_key] = new_pronounce

    with open(rrd, mode='r', encoding='utf-8-sig') as csvfile:
        records = csv.DictReader(csvfile)
        for record in records:
            for fields in zip(syllabaryList, pronounceList):
                sfield: str = fields[0]
                pfield: str = fields[1]
                value: str = record[sfield].strip()
                pronounce: str = record[pfield].strip()
                if "-" in value or "-" in pronounce:
                    continue
                if len(value) == 0:
                    continue
                if len(pronounce) == 0:
                    continue
                if value in ambig.keys():
                    continue
                if value in rrd_lookup.keys() and pronounce != rrd_lookup[value]:
                    ambig[value] = True
                    rrd_lookup.pop(value)
                    continue
                # convert RRD to CED formatting
                pronounce = re.sub("(?i)([aeiouv])([a-zɂ?])", "\\g<1>2\\g<2>", pronounce, flags=re.IGNORECASE)
                pronounce = re.sub("(?i)([ạẹịọụ])([a-zɂ?])", "\\g<1>2\\g<2>", pronounce, flags=re.IGNORECASE)
                pronounce = re.sub("(?i)(ṿ)([a-zɂ?])", "\\g<1>2\\g<2>", pronounce, flags=re.IGNORECASE)
                rrd_lookup[value] = pronounce

    for key in [*rrd_lookup]:
        if " " not in key and "," not in key:
            continue
        pronounce = rrd_lookup[key]
        if " " not in pronounce and "," not in pronounce:
            continue
        if len(key.split(",")) != len(pronounce.split(",")):
            continue
        if len(key.split(" ")) != len(pronounce.split(" ")):
            continue
        for new_key, new_pronounce in zip(key.split(","), pronounce.split(",")):
            new_key = new_key.strip()
            new_pronounce = new_pronounce.strip()
            if new_key in rrd_lookup.keys():
                continue
            rrd_lookup[new_key] = new_pronounce
        for new_key, new_pronounce in zip(key.split(" "), pronounce.split(" ")):
            new_key = new_key.strip().strip(" ,")
            new_pronounce = new_pronounce.strip().strip(" ,")
            if new_key in rrd_lookup.keys():
                continue
            rrd_lookup[new_key] = new_pronounce

    print(f"Skipped loading {len(ambig):,} ambiguous entries from main dictionary files")

    ced_keys = [*ced_lookup]
    with open(cno, mode='r', encoding='utf-8-sig') as csvfile:
        records = csv.DictReader(csvfile)
        for record in records:
            sfield: str = ""
            pfield: str = ""
            for sfield, pfield in zip(syllabaryList, pronounceList):
                value: str = record[sfield].strip()
                if "-" in value:
                    continue
                if len(value) == 0:
                    continue
                print(value)
                if value in ced_keys:
                    continue
                if value + "Ꭲ" in ced_keys:
                    continue
                if value + "Ꭽ" in ced_keys:
                    continue
                for key in [*ced_lookup]:
                    if len(key) > len(value) + 1:
                        continue
                    if value in key:
                        if value not in cno_lookup:
                            cno_lookup[value] = set()
                        cno_lookup[value].add(key)
        #                 for key in [*rrd_lookup]:
        #                     if key in [*ced_lookup]:
        #                         continue
        #                     if value in key:
        #                         if value not in cno_lookup:
        #                             cno_lookup[value]=list()
        #                         cno_lookup[value].append(key)
        #                         break

        print(f"Found {len(cno_lookup)} maybe matches.")

    with open("maybe-matches.txt", "w") as file:
        for key in cno_lookup.keys():
            pronounce = cno_lookup[key]
            mp3 = ""  # mp3_lookup[key].replace("https://data.cherokee.org/Cherokee/LexiconSoundFiles/", "")
            list = cno_lookup[key]
            print(f"{key}|{mp3}|{list}", file=file)
