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
from colorama import Fore, Style
from inspect import currentframe
from tqdm import tqdm
from win32com.client import Dispatch as w32_dispatch
from sys import exit as sys_exit
import os

class apocalyptic_translatorZ:

    def __init__(self, game_dir, lang_sources, lang_targets, translators_preferred, translator_api_key=None,
                 restore=False, files=[], min_size=2, verbose=False, force=False):

        self.project_name = self.__class__.__name__
        self.shortcut_restore_name = f"{self.project_name} (restore).lnk"
        self.game_dir = game_dir
        self.lang_sources = lang_sources
        self.lang_targets = lang_targets
        self.translators_preferred = translators_preferred
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
            raise RuntimeError(f" No game found in directory '{self.working_directory}'.")

        # Show prerequisites
        self.show_prerequisites()

        # Initialize apocalyptic_translatorZ objects
        self.logs = Logs(self.params.game, self.verbose)
        self.logs.log(" • [Initializing apocalyptic_translatorZ] ...", force=True)

        self.language_support = LanguageSupport(self.logs, self.params.game)
        self.translators = Translator(self.logs, self.params.game, self.translators_preferred, self.translator_api_key, self.language_support)
        self.translators_available = self.translators.get_translators_available()
        self.translators_errors = 0
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
                   f"    • Available translators ..................... : {self.translators_available}\n" + \
                   f"    • Order of preference to get translations ... : {self.translators_preferred}\n" + \
                   f"    • Translator authentication key.............. : {auth_api_key}\n" + \
                   f"    • Translate from ............................ : {self.lang_sources}\n" + \
                   f"    • Translate to .............................. : {self.lang_targets}\n" + \
                   f"    • Minimum size string to translate........... : {self.min_size}\n" + \
                   f"    • Verbose mode .............................. : {self.verbose}\n" + \
                   f"    • Force mode ................................ : {self.force}\n" + \
                   f"    • Binary files to translate ................. : {self.file_handler.files_to_translate}\n"
        print(show_msg)


    def initialize_directories(self):
        # Set data game dir
        self.data_dir = f"{self.game_dir}/{self.params.game.get('data_dir_name')}"
        # Set Project directory
        self.project_dir = f"{self.game_dir}/{self.project_name}"
        # Set Project directories based on Game buildid
        self.working_dir = f"{self.project_dir}/{self.buildid}"
        self.database_dir = f"{self.project_dir}/DB/{self.db_type}"
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

                # Set supported source and target languages for translators
                self.translators.set_langs(lang_source, lang_target)

                # Set supported source and target languages for text_processor
                self.text_processor.set_langs(lang_source, lang_target)

                # Set glossary accordingly to source and target languages (currently only for DeepL translator)
                if lang_source not in ['auto']:
                    self.translators.initialize_glossary()

                # Restore backup files for next translations
                self.file_handler.restore_files()

                self.logs.log(f" • [Translations for '{lang_source}' to '{lang_target}'] ...", force=True)

                # # Same language code for DeepL or Google Translators
                self.file_handler.set_translation_dir(f"{self.translations_dir}/{lang_source}_to_{lang_target}")

                # Is translation already done ? + Create translation directory if not exists
                translation_done = self.file_handler.check_translation_done()
                # Only if force translation is not requested
                if not self.force:
                    # Check done file in translation dir + Create translation dir if no done file
                    if translation_done:
                        # Restore translation dir
                        self.file_handler.restore_files(from_translation_dir=True)
                        self.logs.log(f" • [Translations for '{lang_source}' to '{lang_target}'] OK (Already exists)\n", c='OK', force=True)
                        continue

                # Initialize database for the language pair
                self.db.initialize_database(
                    database_fixed_dir=self.database_fixed_dir,
                    translators_preferred=self.translators_preferred,
                    lang_source=lang_source,  # Same language code for DeepL or Google Translators
                    lang_target=lang_target,  # Same language code for DeepL or Google Translators
                    lang_source_name=self.language_support.get_source_language_name(lang_source),  # Same language name for DeepL or Google Translators
                    lang_target_name=self.language_support.get_target_language_name(lang_target)   # Same language name for DeepL or Google Translators
                )
                self.logs.log(f" [DEBUG] self.db.database_fullpath: {self.db.database_fullpath}", c='DEBUG')
                self.logs.log(f" [DEBUG] self.db.translators_preferred: {self.db.translators_preferred}", c='DEBUG')

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
                        f" [DEBUG] lang_source: {lang_source}\n" + \
                        f" [DEBUG] self.translators.lang_source: {self.translators.lang_source}\n" + \
                        f" [DEBUG] lang_target: {lang_target}\n" + \
                        f" [DEBUG] self.translators.lang_target: {self.translators.lang_target}\n" + \
                        f" [DEBUG] self.file_handler.current_allowed_range: {self.file_handler.current_allowed_ranges}\n" + \
                        f" [DEBUG] self.file_handler.bytes_to_translate[:5]: {self.file_handler.bytes_to_translate[:5]}\n" + \
                        f" [DEBUG] self.file_handler.all_bytes_to_translate[:5]: {self.file_handler.all_bytes_to_translate[:5]}",
                        c='DEBUG'
                    )
                    
                    # Process all binay strings from file to translate
                    for b_string in self.file_handler.extract_cyrillic_sequences():

                        # Check if original text must be excluded                        
                        if b_string.s in self.translators.exclude_full_sentences:
                            self.logs.log(f"/!\\ '{b_string.s}' is excluded from translation. See params game 'translator.exclude_full_sentences' key.", c='DEBUG', force=True)
                            # Go to next original text
                            continue

                        # # /!\ BEGIN OPTIMIZED in self.file_handler.get_binary_content()
                        # # Check if in allowed ranges
                        # if self.file_handler.is_break_requested(b_string.offset, file_to_translate):
                        #     break
                        # # /!\ END OPTIMIZED in self.file_handler.get_binary_content()

                        # Add text into text processor
                        self.text_processor.set_original_text(b_string, origin = 'FILE')

                        # Get translated text from DB
                        (translated_text, translator_name) = self.db.get_translation_to_text_by_from_text(self.text_processor.original_text)

                        # Translated text found in DB
                        if translated_text:
                            # Update text into text processoras DB origin
                            self.text_processor.set_translated_text(
                                text=translated_text,
                                alphabet=self.language_support.get_target_language_type(lang_target),
                                origin='DB'
                            )

                            # Display DB translation result
                            log_msg = f"{Fore.CYAN}>> {translator_name:>6s}{Style.RESET_ALL};" + \
                                f"{file_to_translate:s};" + \
                                f"{Fore.RED}0x{self.text_processor.original_text_offset:x}{Style.RESET_ALL};" + \
                                f"{Fore.CYAN}  DB  {Style.RESET_ALL};" + \
                                f"{Fore.LIGHTYELLOW_EX}{self.text_processor.original_text_binary_len:d}{Style.RESET_ALL};" + \
                                f"{Fore.GREEN}{self.text_processor.translated_text_binary_len:d}{Style.RESET_ALL};" + \
                                f"{Fore.LIGHTYELLOW_EX}{self.text_processor.original_text_len:d}{Style.RESET_ALL};" + \
                                f"{Fore.GREEN}{self.text_processor.translated_text_len:d}{Style.RESET_ALL};" + \
                                f"{Fore.LIGHTYELLOW_EX}{self.text_processor.original_text:s}{Style.RESET_ALL};" + \
                                f"{Fore.GREEN}{self.text_processor.translated_text:s}{Style.RESET_ALL};"
                            self.logs.log(log_msg)

                        # Translated text not found in DB
                        # Go to ONLINE translators
                        else:
                            
                            # Reversed loop allow to keep the first element as the priority last one processed by 'self.db' and 'self.text_processor'
                            for translator in reversed(self.translators.translators):

                                # Get translation from ONLINE translator
                                try:
                                    translated_text = self.translators.translate(translator, self.text_processor.original_text)
                                except Exception as e:
                                    # In case of translation error, the original text is not positioned, but a specific error message that will be easy to find.
                                    # translated_text = self.text_processor.original_text
                                    translated_text = self.translators.translation_missing_string
                                    
                                    # Display ONLINE error translation result
                                    log_msg = f"{Fore.LIGHTRED_EX}/!\\{translator.get('translator_name'):>6s};" + \
                                        f"{file_to_translate:s};" + \
                                        f"{Fore.RED}0x{self.text_processor.original_text_offset:x}{Style.RESET_ALL};" + \
                                        f"{Fore.LIGHTRED_EX}{type(e).__name__}{Style.RESET_ALL};" + \
                                        f"{Fore.LIGHTYELLOW_EX}{self.text_processor.original_text_binary_len:d}{Style.RESET_ALL};" + \
                                        f"{Fore.GREEN}{self.text_processor.translated_text_binary_len:d}{Style.RESET_ALL};" + \
                                        f"{Fore.LIGHTYELLOW_EX}{self.text_processor.original_text_len:d}{Style.RESET_ALL};" + \
                                        f"{Fore.GREEN}{self.text_processor.translated_text_len:d}{Style.RESET_ALL};" + \
                                        f"{Fore.LIGHTYELLOW_EX}{self.text_processor.original_text:s}{Style.RESET_ALL};" + \
                                        f"{Fore.GREEN}{translated_text:s}{Style.RESET_ALL};"
                                    self.logs.log(log_msg)
                                    self.translators_errors += 1 

                                # Update translated_text into text processor
                                self.text_processor.set_translated_text(
                                    text=translated_text,
                                    alphabet=self.language_support.get_target_language_type(lang_target),
                                    origin='ONLINE'
                                )

                                # Add translated_text in DB
                                self.db.add_translation(
                                    translator_name=translator.get('translator_name'),
                                    from_text=self.text_processor.original_text,
                                    to_text=self.text_processor.translated_text
                                )

                                # Set the preferred translator for displaying results
                                if translator.get('preferred_for_online'):  # is this translator the preferred one
                                    translator_preferred_in_log = f"{Fore.MAGENTA}>> {translator.get('translator_name'):>6s}{Style.RESET_ALL}"
                                    translator_online_in_log = f"{Fore.MAGENTA}ONLINE{Style.RESET_ALL}"
                                else:
                                    translator_preferred_in_log = f"{Fore.WHITE}   {translator.get('translator_name'):>6s}{Style.RESET_ALL}"
                                    translator_online_in_log = f"{Fore.WHITE}ONLINE{Style.RESET_ALL}"
                            
                                # Display ONLINE translation result
                                log_msg = f"{translator_preferred_in_log};" + \
                                    f"{file_to_translate:s};" + \
                                    f"{Fore.RED}0x{self.text_processor.original_text_offset:x}{Style.RESET_ALL};" + \
                                    f"{translator_online_in_log};" + \
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

                    # Flush data in translation file
                    self.db.flush()

                # Close database
                self.db.close()

                # Create success file flag in translation dir
                self.file_handler.set_translation_done()

                self.logs.log(f" • [Translations for '{lang_source}' to '{lang_target}'] OK\n", c='OK', force=True)
        
        # Check done file in translation dir + Create translation dir if no done file
        if self.file_handler.check_translation_done():
            # Restore last translated files to default data dir
            self.file_handler.restore_files(from_translation_dir=True)

        # Display end translation with number translation errors
        c_color = 'OK'
        error_message = ""
        if self.translators_errors:
            c_color = 'FAIL'
            error_message = f"You can find the error(s) by searching for \"{self.translators.translation_missing_string}\" string in \"{self.db.database_fullpath}\" file."
        self.logs.log(f" • [Running apocalyptic_translatorZ] OK with {self.translators_errors} translation error(s). {error_message}\n", c=c_color, force=True)

        # # Waiting for user input before exit
        # self.logs.input("Press enter to continue...")
