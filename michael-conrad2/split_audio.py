#!/usr/bin/env python3

from pydub import AudioSegment

def detect_sound(sound:AudioSegment, silence_threshold:float=-55.0, chunk_size:int=150)->list:
    '''
    sound is a pydub.AudioSegment
    silence_threshold in dB
    chunk_size in ms
    iterate over entire AudioSegment looking for non-silent chunks
    returns list of chunks as a list of tuples (begin, end). In milliseconds.
    returns an empty list of no sound chunks found
    '''
    sound_start:int = -1
    segments:list=list()
    
    for position in range(0, len(sound), 10): #process in 10 ms chunks
        segment_end:int=min(position+chunk_size, len(sound))
        segment_mid:int=min(position+chunk_size/2, len(sound))
        nextChunk:AudioSegment=sound[position:segment_end]
        if sound_start < 0 and nextChunk.dBFS <= silence_threshold:
            continue
        if sound_start < 0:
            sound_start=segment_mid
            continue
        if sound_start >= 0 and nextChunk.dBFS <= silence_threshold:
            segments.append((sound_start, segment_mid))
            sound_start=-1
            continue
        
    if sound_start >= 0:
        segments.append((sound_start, segment_mid))
        
    if len(segments) == 0:
        segments.append((0, len(sound)))
        
    return segments

def combine_segments(segments:list, target_length:int)->list:
    new_segments:list=list()
    
    if len(segments)==0:
        return list()
    
    if len(segments)==1:
        new_segments.append(segments[0])
        return new_segments
    
    start = segments[0][0]
    end = segments[0][1]
    
    for ix in range(1, len(segments)):
        if segments[ix][1] - start < target_length:
            end=segments[ix][1]
            continue
        new_segments.append((start, end))
        start=segments[ix][0]
        end=segments[ix][1]
        
    if new_segments[-1][0] != start:
        new_segments.append((start, end)) 
    
    return new_segments

if __name__ == "__main__":
        
    import os
    import sys
    import unicodedata as ud
    import random
    import re
    import pathlib
    import subprocess
    from shutil import rmtree
    from builtins import list
    from pydub.effects import normalize
    
    silence_threshold:float=-55.0
    silence_min_duration:int=150 #ms
    max_target_duration:int=9000 #ms
    
    workdir:str = os.path.dirname(sys.argv[0])
    if workdir.strip() != "":
        os.chdir(workdir)
    workdir = os.getcwd()
    
    #clean up any previous files
    rmtree("mp3", ignore_errors=True)
    os.mkdir("mp3")
    
    from os import walk
    mp3s = []
    for (dirpath, dirnames, filenames) in walk("src"):
        mp3s.extend(filenames)
        break
    mp3s.sort()
    splits:list=[]
    tix:int=1
    min_length:float=-1.0
    max_length:float=0.0
    total_length:float=0.0
    for mp3 in mp3s:
        if os.path.splitext(mp3)[1].lower()!=".mp3":
            continue
        print(f"Processing {mp3}")
                    
        mp3=os.path.splitext(mp3)[0]
        data = AudioSegment.from_mp3("src/" + mp3+".mp3").set_channels(1)
        
        print(f" - segment hunting")
        segments = detect_sound(data, silence_threshold, silence_min_duration)
        
        segments = combine_segments(segments, max_target_duration)
        
        if len(segments)==0:
            print(f"=== ONLY SILENCE FOUND IN: {mp3}")
            continue
        
        for segment_start, segment_end in segments:
            chunk_mp3 = f"{tix:04d}-{mp3}"
            tix+=1
            # Normalize the chunk.
            normalized:AudioSegment = normalize(data[segment_start:segment_end])
            
            #duration = len(normalized)
            
            print(f"Saving mp3/{chunk_mp3}-{int(segment_start):06d}.mp3.")
            normalized.export(f"mp3/{chunk_mp3}-{int(segment_start):06d}.mp3",bitrate="192k",format="mp3")
            splits.append(f"mp3/{chunk_mp3}-{int(segment_start):06d}.mp3")
            
            duration:float = normalized.duration_seconds
            total_length+=duration
            if min_length < 0 or min_length>duration:
                min_length = duration
            if max_length < duration:
                max_length = duration
    
    with open("split_audio.txt", "w") as f:
        for mp3 in splits:
            if os.path.splitext(mp3)[1].lower()!=".mp3":
                continue
            f.write("?") #speaker
            f.write("|")
            f.write(mp3) #audio file
            f.write("|")
            f.write("\n")
            
    print()
    print(f"Work directory: {workdir}")
    print()
    print(f"Total splits: {len(splits):,}")
    print()
    print(f"Min duration: {min_length:,.02f} seconds")
    print(f"Max duration: {max_length:,.02f} seconds")
    print(f"Total duration: {total_length:,.02f} seconds")
    print()
            
    sys.exit()