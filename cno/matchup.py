#!/usr/bin/env python3
import string

if __name__ == "__main__":
    import os
    import sys
    import csv
    import codecs
    import re
    
    from chrutils import ascii_ced2mco
    from chrutils import ascii_ced2ced
    
    dname = os.path.dirname(sys.argv[0])
    if len(dname) > 0:
        os.chdir(dname)
        
    syllabaryList:tuple = ("syllabaryb", 'nounadjpluralsyllf', 'vfirstpresh', 'vsecondimpersylln', 'vthirdinfsyllp', 'vthirdpressylll', 'vthirdpastsyllj')
    pronounceList:tuple = ("entrytone", 'nounadjpluraltone', 'vfirstprestone', 'vsecondimpertone', 'vthirdinftone', 'vthirdprestone', 'vthirdpasttone')
        
    ced:str = "ced_202010301607.csv"
    rrd:str = "rrd_202010301608.csv"
    cno:str = "cnos_202010301611.csv"
    
    ced_lookup:dict = dict()
    rrd_lookup:dict = dict()
    cno_lookup:dict = dict()
    mp3_lookup:dict = dict()
    
    ambig:dict = dict()
    
    with open(ced, mode='r', encoding='utf-8-sig') as csvfile:
        records = csv.DictReader(csvfile)
        for record in records:
            for fields in zip(syllabaryList, pronounceList):
                sfield:str = fields[0]
                pfield:str = fields[1]
                value:str = record[sfield].strip().strip(",")
                pronounce:str = record[pfield].strip().strip(",")
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
                sfield:str = fields[0]
                pfield:str = fields[1]
                value:str = record[sfield].strip()
                pronounce:str = record[pfield].strip()
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
    
    with open(cno, mode='r', encoding='utf-8-sig') as csvfile:
        records = csv.DictReader(csvfile)
        for record in records:
            for fields in zip(syllabaryList, pronounceList):
                sfield:str = fields[0]
                pfield:str = fields[1]
                value:str = record[sfield].strip()
                if "-" in value:
                    continue                
                if len(value) == 0:
                    continue
                if value in ambig.keys():
                    continue
                if value in ced_lookup.keys():
                    cno_lookup[value] = ced_lookup[value]
                    mp3_lookup[value] = record["notes"]
                    continue
                if value in rrd_lookup.keys():
                    cno_lookup[value] = rrd_lookup[value]
                    mp3_lookup[value] = record["notes"]
                    continue
                if value + "Ꭲ" not in ambig.keys():
                    if value + "Ꭲ" in ced_lookup.keys():
                        pronounce = ced_lookup[value + "Ꭲ"][:-1]
                        while pronounce[-1] in "?ɂ2":
                            pronounce = pronounce[:-1]
                        cno_lookup[value] = pronounce
                        mp3_lookup[value] = record["notes"]
                        continue
                    if value + "Ꭲ" in rrd_lookup.keys():
                        pronounce = rrd_lookup[value + "Ꭲ"][:-1]
                        while pronounce[-1] in "?ɂ2":
                            pronounce = pronounce[:-1]
                        cno_lookup[value] = pronounce
                        mp3_lookup[value] = record["notes"]
                        continue
                if value + "Ꭽ" not in ambig.keys():
                    if value + "Ꭽ" in ced_lookup.keys():
                        pronounce = ced_lookup[value + "Ꭽ"][:-2]
                        while pronounce[-1] in "?ɂ2":
                            pronounce = pronounce[:-1]
                        cno_lookup[value] = pronounce
                        mp3_lookup[value] = record["notes"]
                        print(f"{value}[Ꭽ] = {pronounce}")
                        continue
                    if value + "Ꭽ" in rrd_lookup.keys():
                        pronounce = rrd_lookup[value + "Ꭽ"][:-2]
                        while pronounce[-1] in "?ɂ2":
                            pronounce = pronounce[:-1]
                        cno_lookup[value] = pronounce
                        mp3_lookup[value] = record["notes"]
                        print(f"{value}[Ꭽ] = {pronounce}")
                        continue
                if value + "Ꮬ" not in ambig.keys():
                    if value + "Ꮬ" in ced_lookup.keys():
                        pronounce = ced_lookup[value + "Ꮬ"][:-3]
                        print(f"{value}[Ꮬ] = {pronounce}")
                        while pronounce[-1] in "?ɂ2":
                            pronounce = pronounce[:-1]
                        cno_lookup[value] = pronounce
                        mp3_lookup[value] = record["notes"]
                        continue
                    if value + "Ꮬ" in rrd_lookup.keys():
                        pronounce = rrd_lookup[value + "Ꮬ"][:-3]
                        print(f"{value}[Ꮬ] = {pronounce}")
                        while pronounce[-1] in "?ɂ2":
                            pronounce = pronounce[:-1]
                        cno_lookup[value] = pronounce
                        mp3_lookup[value] = record["notes"]
                        continue
                if value + "Ꭰ" not in ambig.keys():
                    if value + "Ꭰ" in ced_lookup.keys():
                        pronounce = ced_lookup[value + "Ꭰ"][:-1]
                        while pronounce[-1] in "?ɂ2":
                            pronounce = pronounce[:-1]
                        cno_lookup[value] = pronounce
                        mp3_lookup[value] = record["notes"]
                        continue
                    if value + "Ꭰ" in rrd_lookup.keys():
                        pronounce = rrd_lookup[value + "Ꭰ"][:-1]
                        print(f"{value}[Ꭽ] = {pronounce}")
                        while pronounce[-1] in "?ɂ2":
                            pronounce = pronounce[:-1]
                        cno_lookup[value] = pronounce
                        mp3_lookup[value] = record["notes"]
                        continue
                if "Ꮧ" + value not in ambig.keys():
                    if "Ꮧ" + value in ced_lookup.keys():
                        pronounce = "di2" + ced_lookup["Ꮧ" + value]
                        cno_lookup[value] = pronounce
                        mp3_lookup[value] = record["notes"]
                        continue
                    if "Ꮧ" + value in rrd_lookup.keys():
                        pronounce = "di2" + rrd_lookup["Ꮧ" + value]
                        print(f"{value}[Ꭽ] = {pronounce}")
                        cno_lookup[value] = pronounce
                        mp3_lookup[value] = record["notes"]
                        continue
                if value[-1] == "Ꮫ":
                    xvalue = value[:-1] + "Ꮣ"
                    if xvalue not in ambig.keys():
                        if xvalue in ced_lookup.keys():
                            pronounce = ced_lookup[xvalue]
                            pronounce = pronounce[:-1] + "v"
                            cno_lookup[value] = pronounce
                            mp3_lookup[value] = record["notes"]
                            continue
                        if xvalue in rrd_lookup.keys():
                            pronounce = rrd_lookup[xvalue]
                            pronounce = pronounce[:-1] + "v"
                            cno_lookup[value] = pronounce
                            mp3_lookup[value] = record["notes"]
                            continue
        print(f"Found {len(cno_lookup)} matches.")
        
    with open("matches.txt", "w") as file:
        for key in cno_lookup.keys():
            pronounce = cno_lookup[key]
            mp3 = mp3_lookup[key].replace("https://data.cherokee.org/Cherokee/LexiconSoundFiles/", "")
            mco = ascii_ced2mco(pronounce)
            pced = ascii_ced2ced(pronounce)
            print(f"{key}|{pced}|{mco}|{mp3}|", file=file)
    
    with open(cno, mode='r', encoding='utf-8-sig') as csvfile:
        with open("cno-web.txt", "w") as file:
            pkey = "entrya"
            records = csv.DictReader(csvfile)
            for record in records:
                pronounce = record[pkey].strip().lower()
                if "ts" in pronounce:
                    continue
                for v in "aeiouv":
                    pronounce = pronounce.replace(v, v+"\u030a")
                if pronounce[-1] == "\u030a":
                    pronounce = pronounce[:-1]
                
                mp3:string = record["notes"].replace("https://data.cherokee.org/Cherokee/LexiconSoundFiles/", "")
                print(f"{pronounce}|{mp3}|", file=file)
                
    with open(cno, mode='r', encoding='utf-8-sig') as csvfile:
        with open("cno-web-syl.txt", "w") as file:
            pkey = "syllabaryb"
            records = csv.DictReader(csvfile)
            for record in records:
                text = record[pkey].strip().upper()
                mp3:string = record["notes"].replace("https://data.cherokee.org/Cherokee/LexiconSoundFiles/", "")
                print(f"{text}|{mp3}|", file=file)
            
