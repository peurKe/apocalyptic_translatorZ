import json
import os
from apocalyptic_translatorZ.logic.translator import Translator
from sys import exit as sys_exit

class DBManagerJSON:
    
    def __init__(self, logs, params_game, database_dir: str ="./json"):
        # Get logs object instance
        self.logs = logs
        # Get params_game
        self.params_game = params_game

        self.db_file = params_game.get('database').get('db_file')
        self.database_dir = database_dir
        os.makedirs(self.database_dir, exist_ok=True)

        self.database = None
        self.file_descriptor = None
        self.next_id = 0  # Counter for unique IDs
        self.fix_list = []  # Fix list to be used

        # Initialize database states for notiifications in 'state' JSON key.
        self.notif_db_state__in_progress = 'IN PROGRESS'
        self.notif_db_state__done = 'DONE'


    def initialize_database(self, database_fixed_dir: str, translators_preferred: list, lang_source: str, lang_target: str, lang_source_name: str, lang_target_name: str):
        """
        Initialize or create a database and set language codes and names.
        """
        self.database_fixed_dir = database_fixed_dir
        self.translators_preferred = translators_preferred
        
        # initialize database file full path
        # self.database_fullpath = f"{self.database_dir}/{translator_name}_{lang_source}_{lang_target}_{self.db_file}"
        # self.database_fullpath = f"{self.database_dir}/{lang_source}_{lang_target}_{self.db_file}"
        self.database_fullpath = f"{self.database_dir}/{lang_target}_{self.db_file}"

        # Get fixed database file full path
        # fixed_database_fullpath = f"{self.database_fixed_dir}/{translator_name}_{lang_source}_{lang_target}_{self.db_file}"
        # fixed_database_fullpath = f"{self.database_fixed_dir}/{lang_source}_{lang_target}_{self.db_file}"
        fixed_database_fullpath = f"{self.database_fixed_dir}/{lang_target}_{self.db_file}"

        # Check if fixed database file present in fixed database directory
        if os.path.exists(fixed_database_fullpath):
            # Set database directory to fixed database directory
            self.database_fullpath = fixed_database_fullpath
            self.logs.log(f" • [Custom fixed JSON database was found: '{fixed_database_fullpath}'] OK", c='DEBUG', force=True)

        # self.logs.log(f"[DEBUG] self.database_fullpath: '{self.database_fullpath}'", c='DEBUG')
        # self.logs.input("Press enter to continue...", c='ASK')

        # Open the file for reading and writing
        mode = "r+" if os.path.exists(self.database_fullpath) else "w+"
        self.file_descriptor = open(self.database_fullpath, mode, encoding="utf-8")

        # Initialise ID counter
        self.next_id = 0

        # Load or create the database
        try:
            self.database = json.load(self.file_descriptor)
            self.next_id = self.database.get("next_id", 0)  # Get last ID used
            self.fix_list = self.database.get("fix_list", [])  # Get fix list to be used
            self.database['state'] = self.notif_db_state__in_progress  # Indicates that database processing is in progress
        except json.JSONDecodeError as e:
            self.database = {
                "state": self.notif_db_state__in_progress,  # Indicates that database processing is in progress
                "source": {"code": lang_source, "name": lang_source_name},
                "target": {"code": lang_target, "name": lang_target_name},
                "fix_list": [],  # Initialise fix list
                "translations": [],
                "next_id": self.next_id  # Initialise ID counter
            }

        else:
            # Update the database with provided source and target
            self.database["source"]["code"] = lang_source
            self.database["source"]["name"] = lang_source_name
            self.database["target"]["code"] = lang_target
            self.database["target"]["name"] = lang_target_name

            self.check_data_in_json()


    def check_data_in_json(self):
        # Check required keys '__from_text' and '____to_text' are not missing.
        required_keys = {"__from_text", "____to_text"}
        missing_ids = [
            d["_________id"] 
            for d in self.database["translations"]
            if not required_keys.issubset(d.keys())
        ]
        
        # Check required key '_________id' is not missing
        required_keys = {"_________id"}
        missing_from_texts = [
            d["__from_text"] 
            for d in self.database["translations"]
            if not required_keys.issubset(d.keys())
        ]

        # Set error message when any required key is missing
        error_msg = []
        if len(missing_ids):
            error_msg.append(f"Problem with '__from_text' and/or '____to_text' keys for following IDs: {missing_ids} in '{self.database_fullpath}' file.")
        if len(missing_from_texts):
            error_msg.append(f"Problem with '_________id' key for following '__from_text': {missing_from_texts} in '{self.database_fullpath}' file.")

        # At least one required key is missing
        if len(error_msg):
            self.logs.log(error_msg, c='FAIL', force=True)
            self.logs.input("Press enter to continue...", c='ASK')
            raise RuntimeError(error_msg)


    def add_translation(self, translator_name, from_text: str, to_text: str):
        """
        Add a translation to the database if it doesn't already exist.
        """
        translations = self.database.get("translations", [])
        if not any(
            entry["__from_text"] == from_text and
            entry["_translator"] == translator_name
            for entry in translations
        ):
            # Generate a unique ID
            translations.append({
                "_________id": self.next_id,
                "_translator": translator_name,
                "__from_text": from_text,
                "____to_text": to_text
            })
            self.database["translations"] = translations  # Ensure the list is updated
            self.next_id += 1  # Increment the ID counter
            self.database["next_id"] = self.next_id  # Save the updated counter


    def get_translation_to_text_by_from_text(self, from_text: str):
        """
        Retrieve the '____to_text' or fixed translation for a given 'from_text'.
        """
        translations = self.database.get("translations", [])
        
        # Quick search for 'from_text' entry
        for translator in self.translators_preferred:
            entry = next((t for t in translations if t["__from_text"] == from_text and t["_translator"] == translator), None)
            if entry:
                break
        
        if not entry:
            return None, None  # Return None if not found

        # Check fixed translation in the 'fix_list'.
        # self.logs.log(f"[DEBUG] fix_list: {self.fix_list}", c='DEBUG')
        # self.logs.log(f"[DEBUG] entry: '{entry}'", c='DEBUG')
        for from_fix in self.fix_list:
            if fix := entry.get(from_fix):  # Finds and returns the first match
                # self.logs.log(f"[DEBUG] fix: '{fix}'", c='DEBUG')
                return fix, entry.get("_translator")

        # self.logs.log(f"[DEBUG] to_text: '{entry.get("____to_text")}'", c='DEBUG')
        # self.logs.input("Press enter to continue...", c='ASK')

        # Returns the default translation if no fixed translation is found
        return entry.get("____to_text"), entry.get("_translator")


    def flush(self):
        """
        Write the current JSON database to disk
        without closing the file or clearing the in-memory database.
        """
        # ⚠️ This method do not close the file or the database (see self.close method)
        if self.database and self.file_descriptor:
            # Rewind the file descriptor to overwrite the content
            self.file_descriptor.seek(0)
            json.dump(self.database, self.file_descriptor, ensure_ascii=False, indent=2)
            self.file_descriptor.truncate()  # Ensure no residual data remains


    def close(self):
        """
        Close the JSON database after saving current JSON database and state to disk.
        """
        # Indicates that database processing is complete
        if self.database:
            self.database['state'] = self.notif_db_state__done

        # Write the current JSON database and state to disk
        self.flush()

        # Close database and file
        if self.database and self.file_descriptor:
            self.file_descriptor.close()
            self.file_descriptor = None
            self.database = None
