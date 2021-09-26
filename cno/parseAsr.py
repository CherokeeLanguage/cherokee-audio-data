#!/usr/bin/env python3

if __name__ == "__main__":
    import os
    import sys
    import csv
    import codecs
    import re
    import json
    
    from chrutils import ascii_ced2mco
    from chrutils import ascii_ced2ced
    
    dname=os.path.dirname(sys.argv[0])
    if len(dname)>0:
        os.chdir(dname)
    
    mp3_lookup:dict=dict()
    
    with open("entries-timestamps.txt") as file:
        for line in file:
            fields=line.strip().split("|")
            idx=fields[0]
            start_time=float(fields[1])
            mp3=fields[2].replace("cno_cwl/", "")
            mp3_lookup[start_time]=mp3
    mp3_starttimes:list=[*mp3_lookup]
    mp3_starttimes.sort()
            
    asr_lookup:dict=dict()
    with open("asrOutput.json") as file:
        object = json.load(file)
        results=object["results"]
        speaker_labels=results["speaker_labels"]
        segments=speaker_labels["segments"]
        for segment in segments:
            start_time=float(segment["start_time"])
            speaker_label=segment["speaker_label"]
            end_time=float(segment["end_time"])
            asr_lookup[end_time]=speaker_label
    asrEndTimes:list=[*asr_lookup]
    asrEndTimes.sort()
    
    with open ("mp3-speaker-lookup.txt", "w") as file:
        for start_time in mp3_starttimes:
            speaker:str=asr_lookup[asrEndTimes[0]]
            for end_time in asrEndTimes:
                speaker=asr_lookup[end_time]
                if start_time > end_time:
                    continue
                print(f"chr|cno-{speaker}|{mp3_lookup[start_time]}|", file=file)
                break
            

    