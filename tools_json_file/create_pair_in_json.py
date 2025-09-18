import json
import argparse
import os
import sys
from copy import deepcopy


def ensure_pairs(translations):
    new_list = []
    for entry in translations:
        translator = entry["_translator"]
        from_text = entry["__from_text"]
        to_text = entry["____to_text"]

        if translator == "deepl":
            # Ajouter un google avant si inexistant
            if not (new_list and new_list[-1]["_translator"] == "google" and new_list[-1]["__from_text"] == from_text):
                google_entry = {
                    "_________id": None,  # sera réattribué plus tard
                    "_translator": "google",
                    "__from_text": from_text,
                    "____to_text": to_text
                }
                new_list.append(google_entry)
            new_list.append(entry)

        elif translator == "google":
            # Ajouter un deepl après si inexistant
            if not (len(new_list) > 0 and new_list[-1]["_translator"] == "deepl" and new_list[-1]["__from_text"] == from_text):
                deepl_entry = {
                    "_________id": None,
                    "_translator": "deepl",
                    "__from_text": from_text,
                    "____to_text": to_text
                }
                new_list.append(entry)
                new_list.append(deepl_entry)
            else:
                new_list.append(entry)

    return new_list


def reindex(translations):
    for idx, entry in enumerate(translations):
        entry["_________id"] = idx
    return translations, len(translations)


def main():
    # Récupération du nom du script sans extension
    script_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]

    parser = argparse.ArgumentParser(description="Ensure translation pairs (google+deepl) in JSON file.")
    parser.add_argument("-f", "--file", required=True, help="Path to the JSON input file")
    args = parser.parse_args()

    # Construction du chemin complet : args/<script_name>/<file>
    input_file = os.path.join("args", script_name, args.file)

    # Charger le fichier
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    translations = data.get("translations", [])
    fixed = ensure_pairs(translations)
    fixed, next_id = reindex(fixed)

    data["translations"] = fixed
    data["next_id"] = next_id

    # Écrire le fichier corrigé
    updated_file = f"{input_file}.updated"
    with open(updated_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
