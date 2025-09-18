# apocalyptic_translatorZ

# Useful shell commands

```
# Generate all JSON database files containing translations for a given game using DeepL and Google Translate, and force the translation of existing files. The source language will be chosen automatically by the translator.
cd ~/<GITHUB_LOCAL_REPOSITORY> && python -m apocalyptic_translatorZ.main -g '<GAME_FOLDER_FULL_PATH>' -ls auto -l 'da,de,en,es,fi,fr,hu,it,nl,pl,pt,ro,sv' -v -t 'deepl,google' -ta <DEEPL_APIKEY> --force

# Verify the compliance of the JSON database file
cd ~/<GITHUB_LOCAL_REPOSITORY>/tools_json_file && python -m check_characters_in_json -f <JSON_DATABASE_FILE>

# Generate the executable file 'apocalyptic_translatorZ.exe' from the sources.
cd ~/<GITHUB_LOCAL_REPOSITORY> && pyinstaller --distpath ./apocalyptic_translatorZ/pyinstaller/dist --workpath ./apocalyptic_translatorZ/pyinstaller/build --onefile --name apocalyptic_translatorZ  apocalyptic_translatorZ/main.py
```

# Tree structure

| FOLDERS             | CONTENT                                                       |
|--------------------:|:--------------------------------------------------------------|
| **DB**              | JSON database file folder                                     |
| **images**          | Project folder for images (mainly for README.md)              |
| **innosetup**       | Innosetup folder for automatic installer versions             |
| **logic**           | All apocalyptic_translatorZ mod logic                         |
| **pyinstaller**     | Pyinstaller folder for apocalyptic_translatorZ mod executable |
| **tools_json_file** | Various useful scripts for managing JSON database files       |
