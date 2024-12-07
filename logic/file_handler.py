import os
import shutil
import re
from inspect import currentframe
from collections import namedtuple

String = namedtuple("String", ["s", "offset", "binary_length", "char_length"])

class FileHandler:

    def __init__(self, logs, params_game, cyrillic):
        # Get logs object instance
        self.logs = logs
        # Get params_game
        self.params_game = params_game

        # Allow to exclude all sentences containing LATIN specific terms
        self.exclude_words = self.params_game.get('exclude_words')

        # Initialize done file in translation dir
        self.done_file = self.params_game.get('done_file')
        # Initialize translation dir ('ru_to_fr' or 'uk_to_cs' etc.)
        self.translation_dir = None
        # Initialize backup dir ('backup')
        self.backup_dir = None
        # Initialize data dir ('GAME_Data')
        self.data_dir = None
        # Get cyrillic
        self.cyrillic = cyrillic
        # Initialize files to translate
        self.files_to_translate = []
        # Initialize watermark in binary
        self.watermark_in_binary = self.params_game['watermark_in_binary'].encode('utf-8')  # Convertir en bytes
        # Initialize watermark in binary length
        self.watermark_in_binary_len = len(self.watermark_in_binary)
        pass


    def get_files_to_translate(self, data_dir, files, files_starts=[], files_ends=[], files_not_starts=[], files_not_ends=[]):
        """
        Get files to translate from a directory according to the criteria supplied.

        :param files: basename files to translate.
        :param data_dir: data directory to browse.
        :param starts: List of prefixes. Includes files whose name begins with one of these prefixes.
        :param ends: List of suffixes. Includes files whose name ends with one of these suffixes.
        :param not_starts: List of prefixes. Excludes files whose name begins with one of these prefixes.
        :param not_ends: List of suffixes. Excludes files whose name ends with one of these suffixes.
        :return: List of full paths to filtered files.
        """
        if len(files):
            self.files_to_translate = [f"{data_dir}/{file}" for file in files]
        else:
            if not os.path.isdir(data_dir):
                raise ValueError(f"{data_dir} n'est pas un répertoire valide.")
            
            # Recover all the files in the
            all_files = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]

            self.logs.log(f" [DEBUG] all_files={all_files}", c='DEBUG')
            self.logs.log(f" [DEBUG] files_starts={files_starts}", c='DEBUG')
            self.logs.log(f" [DEBUG] files_ends={files_ends}", c='DEBUG')
            self.logs.log(f" [DEBUG] files_not_starts={files_not_starts}", c='DEBUG')
            self.logs.log(f" [DEBUG] files_not_ends={files_not_ends}", c='DEBUG')

            # File filtering
            self.files_to_translate = []
            for file in all_files:
                include = True

                # Checking all inclusion criteria
                if files_starts and not any(file.startswith(prefix) for prefix in files_starts):
                    include = False
                if files_ends and not any(file.endswith(suffix) for suffix in files_ends):
                    include = False
                
                # Checking all exclusion criteria
                if files_not_starts and any(file.startswith(prefix) for prefix in files_not_starts):
                    include = False
                if files_not_ends and any(file.endswith(suffix) for suffix in files_not_ends):
                    include = False

                # Add the file if it meets the criteria
                if include:
                    self.files_to_translate.append(os.path.join(data_dir, file))
        
        self.logs.log(f" [DEBUG] self.files_to_translate={self.files_to_translate}", c='DEBUG')


    def read_file(self, path):
        self.logs.log(f" [DEBUG] Reading file: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()


    def save_file(self, path, content):
        self.logs.log(f" [DEBUG] Saving file: {path}")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)


    def create_file(self, path):
        self.logs.log(f" [DEBUG] Creating file: {path}")
        with open(path, "w", encoding="utf-8") as f:
            pass


    def is_path_exists(self, path):
        if os.path.exists(path):
            return True
        return False


    def create_dir(self, dir):
        # if not os.path.exists(dir):
        #     os.makedirs(dir)
        os.makedirs(dir, exist_ok=True)


    def set_translation_dir(self, path):
        self.translation_dir = path
        self.create_dir(self.translation_dir)

    def set_backup_dir(self, path):
        self.backup_dir = path
        self.create_dir(self.backup_dir)


    def set_required_data_dir(self, path):
        self.data_dir = path
        if not os.path.exists(self.data_dir):
            raise FileNotFoundError(f"Folder not found: '{self.data_dir}'")


    def inject_bytes(self, binary_string, offset, length):
        self.all_bytes_to_translate[offset:offset+length] = binary_string


    def inject_bytes_in_file(self):
        # Insert watermark at the very end of all bytes array
        self.all_bytes_to_translate.extend(self.watermark_in_binary)

        # Check translation dir does exist
        if not self.is_path_exists(self.translation_dir):
            raise FileNotFoundError(f"Folder not found: '{self.translation_dir}' during copy original file in translation dir.")

        # Copy original file in translation dir
        shutil.copy(self.current_file, self.translation_dir)

        # Set new current file to file located in translation dir
        self.current_file = f"{self.translation_dir}/{os.path.basename(self.current_file)}"
        
        # Check new current file does exist
        if not self.is_path_exists(self.current_file):
            raise FileNotFoundError(f"File not found: '{self.current_file}' during copy original file in translation dir.")

        # Write all bytes array into file in translation dir
        with open(self.current_file, 'rb+') as f:
            # Write translated dialog in bytes array into translated file
            f.write(self.all_bytes_to_translate)


    def set_translation_done(self):
        done_path = f"{self.translation_dir}/{self.done_file }"
        with open(done_path, "w") as f:
            pass


    def check_translation_done(self):
        # Check if done file is present in translation dir
        if self.is_path_exists(self.translation_dir):
            done_path = f"{self.translation_dir}/{self.done_file }"
            if self.is_path_exists(done_path):
                return True
        else:
            self.create_dir(self.translation_dir)
            return False


    def validation_original_data_files(self, file):
        # Open the file in binary mode
        with open(file, 'rb') as f:
            # Go 'self.watermark_in_binary_len' bytes before the end of the file
            f.seek(-(self.watermark_in_binary_len), 2)  # 2 signifie "depuis la fin du fichier"
            # Read last 'self.watermark_in_binary_len' bytes
            last_bytes = f.read(self.watermark_in_binary_len)

            # TESTING PURPOSE ONLY
            # print(f"{file}: last_bytes='{last_bytes}'")

        # Check whether the last 'self.watermark_in_binary_len' bytes correspond to the string
        if last_bytes == self.watermark_in_binary:
            return False
        return True


    def backup_files(self): 
        # Backup files       
        self.logs.log(f" • [Create backup in '{self.backup_dir}' directory] ...", force=True)
        
        all_original_files = True
        for file in self.files_to_translate:
            backup_file = os.path.join(self.backup_dir, os.path.basename(file))
            # If backup file does not exist OR backup file is not a real original file
            if (not os.path.exists(backup_file)) or (not self.validation_original_data_files(backup_file)):
                # Check file is a real original file
                if self.validation_original_data_files(file):
                    shutil.copy2(file, backup_file)
                else:
                    self.logs.log(f" • [Game file '{file}' is not an original file.] WARNING", c='WARN', force=True)
                    all_original_files = False
        
        if not all_original_files:
            self.logs.log(f" • [Create backup in '{self.backup_dir}' directory] INCOMPLETE\n", c='WARN', force=True)
            return False
        
        self.logs.log(f" • [Create backup in '{self.backup_dir}' directory] OK\n", c='OK', force=True)
        return True


    def restore_files(self, from_translation_dir=False):
        # Restore files
        if from_translation_dir:
            src_dir = self.translation_dir
        else:
            src_dir = self.backup_dir
        self.logs.log(f" • [Restore files from '{src_dir}/' directory to '{self.data_dir}/'] ...", force=True)
        
        # All backup files
        files_to_copy = [os.path.join(src_dir, f) for f in os.listdir(src_dir)]
        files_count = len(files_to_copy)
        if not files_count:
            raise RuntimeError(f" Function '{currentframe().f_code.co_name}': Damn! There is {files_count} file to restore from '{src_dir}/' directory.\n", force=True)
        # Copy all backup files in data directory
        for file in files_to_copy:
            data_file = os.path.join(self.data_dir, os.path.basename(file))
            shutil.copy2(file, data_file)

        self.logs.log(f" • [Restore {files_count} files from '{src_dir}/' directory to '{self.data_dir}/'] OK\n", c='OK', force=True)


    def is_break_requested(self, address, file):
        # Check if we are in allowed range
        for range in self.get_current_range():
            # Log offset and allowed range
            # self.logs.log(f" s.offset: '{address}'; range: '{range}'; file: '{file}'", c='DEBUG')
            # input("Press enter to continue...")

            if (address < range.get('begin')) or (range.get('end') >= 0 and address > range.get('end')):
                self.logs.log(f" BREAK", c='INFO')
                return True
        
        return False


    def extract_cyrillic_sequences(self):
        cyrillic_pattern_min = rb'(?:' + self.cyrillic.CYRILLIC_BYTES + rb'){%d,}' % self.get_current_min_size()  # Regex pour trouver au moins 'min_size' caractères cyrilliques consécutifs
        start_address = self.get_current_start_address_int()

        for match in re.finditer(self.cyrillic.CYRILLIC_REGEX, self.bytes_to_translate):  # Chercher toutes les occurrences
            # Get match address
            match_address = start_address + match.start()

            cyrillic_binary = match.group(0)  # Retourner les bytes cyrilliques trouvés
            if re.search(cyrillic_pattern_min, cyrillic_binary):

                # Get cyrillic_string as string
                cyrillic_string = cyrillic_binary.decode('utf-8', errors='ignore')

                # Ensure cyrillic_string does not contain any LATIN specific terms to exclude
                if all(exclude_word not in cyrillic_string for exclude_word in self.exclude_words):
                    # cyrillic_string does not contain LATIN specific terms to exclude
                    yield String(
                        cyrillic_string,  # Cyrillic string found (string)
                        match_address,  # Cyrillic string found at offset (int)
                        len(cyrillic_binary),  # Cyrillic binary found length (int)
                        len(cyrillic_string)  # Cyrillic number of characters found (int)
                    )


    def get_binary_content(self):
        with open(self.current_file, 'rb') as f:
            # Get all binary file's bytes into a byte array for future writes.
            f.seek(0)
            self.all_bytes_to_translate = bytearray(f.read())

            # Read to EOF
            length_bytes = -1
            # Only if end address greater than start address
            if self.get_current_end_address_int() > self.get_current_start_address_int():
                # Set binary lenth from end address minus start address
                length_bytes = self.get_current_end_address_int() - self.get_current_start_address_int()

            # Go to first byte to translate
            f.seek(self.get_current_start_address_int())
            # Read until length_bytes
            self.bytes_to_translate = f.read(length_bytes)
                   

    def get_current_min_size(self):
        return int(self.current_allowed_ranges.get('min_size'))


    def get_current_start_address_int(self):
        return int(self.current_allowed_ranges.get('start_address_int'))


    def get_current_end_address_int(self):
        return int(self.current_allowed_ranges.get('end_address_int'))


    def get_current_range(self):
        return self.current_allowed_ranges.get('ranges')


    def set_current_allowed_ranges(self, file):
        self.current_file = file
        
        # Check file foes exist
        if not os.path.exists(self.current_file):
            self.logs.log(f" [WARN] File not found: '{self.current_file}'", c='WARN')
            return False
        
        # Check valid start address in allowed ranges
        self.current_allowed_ranges = self.allowed_ranges.get(os.path.basename(self.current_file))
        if int(self.current_allowed_ranges.get('start_address_int')) < 0:
            return False

        # File does exist and start address is valid
        return True


    def set_allowed_ranges(self):
        # Initialize local variables
        start_address = 0
        min_size = 2
        # Initialize allowed_ranges to be returned
        allowed_ranges = {}

        for file_path in self.files_to_translate:
            
            file_name = os.path.basename(file_path)
            # All 'level' files
            path_type = 'levels'
            # All '.assets' files
            if '.assets' in file_path:
                path_type = 'assets'

            allowed_ranges = self.params_game.get('allowed_ranges')
            # Get minimun string size
            min_size = allowed_ranges.get(path_type).get('min_size')
            # Get start address (hex)
            start_address_hex = allowed_ranges.get(path_type).get('start_address_hex')
            # Get start address (label)
            start_from_hex_label = allowed_ranges.get(path_type).get('start_address_hex_label')
            # Get start address (int)
            start_address_int = self.get_address_from_binary(file_path, start_address_hex, start_from_hex_label)

            # Set range values
            allowed_ranges[file_name] = dict(
                min_size = min_size,
                start_address_hex = start_address_hex,
                start_address_int = start_address_int,
                end_address_int = -1,
                ranges = [
                    {
                        "begin": start_address,  # int
                        "end": -1  # int (-1 is for EOF)
                    }
                ]
            )

        # Set allowed ranges
        self.allowed_ranges = allowed_ranges


    def get_address_from_binary(self, path, search_hex, label):
        # Open path in binary mode
        with open(path, 'rb') as f:
            f.seek(0)
            try:
                offset_int = f.read().find(bytes.fromhex(search_hex))
            except Exception as e:
                raise RuntimeError(f" Hell! Error during search address for '{label}' in '{path}' binary file. Exception {type(e).__name__}: {e}.\n")
            return offset_int
