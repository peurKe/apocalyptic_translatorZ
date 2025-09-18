import json
import argparse
import os
import sys

# Liste des caractères autorisés
allowed_chars = set(" 0123456789abcdefghijklmnopqrstuvwxyz%,.?!+()/\"'–-—\n\\~:")

def check_entry(entry):
    """
    Vérifie un dictionnaire contenant potentiellement '_________id' et '____to_text'.
    Retourne un dict avec id, texte et les caractères interdits trouvés.
    """
    if "____to_text" in entry:
        value = str(entry["____to_text"])
        disallowed = [ch for ch in value.lower() if ch not in allowed_chars]
        if disallowed:
            return {
                "___id": entry.get("_________id"),
                "__invalid_chars": disallowed,
                "_to_text": value
            }
    return None

def collect_results(obj):
    """
    Parcourt récursivement le JSON pour trouver les dicts contenant '____to_text'.
    """
    results = []
    if isinstance(obj, dict):
        res = check_entry(obj)
        if res:
            results.append(res)
        for value in obj.values():
            results.extend(collect_results(value))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(collect_results(item))
    return results

def collect_ids_with_exclamation(obj, collected_ids):
    """
    Parcourt récursivement le JSON pour collecter les IDs où '____to_text' contient '(!)'.
    """
    if isinstance(obj, dict):
        text = obj.get("____to_text")
        if text and "(!)" in str(text):
            collected_ids.append(obj.get("_________id"))
        for value in obj.values():
            collect_ids_with_exclamation(value, collected_ids)
    elif isinstance(obj, list):
        for item in obj:
            collect_ids_with_exclamation(item, collected_ids)

def collect_id_objects(obj, id_objects):
    """
    Parcourt récursivement le JSON et stocke les objets contenant '_________id'.
    """
    if isinstance(obj, dict):
        if "_________id" in obj and isinstance(obj["_________id"], int):
            id_objects.append(obj)
        for value in obj.values():
            collect_id_objects(value, id_objects)
    elif isinstance(obj, list):
        for item in obj:
            collect_id_objects(item, id_objects)

def reindex_ids(data):
    """
    Réindexe tous les '_________id' pour qu'ils soient consécutifs (0..N-1).
    Retourne le prochain index disponible.
    """
    id_objects = []
    collect_id_objects(data, id_objects)

    for new_id, obj in enumerate(id_objects):
        obj["_________id"] = new_id

    return len(id_objects)

def main():
    script_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]

    parser = argparse.ArgumentParser(description="Vérifie les champs '____to_text' dans un fichier JSON.")
    parser.add_argument("-f", "--file", required=True, help="Nom du fichier JSON à analyser (dans ./args/<script_name>/)")
    args = parser.parse_args()

    input_file = os.path.join("args", script_name, args.file)

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    valid_states = ['DONE']
    current_state = data.get("state")
    print(f"### Current state is '{current_state}'")
    if current_state not in valid_states:
        print(f"### /!\\ Current state is not in '{valid_states}'.")
        sys.exit(0)

    previous_next_id = data.get("next_id")
    next_id = reindex_ids(data)
    data["next_id"] = next_id
    print(f"### IDs reindexed from 0 to {next_id-1}. Previous next ID = {previous_next_id}")

    # Vérification des caractères interdits
    results = collect_results(data)
    if results:
        print("### Unsupported characters in results:")
        for r in results:
            print(r)
        all_invalid_chars = set(ch for r in results for ch in r["__invalid_chars"])
        print("\n### Unique invalid characters found:")
        print(" ".join(sorted(all_invalid_chars)))
    else:
        print("### No unsupported characters in results.")

    # Collecte des IDs contenant '(!)'
    exclamation_ids = []
    collect_ids_with_exclamation(data, exclamation_ids)
    print("\n### IDs where '____to_text' contains '(!)':")
    print(exclamation_ids if exclamation_ids else "None found.")

    # Sauvegarde du JSON modifié
    with open(input_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
