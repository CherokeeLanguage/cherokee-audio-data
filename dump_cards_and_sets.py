import os
import shutil
import subprocess
from sys import argv
from typing import Dict, List
from match_audio_files import FIELDS
from csv import DictReader
import json

from online_exercises_meta import COLLECTIONS, CollectionMeta

def read_file(folder: str):
    cards_by_vocab_set: Dict[str, List[Dict[str, str]]] = {}
    with open(os.path.join(folder, "online-exercises-data.csv")) as f:
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
    return localpath.replace('mp3/', 'online-exercises-audio/', 1)

def main(collection: CollectionMeta):

    cards_by_vocab_set = read_file(collection.folder)
    vocab_sets = [{
        "id": f"{collection.id}:{key}",
        "title": f"Lessons {key}",
        "terms": [card["cherokee"] for card in cards]
    } for key, cards in cards_by_vocab_set.items()]

    all_cards = []
    os.makedirs(os.path.join(collection.folder, "online-exercises-audio"), exist_ok=True)
    for set_cards in cards_by_vocab_set.values():
        for card in set_cards:
            oldpath = card["cherokee_audio"][0]
            # move files that aren't in the right folder
            if oldpath.startswith("mp3/"):
                newpath = change_path(oldpath)
                shutil.copy(os.path.join(collection.folder, oldpath), os.path.join(collection.folder, newpath))
                all_cards.append({**card, "cherokee_audio": [newpath]})
            else:
                all_cards.append(card)
            

    json.dump(all_cards, open(f"{collection.shortname}-cards.json", "w"), ensure_ascii=False)
    json.dump({
        "id": collection.id,
        "title": collection.name,
        "sets": vocab_sets
    }, open(f"{collection.shortname}.json", "w"), ensure_ascii=False)

    # not part of process rn
    # subprocess.run(["zip", f"{collection.shortname}.zip", f"{collection.shortname}.json", f"{collection.shortname}-cards.json", "-r", os.path.join(collection.folder, "online-exercises-audio")])

    

if __name__ == "__main__":
    collection = COLLECTIONS.get(argv[1])
    if collection is None:
        raise ValueError("Unknown collection id. Update online_exercises_meta.py if starting a new collection")
    main(collection)