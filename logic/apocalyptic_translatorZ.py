from apocalyptic_translatorZ.logic.translator import Translator
from apocalyptic_translatorZ.logic.logs import Logs
from apocalyptic_translatorZ.logic.params import Params
from apocalyptic_translatorZ.logic.text_processor import TextProcessor
from apocalyptic_translatorZ.logic.cyrillic import Cyrillic
from apocalyptic_translatorZ.logic.file_handler import FileHandler
from apocalyptic_translatorZ.logic.db_manager_sqlite import DBManagerSQLITE
from apocalyptic_translatorZ.logic.db_manager_json import DBManagerJSON
from apocalyptic_translatorZ.logic.language_support import LanguageSupport
from apocalyptic_translatorZ.logic.steam import Steam
from colorama import init as colorama_init, Fore, Style
from inspect import currentframe
from tqdm import tqdm
from win32com.client import Dispatch as w32_dispatch
from sys import exit as sys_exit
import os

class apocalyptic_translatorZ:

    def __init__(self, game_dir, lang_sources, lang_targets, translator_name, translator_api_key=None,
                 restore=False, files=[], min_size=2, verbose=False, force=False):

        self.project_name = self.__class__.__name__
        self.shortcut_restore_name = f"{self.project_name} (restore).lnk"
        self.game_dir = game_dir
        self.lang_sources = lang_sources
        self.lang_targets = lang_targets
        self.translator_name = translator_name
        self.translator_api_key = translator_api_key
        self.restore = restore
        self.files = files
        self.min_size = min_size
        self.min_size_save = self.min_size 
        self.verbose = verbose
        self.force = force

        self.params = Params()
        if self.params.game is None:
            # Raise an error if the 'game' property' does not exist
            raise ValueError(f" No game found in directory '{self.working_directory}'.")

        # Show prerequisites
        self.show_prerequisites()

        # Initialize apocalyptic_translatorZ objects
        self.logs = Logs(self.params.game, self.verbose)
        self.logs.log(" • [Initializing apocalyptic_translatorZ] ...", force=True)

        self.language_support = LanguageSupport(self.logs, self.params.game)
        self.translator = Translator(self.logs, self.params.game, self.translator_name, self.translator_api_key, self.language_support)
        self.text_processor = TextProcessor(self.logs, self.params.game)
        self.cyrillic = Cyrillic(self.logs, self.params.game)
        self.file_handler = FileHandler(self.logs, self.params.game, self.cyrillic)
        # Initialize Steam client
        self.steam = Steam(self.logs, self.params.game_exec, self.params.game.get('steam'))

        # Create or update shortcut for restoring backup files
        self.create_restore_shortcut()

        # Get game files
        self.file_handler.get_files_to_translate(
            data_dir=self.params.game.get('data_dir_name'),
            files=self.files,
            files_starts=self.params.game.get('files').get('starts'),
            files_ends=self.params.game.get('files').get('ends'),
            files_not_starts=self.params.game.get('files').get('not_starts'),
            files_not_ends=self.params.game.get('files').get('not_ends'),
        )

        # Prepare allowed ranges in game files
        self.file_handler.set_allowed_ranges()

        # Set Game buildid
        self.buildid = self.steam.get_buildid()

        # Set Database type (sqlite or json)
        self.db_type = self.params.game.get('database').get('type')

        # Initialiaze directories
        self.initialize_directories()

        if self.db_type == "sqlite":
            # Initialize SQLite Database
            self.db = DBManagerSQLITE(self.logs, self.params.game, self.database_dir)
        elif self.db_type == "json":
            # Initialize SQLite Database
            self.db = DBManagerJSON(self.logs, self.params.game, self.database_dir)
        else:
            self.logs.log(f" • [Initializing '{self.db_type}' Database type not supported] FAIL\n", c='FAIL', force=True)    

        self.logs.log(" • [Initializing apocalyptic_translatorZ] OK\n", c='OK', force=True)


    def show_prerequisites(self):
        show_msg = "    /// PREREQUISITES:\n" + \
                   "    • Your Steam game must be up to date.\n" + \
                   "    • Your PC must have an Internet connection for Google Translator or Deepl API requests.\n" + \
                   "    • You must have a valid API auth key if you use Deepl API requests with the \"-t 'deepl'\" and \"-ta 'xxx'\" parameters.\n"
        print(show_msg)

    def show_parameters(self):
        auth_api_key = "(None)"
        if self.translator_api_key:
            auth_api_key = "********"

        show_msg = "    /// PARAMETERS:\n" + \
                   f"    • Translator ........................ : {self.translator_name}\n" + \
                   f"    • Translator authentication key...... : {auth_api_key}\n" + \
                   f"    • Translate from .................... : {self.lang_sources}\n" + \
                   f"    • Translate to ...................... : {self.lang_targets}\n" + \
                   f"    • Minimum size string to translate... : {self.min_size}\n" + \
                   f"    • Verbose mode ...................... : {self.verbose}\n" + \
                   f"    • Force mode ........................ : {self.force}\n" + \
                   f"    • Binary files to translate ......... : {self.file_handler.files_to_translate}\n"
        print(show_msg)


    def initialize_directories(self):
        # Set data game dir
        self.data_dir = f"{self.game_dir}/{self.params.game.get('data_dir_name')}"
        # Set Project directory
        self.project_dir = f"{self.game_dir}/{self.params.game.get('safe_name')}_{self.project_name}"
        # Set Project directories based on Game buildid
        self.working_dir = f"{self.project_dir}/{self.buildid}"
        # self.database_dir = f"{self.working_dir}/DB/{self.db_type}/{self.translator_name}"
        self.database_dir = f"{self.working_dir}/DB/{self.db_type}"
        self.database_fixed_dir = f"{self.project_dir }.FIXED_DB"
        self.backup_dir = f"{self.working_dir}/{self.params.game.get('backup_dir_name')}"
        self.translations_dir = f"{self.working_dir}/{self.params.game.get('translations_dir_name')}"
        #  Create Project directories based on Game buildid
        self.file_handler.create_dir(self.working_dir)
        self.file_handler.create_dir(self.database_dir)
        self.file_handler.create_dir(self.database_fixed_dir)
        self.file_handler.create_dir(self.backup_dir)
        self.file_handler.create_dir(self.translations_dir)
        # Set done file path for
        self.file_handler.create_dir(self.translations_dir)
        # Set data dir
        self.file_handler.set_required_data_dir(self.data_dir)
        # Set backup dir
        self.file_handler.set_backup_dir(self.backup_dir)


    def create_restore_shortcut(self):
        try:
            # Get current script name
            script_name = f"{os.path.splitext(os.path.basename(__file__))[0]}.exe"
            # Define the executable path and shortcut properties
            exe_path = f"{self.game_dir}\\{script_name}"
            exe_args = '-r'
            shortcut_target = exe_path
            # Create a WScript.Shell object
            shell = w32_dispatch('WScript.Shell')
            # Create a shortcut object
            shortcut = shell.CreateShortCut(self.shortcut_restore_name)
            # Set the shortcut properties
            shortcut.TargetPath = shortcut_target
            shortcut.WorkingDirectory = os.path.dirname(shortcut_target)
            shortcut.Arguments = exe_args
            # Save the shortcut
            shortcut.save()
            self.logs.log(f" • [Create '{self.shortcut_restore_name}' shortcut for restoring original binary files] OK", c='OK', force=True)
        except:
            self.logs.log(f" • [Create '{self.shortcut_restore_name}' shortcut for restoring original binary files] Fail", c='WARN', force=True)


    def run(self):
        # Show parameters
        self.show_parameters()

        self.logs.log(" • [Running apocalyptic_translatorZ] ...", force=True)
        self.logs.log(f"   {self.steam.get_game_exec()}:{self.steam.get_manifest_acf_file()}:buildid:{self.steam.get_buildid()}]\n", c='DEBUG', force=True)

        # Check backup files are original files
        if not self.file_handler.backup_files():
            if self.steam.steam_update_game_files():
                if not self.file_handler.backup_files():
                    raise RuntimeError(f" Function '{currentframe().f_code.co_name}': Damn! It is not possible to save data files even after Steam has updated the game files.")
            else:
                raise RuntimeError(f" Function '{currentframe().f_code.co_name}': Ouch! Impossible to automatic update game files with Steam.")
        
        # Only restore backup files and quit
        if self.restore:
            self.file_handler.restore_files()
            self.logs.input("Press enter to continue...")
            sys_exit(0)

        # All source langs
        for lang_source in self.lang_sources:
            
            # All target langs
            for lang_target in self.lang_targets:
            
                # Check source and target requested languages are supported
                self.language_support.check_langs_supported(lang_source, lang_target)

                # Restore backup files for next translations
                self.file_handler.restore_files()

                # Set source and target requested languages in translator
                self.translator.set_langs(lang_source, lang_target)

                self.logs.log(f" • [Translations for '{self.translator.lang_source}' to '{self.translator.lang_target}'] ...", force=True)

                self.file_handler.set_translation_dir(f"{self.translations_dir}/{self.translator.lang_source}_to_{self.translator.lang_target}")

                # Is translation already done ? + Create translation directory if not exists
                translation_done = self.file_handler.check_translation_done()
                # Only if force translation is not requested
                if not self.force:
                    # Check done file in translation dir + Create translation dir if no done file
                    if translation_done:
                        # Restore translation dir
                        self.file_handler.restore_files(from_translation_dir=True)
                        self.logs.log(f" • [Translations for '{self.translator.lang_source}' to '{self.translator.lang_target}'] OK (Already exists)\n", c='OK', force=True)
                        continue

                # # BEGIN TESTING PURPOSE ONLY
                # # Restore backup dir
                # self.file_handler.restore_files()
                # # END TESTING PURPOSE ONLY

                # # BEGIN TESTING PURPOSE ONLY
                # input("Press enter to continue")
                # # END TESTING PURPOSE ONLY

                # Initialize database for the language pair
                self.db.initialize_database(
                    self.database_fixed_dir,
                    self.translator_name,
                    self.translator.lang_source,
                    self.translator.lang_target,
                    self.language_support.get_source_language_name(lang_source),
                    self.language_support.get_target_language_name(lang_target)
                )
                self.logs.log(f" [DEBUG] self.db.database_fullpath: {self.db.database_fullpath}", c='DEBUG')

                # # BEGIN Done in 'Initialize database for the language pair' above
                # # Add source lang to DB
                # self.db.add_lang_source(
                #     lang_source,
                #     self.language_support.get_source_language_name(lang_source)
                # )
                # # Add target lang to DB
                # self.db.add_lang_target(
                #     lang_target,
                #     self.language_support.get_target_language_name(lang_target)
                # )
                # # END Done in 'Initialize database for the language pair' above

                # For each file to translate
                for file_to_translate in tqdm(self.file_handler.files_to_translate):
                    
                    # When current range is not valid then go to next file
                    if not self.file_handler.set_current_allowed_ranges(file_to_translate):
                        continue

                    # Get all binay texts from file to translate
                    self.file_handler.get_binary_content()

                    # Show file information
                    self.logs.log(
                        f" ------------------ \n" + \
                        f" [DEBUG] file_to_translate: {file_to_translate}\n" + \
                        f" [DEBUG] self.translator.lang_source: {self.translator.lang_source}\n" + \
                        f" [DEBUG] self.translator.lang_target: {self.translator.lang_target}\n" + \
                        f" [DEBUG] self.file_handler.current_allowed_range: {self.file_handler.current_allowed_ranges}\n" + \
                        f" [DEBUG] self.file_handler.bytes_to_translate[:5]: {self.file_handler.bytes_to_translate[:5]}\n" + \
                        f" [DEBUG] self.file_handler.all_bytes_to_translate[:5]: {self.file_handler.all_bytes_to_translate[:5]}",
                        c='DEBUG'
                    )
                    
                    # Process all binay strings from file to translate
                    for b_string in self.file_handler.extract_cyrillic_sequences():
                        
                        # Log binary string
                        # self.logs.log(f" b_text={b_string}", c='DEBUG')
                        
                        # # /!\ BEGIN OPTIMIZED in self.file_handler.get_binary_content()
                        # # Check if in allowed ranges
                        # if self.file_handler.is_break_requested(b_string.offset, file_to_translate):
                        #     break
                        # # /!\ END OPTIMIZED in self.file_handler.get_binary_content()

                        # Add text into text processor
                        self.text_processor.set_original_text(b_string, origin = 'FILE')

                        # Get translated text from DB
                        translated_text = self.db.get_translation_to_text_by_from_text(self.text_processor.original_text)
                        # Translated text found in DB
                        if translated_text:
                            # Update text into text processor
                            self.text_processor.set_translated_text(
                                text=translated_text,
                                alphabet=self.language_support.get_target_language_type(lang_target),
                                origin='DB'
                            )
                        # Translated text not found in DB
                        else:
                            # Get translation from ONLINE translator
                            translated_text = self.translator.translate(self.text_processor.original_text)

                            # # TESTING PURPOSE ONLY
                            # self.logs.log(f"'{translated_text}'", c='NOTIF', force=True)

                            # Update translated_text into text processor
                            self.text_processor.set_translated_text(
                                text=translated_text,
                                alphabet=self.language_support.get_target_language_type(lang_target),
                                origin='ONLINE'
                            )
                            
                            # # TESTING PURPOSE ONLY
                            # self.logs.log(f"'{self.text_processor.translated_text}'", c='DEBUG', force=True)
                            
                            # Add translated_text in DB
                            self.db.add_translation(self.text_processor.original_text, self.text_processor.translated_text)
                        
                        # self.logs.log(f" translated_text ({self.text_processor.translated_origin}): {self.text_processor.translated_text}", c='WARN')
                        
                        if self.text_processor.translated_text_binary_len != self.text_processor.original_text_binary_len:
                            self.logs.log(" ### /!\\ THIS TRANSLATED DIALOG FINAL BYTES LENGTH BELOW DIFFER THAN ORIGINAL DIALOG BYTES LENGTH /!\\ ###", c='FAIL')
                        log_msg = f"{Style.RESET_ALL} {file_to_translate:s};" + \
                                  f"{Fore.RED}0x{self.text_processor.original_text_offset:x}{Style.RESET_ALL};" + \
                                  f"{Fore.MAGENTA}{self.text_processor.translated_origin:s}{Style.RESET_ALL};" + \
                                  f"{Fore.LIGHTYELLOW_EX}{self.text_processor.original_text_binary_len:d}{Style.RESET_ALL};" + \
                                  f"{Fore.GREEN}{self.text_processor.translated_text_binary_len:d}{Style.RESET_ALL};" + \
                                  f"{Fore.LIGHTYELLOW_EX}{self.text_processor.original_text_len:d}{Style.RESET_ALL};" + \
                                  f"{Fore.GREEN}{self.text_processor.translated_text_len:d}{Style.RESET_ALL};" + \
                                  f"{Fore.LIGHTYELLOW_EX}{self.text_processor.original_text:s}{Style.RESET_ALL};" + \
                                  f"{Fore.GREEN}{self.text_processor.translated_text:s}{Style.RESET_ALL};"
                        self.logs.log(log_msg)

                        # Inject translated bytes in all bytes array
                        self.file_handler.inject_bytes(
                            self.text_processor.translated_text_binary,
                            self.text_processor.original_text_offset,
                            self.text_processor.original_text_binary_len
                        )

                    # Inject all bytes array in translation file
                    self.file_handler.inject_bytes_in_file()

                    # # BEGIN TESTING PURPOSE ONLY
                    # input("Press enter to continue....")
                    # END TESTING PURPOSE ONLY

                # Close database
                self.db.close()

                # Create success file flag in translation dir
                self.file_handler.set_translation_done()

                self.logs.log(f" • [Translations for '{self.translator.lang_source}' to '{self.translator.lang_target}'] OK\n", c='OK', force=True)
        
        # Check done file in translation dir + Create translation dir if no done file
        if self.file_handler.check_translation_done():
            # Restore last translated files to default data dir
            self.file_handler.restore_files(from_translation_dir=True)

        self.logs.log(" • [Running apocalyptic_translatorZ] OK\n", c='OK', force=True)

        # # BEGIN TESTING PURPOSE ONLY
        # self.logs.input("Press enter to continue...")
        # # END TESTING PURPOSE ONLY
