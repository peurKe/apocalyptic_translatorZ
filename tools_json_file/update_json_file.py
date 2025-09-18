import json

# Charger les fichiers JSON source et target
def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Erreur : le fichier {file_path} est introuvable.")
        return None
    except json.JSONDecodeError:
        print(f"Erreur : le fichier {file_path} contient un JSON invalide.")
        return None

def save_json(data, file_path):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du fichier {file_path} : {e}")

# Fonction principale pour mettre à jour les traductions
def update_translations(source_path, target_path, output_path):
    source_data = load_json(source_path)
    target_data = load_json(target_path)

    if not source_data or not target_data:
        return

    source_translations = source_data.get("translations", [])
    target_translations = target_data.get("translations", [])

    for source_item in source_translations:
        source_text = source_item.get("__from_text")

        for target_item in target_translations:
            if target_item.get("__from_text") == source_text:
                # Copier les clés spécifiques du source vers le target
                for key, value in source_item.items():
                    if key.startswith("_____peurKe") or key.startswith("_comment_"):
                        target_item[key] = value

    # Sauvegarder les modifications dans un nouveau fichier
    save_json(target_data, output_path)


# Fonction principale pour mettre à jour les traductions
def update_all_google_with_deepl_translations(source_path, output_path):
    source_data = load_json(source_path)

    if not source_data:
        return

    source_translations = source_data.get("translations", [])

    source_text = ""
    for source_item in reversed(source_translations):
        if source_item.get("_translator") == "deepl":
            source_text = source_item.get("____to_text")
            continue
        if source_item.get("_translator") == "google":
            source_item["____to_text"] = source_text

    # Sauvegarder les modifications dans un nouveau fichier
    save_json(source_data, output_path)

# # Chemins des fichiers source et target
# source_file = "args/update_translations/ru_fr_CONVRGENCE_source.json"
# target_file = "args/update_translations/ru_fr_CONVRGENCE_target.json"
# output_file = "args/update_translations/ru_fr_CONVRGENCE_updated.json"
# update_translations(source_file, target_file, output_file)

# Chemins des fichiers source et target
source_file = "args/update_all_google_with_deepl_translations/fr_ZONAORIGIN_source.json"
output_file = "args/update_all_google_with_deepl_translations/fr_ZONAORIGIN.updated.json"
update_all_google_with_deepl_translations(source_file, output_file)

print(f"Mise à jour terminée. Le fichier modifié a été enregistré sous {output_file}.")
