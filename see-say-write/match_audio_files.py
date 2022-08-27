import re
from csv import DictReader, DictWriter
import shutil
from typing import Dict

import unidecode
FIELDS = ["has_problems", "vocab_set", "syllabary", "english", "cherokee", "audio"]

trigrams = lambda a: zip(a, a[1:], a[2:])
def trigram_similarity(a, b):
    a_t = set(trigrams(a))
    b_t = set(trigrams(b))
    return len(a_t & b_t) / len(a_t | b_t)

def minify_pronounce(rich: str):
    return unidecode.unidecode(re.sub(r'[\:ɂ]', "", rich)).lower()

def load_data():
    indexed_data: Dict[str, Dict[str, str]] = {}
    with open('data-chr.txt') as f:
        reader = DictReader(f, ["speaker", "file", "pronunciation"], delimiter="|")
        for row in reader:
            key = minify_pronounce(row["pronunciation"])
            print(key, row)
            indexed_data[minify_pronounce(key)] = row
    
    return indexed_data

def top_n_entries(query: str, data: Dict[str, Dict[str, str]], n: int):
    sorted_data = sorted(data.keys(), key=lambda pronounce: trigram_similarity(query, pronounce), reverse=True)
    return sorted_data[:n]


def match_online_exercises_data(indexed_data: Dict[str, Dict[str, str]]):
    out = 'online-exercises-data-new.csv'
    with open('online-exercises-data.csv') as infile, open(out, 'w') as outfile:
        reader = DictReader(infile, FIELDS, delimiter='|')
        writer = DictWriter(outfile, FIELDS, delimiter='|')
        for row in reader:
            if not row["audio"]:
                if row["has_problems"] == "":
                    # search by cherokee that is in there
                    print(f"--- select match for {row['cherokee']} / {row['english']} ---")
                    results = top_n_entries(row["cherokee"], indexed_data, 10)
                    for idx, result in enumerate(results):
                        print(f"{idx}) {indexed_data[result]['pronunciation']}")
                    
                    selected_row = input("Match index: ")

                    if selected_row:
                        match = indexed_data[results[int(selected_row)]]
                        print(match["file"])

                        row["audio"] = match["file"]
                        row["cherokee"] = match["pronunciation"]
                    else:
                        row["has_problems"] = "*"
            
            writer.writerow(row)

    shutil.move('online-exercises-data.csv', 'online-exercises-data.back')
    shutil.move(out, 'online-exercises-data.csv')
        

def main():
    running = True
    indexed_data = load_data()
    
    match_online_exercises_data(indexed_data)

    # entries = []

    # entries.append({
    #     "cherokee": match["pronunciation"],
    #     "syllabary": syllabary,
    #     "alternate_pronunciations": [],
    #     "alternate_syllabary": [],
    #     "english": english,
    #     "cherokee_audio": [match["file"]],
    #     "english_audio": []
    # })

    # outname = input("vocab_set name: ")

    # json.dump(entries, open(outname+'.json', 'w'), ensure_ascii=False)

if __name__ == '__main__':
    main()