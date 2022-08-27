import os
import shutil
import subprocess
from typing import Dict, List
from match_audio_files import FIELDS
from csv import DictReader
import json

def read_file():
    cards_by_vocab_set: Dict[str, List[Dict[str, str]]] = {}
    with open("online-exercises-data.csv") as f:
        reader = DictReader(f, FIELDS, delimiter="|")
        for row in reader:
            if row["has_problems"] == "*":
                continue
            new_card = {
                "cherokee": row["cherokee"],
                "syllabary": row["syllabary"],
                "alternate_pronunciations": [],
                "alternate_syllabary": [],
                "english": row["english"],
                "cherokee_audio": [row["audio"]],
                "english_audio": []
            }
            if row["vocab_set"] in cards_by_vocab_set:
                cards_by_vocab_set[row["vocab_set"]].append(new_card)
            else:
                cards_by_vocab_set[row["vocab_set"]] = [new_card]
        
    return cards_by_vocab_set

def change_path(localpath: str):
    return localpath.replace('mp3/', 'ssw-audio/', 1)

def main():
    cards_by_vocab_set = read_file()
    collection_id = "SEE_SAY_WRITE"
    vocab_sets = [{
        "id": f"{collection_id}:{key}",
        "title": f"Lessons {key}",
        "terms": [card["cherokee"] for card in cards]
    } for key, cards in cards_by_vocab_set.items()]

    all_cards = []
    os.makedirs("ssw-audio", exist_ok=True)
    for set_cards in cards_by_vocab_set.values():
        for card in set_cards:
            oldpath = card["cherokee_audio"][0]
            newpath = change_path(oldpath)
            shutil.copy(oldpath, newpath)
            all_cards.append({**card, "cherokee_audio": [newpath]})
            

    json.dump(all_cards, open("ssw-cards.json", "w"), ensure_ascii=False)
    json.dump({
        "id": collection_id,
        "title": "See Say Write",
        "sets": vocab_sets
    }, open("ssw.json", "w"), ensure_ascii=False)

    subprocess.run(["zip", "ssw.zip", "ssw.json", "ssw-cards.json", "-r", "./ssw-audio"])

    

if __name__ == "__main__":
    main()