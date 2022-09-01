from dataclasses import dataclass
import os
import re
from csv import DictReader, DictWriter
import shutil
from typing import Dict, List
import json

import unidecode
from pydub import AudioSegment
from pydub.effects import normalize

from structs import SplitMetadata

FIELDS = ["has_problems", "vocab_set", "syllabary", "english", "cherokee", "audio"]

trigrams = lambda a: zip(a, a[1:], a[2:])
def trigram_similarity(a, b):
    a_t = set(trigrams(a))
    b_t = set(trigrams(b))
    return len(a_t & b_t) / len(a_t | b_t)

def minify_pronounce(rich: str):
    return unidecode.unidecode(re.sub(r'[\:ɂ]', "", rich)).lower()

@dataclass
class SplitWithPronounce:
    split: SplitMetadata
    pronunciation: str

def load_data():
    indexed_data: Dict[str, SplitWithPronounce] = {}
    with open('split_metadata.json') as f:
        splits: Dict[str, SplitMetadata] = {split.out_file: split for split in (SplitMetadata(**metadict) for metadict in json.load(f))}
    with open('data-chr.txt') as f:
        reader = DictReader(f, ["speaker", "file", "pronunciation"], delimiter="|")
        for row in reader:
            key = minify_pronounce(row["pronunciation"])
            split = splits.get(row["file"], None)
            if not split:
                print("Missing split for", key, row["file"])
                continue
            indexed_data[minify_pronounce(key)] = SplitWithPronounce(split=split, pronunciation=row["pronunciation"])
    
    ordered_data = sorted((split for split in indexed_data.values()), key=lambda s: (s.split.source_file, s.split.start))

    return indexed_data, ordered_data

def top_n_entries(query: str, data: Dict[str,SplitWithPronounce], n: int):
    sorted_data = sorted(data.keys(), key=lambda pronounce: trigram_similarity(query, pronounce), reverse=True)
    return [data[k] for k in sorted_data[:n]]

def join_match_pronounce(matches: List[SplitWithPronounce]):
    return ' '.join(minify_pronounce(match.pronunciation) for match in matches)

def extend_matches(query: str, matches: List[SplitWithPronounce], ordered_data: List[SplitWithPronounce]) -> List[List[SplitWithPronounce]]:
    """
    Extend a list of matches by appending subsequent matching terms, taking the one with the best trigram similarity.
    """
    extended_matches: List[List[SplitWithPronounce]] = []
    for match in matches:
        best_match = [match]
        best_match_strength = trigram_similarity(query, join_match_pronounce(best_match))
        current_idx = ordered_data.index(match)
        for j in range(3):
            for i in range(3):
                extended_match = ordered_data[current_idx-j:current_idx+i]            
                extended_match_strength = trigram_similarity(query, join_match_pronounce(extended_match))

                if extended_match_strength >= best_match_strength:
                    best_match = extended_match
                    best_match_strength = extended_match_strength

        extended_matches.append(best_match)
    
    return extended_matches


def get_or_create_audio_for_pronounce(splits: List[SplitWithPronounce]):
    # if the audio file is just one segment; return that segment
    if len(splits) == 1:
        return splits[0].split.out_file
    
    source_files = set(split.split.source_file for split in splits)
    assert len(source_files) == 1, "All audio must be from the same file!"
    source, = source_files
    data: AudioSegment = AudioSegment.from_file(f"src/{source}").set_channels(1)
    normalized: AudioSegment = normalize(data[splits[0].split.start:splits[-1].split.end])
    source_base = os.path.splitext(os.path.split(source)[1])[0]
    output_file = f"ssw-audio/{source_base}-{join_match_pronounce(splits)}-bespoke.wav"
    normalized.export(output_file, format="mp3", parameters=["-qscale:a", "0"])
    return output_file


def match_online_exercises_data(indexed_data: Dict[str, SplitWithPronounce], ordered_data: List[SplitWithPronounce]):
    out = 'online-exercises-data-new.csv'
    with open('online-exercises-data.csv') as infile, open(out, 'w') as outfile:
        reader = DictReader(infile, FIELDS, delimiter='|')
        writer = DictWriter(outfile, FIELDS, delimiter='|')
        for row in reader:
            if not row["audio"]:
                if row["has_problems"] == "":
                    # search by cherokee that is in there
                    query = row["cherokee"]
                    print(f"--- select match for {query} / {row['english']} ---")
                    matches = top_n_entries(query, indexed_data, 5)
                    results = extend_matches(query, matches, ordered_data)
                    for idx, result in enumerate(results):
                        print(f"{idx}) {' '.join(m.pronunciation for m in result)}")
                    
                    selected_row = input("Match index: ")

                    if selected_row:
                        selected = results[int(selected_row)]
                        pronunciation = ' '.join(m.pronunciation for m in selected)
                        audio_file = get_or_create_audio_for_pronounce(selected)
                        row["audio"] = audio_file
                        row["cherokee"] = pronunciation
                    else:
                        row["has_problems"] = "*"
            
            writer.writerow(row)

    shutil.move('online-exercises-data.csv', 'online-exercises-data.back')
    shutil.move(out, 'online-exercises-data.csv')
        

def main():
    indexed_data, ordered_data = load_data()
    match_online_exercises_data(indexed_data, ordered_data)

if __name__ == '__main__':
    main()