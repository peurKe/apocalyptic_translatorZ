import sqlite3
import os
from inspect import currentframe
from typing import Optional, List, Tuple

class DBManagerSQLITE:

    def __init__(self, logs, params_game, database_dir: str ="./sqlite"):
        """
        Initialize the DBManagerSQLITE with a directory to store SQLite databases and database filename.
        """
        # Get logs object instance
        self.logs = logs
        # Get params_game
        self.params_game = params_game

        self.db_file = params_game.get('db_file')
        self.database_dir = database_dir
        os.makedirs(self.database_dir, exist_ok=True)
        
        # Initialize lang source and target name and id
        self.lang_source_name = None
        self.lang_source_id = None
        self.lang_target_name = None
        self.lang_target_id = None


    def initialize_database(self, database_fixed_dir, translator_name: str, lang_source: str, lang_target: str, lang_source_name: str, lang_target_name: str, reindex: list = ['all']):
        self.database_fixed_dir = database_fixed_dir
        self.translator_name = translator_name
        self.lang_source = lang_source
        self.lang_target = lang_target
        self.lang_source_name = lang_source_name
        self.lang_target_name = lang_target_name
        self.lang_source_id = self.add_lang(self.lang_source, self.lang_source_name)
        self.lang_target_id = self.add_lang(self.lang_target, self.lang_target_name)
        self.reindex = reindex

        # initialize database file full path
        # self.database_fullpath = f"{self.database_dir}/{self.translator_name}_{lang_source}_{lang_target}_{self.db_file}"
        self.database_fullpath = f"{self.database_dir}/{lang_source}_{lang_target}_{self.db_file}"

        # Get fixed database file full path
        # fixed_database_fullpath = f"{self.database_fixed_dir}/{self.translator_name}_{lang_source}_{lang_target}_{self.db_file}"
        fixed_database_fullpath = f"{self.database_fixed_dir}/{lang_source}_{lang_target}_{self.db_file}"
        # Check if fixed database file present in fixed database directory
        if os.path.exists(fixed_database_fullpath):
            # Set database directory to fixed database directory
            self.database_fullpath = fixed_database_fullpath
            self.logs.log(f" • [Custom fixed SQLite database was found: '{fixed_database_fullpath}'] OK", c='DEBUG', force=True)

        # self.logs.log(f"[DEBUG] self.database_fullpath: '{self.database_fullpath}'", c='DEBUG')
        # self.logs.input("Press enter to continue...", c='ASK')

        self.connection = sqlite3.connect(self.database_fullpath)
        self.cursor = self.connection.cursor()
        self.create_tables(reindex)


    def create_tables(self, reindex):
        # Creating the 'langs' table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS langs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        # Creating the 'from_text' table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS from_text (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL UNIQUE
            )
        ''')
        # Creating the 'to_text' table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS to_text (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL UNIQUE
            )
        ''')
        # Creating the 'translation' table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS translation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_lang_id INTEGER,
                from_text_id INTEGER,
                to_lang_id INTEGER,
                to_text_id INTEGER,
                FOREIGN KEY (from_lang_id) REFERENCES langs(id),
                FOREIGN KEY (from_text_id) REFERENCES from_text(id),
                FOREIGN KEY (to_lang_id) REFERENCES langs(id),
                FOREIGN KEY (to_text_id) REFERENCES to_text(id),
                UNIQUE (from_lang_id, from_text_id, to_lang_id, to_text_id)  -- Ensure uniqueness
            )
        ''')
        # Create index
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_langs_code ON langs(code);')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_langs_code ON langs(code);')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_to_text_text ON to_text(text);')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_from_text_text ON from_text(text);')
        
        if len(reindex):
            if 'all' in reindex:
                self.cursor.execute('REINDEX;')
            else:
                for table in reindex:
                    self.cursor.execute(f"REINDEX {table};")
        
        self.connection.commit()


    # def add_lang_source(self, code: str, name: str, source: Optional[bool] = False, target: Optional[bool] = False, verbose: Optional[bool] = False) -> Optional[int]:
    #     self.lang_source_name = name
    #     self.lang_source_id = self.add_lang(code, name, verbose)


    # def add_lang_target(self, code: str, name: str, source: Optional[bool] = False, target: Optional[bool] = False, verbose: Optional[bool] = False) -> Optional[int]:
    #     self.lang_target_name = name
    #     self.lang_target_id = self.add_lang(code, name, verbose)


    def add_lang(self, code: str, name: str, verbose: Optional[bool] = False) -> Optional[int]:
        # Adding a record to 'lang'
        try:
            self.cursor.execute('INSERT INTO langs (name, code) VALUES (?, ?)', (name, code))
            self.connection.commit()
            # if verbose:
            #     self.logs.log(f"Added language: {code} ({name})", c='ASK')
            return self.cursor.lastrowid  # Return the ID of the newly created record

        except sqlite3.IntegrityError:
            # If a duplicate entry is found, retrieve the existing record's ID
            self.cursor.execute('SELECT id FROM langs WHERE code = ? AND name = ?', (code, name))
            result = self.cursor.fetchone()
            if result:
                # if verbose:
                #     self.logs.log(f"Duplicate entry found in 'lang'. Returning existing ID {result[0]}.", c='ASK')
                return result[0]  # Return the existing record's ID
            else:
                self.logs.log(f"An unexpected error occurred.", c='FAIL')
                return None

    def add_to_text(self, text: str, verbose: Optional[bool] = False) -> Optional[int]:
        # Adding a record to 'to_text'
        try:
            self.cursor.execute('INSERT INTO to_text (text) VALUES (?)', (text,))
            self.connection.commit()
            # if verbose:
            #     self.logs.log(f"Added to_text : {text}", c='ASK')
            return self.cursor.lastrowid  # Return the ID of the newly created record

        except sqlite3.IntegrityError:
            # If a duplicate entry is found, retrieve the existing record's ID
            self.cursor.execute('SELECT id FROM to_text WHERE text = ?', (text,))
            result = self.cursor.fetchone()
            if result:
                # if verbose:
                #     self.logs.log(f"Duplicate entry found in 'to_text'. Returning existing ID {result[0]}.", c='ASK')
                return result[0]  # Return the existing record's ID
            else:
                self.logs.log(f"An unexpected error occurred.", c='FAIL')
                return None

    def add_from_text(self, text: str, verbose: Optional[bool] = False) -> Optional[int]:
        # Adding a record to 'from_text'
        try:
            self.cursor.execute('INSERT INTO from_text (text) VALUES (?)', (text,))
            self.connection.commit()
            # if verbose:
            #     self.logs.log(f"Added from_text : {text}", c='ASK')
            return self.cursor.lastrowid  # Return the ID of the newly created record

        except sqlite3.IntegrityError:
            # If a duplicate entry is found, retrieve the existing record's ID
            self.cursor.execute('SELECT id FROM from_text WHERE text = ?', (text,))
            result = self.cursor.fetchone()
            if result:
                # if verbose:
                #     self.logs.log(f"Duplicate entry found in 'from_text'. Returning existing ID {result[0]}.", c='ASK')
                return result[0]  # Return the existing record's ID
            else:
                self.logs.log(f"An unexpected error occurred.", c='FAIL')
                return None

    def add_translation(self, from_text: str, to_text: str, verbose: Optional[bool] = False) -> Optional[int]:
        # Set from and to lang id (set in 'add_lang_source' and 'add_lang_target' methods)
        from_lang_id = self.lang_source_id
        to_lang_id = self.lang_target_id

        # Adding a record to 'translation'
        from_text_id = self.add_from_text(from_text, verbose)
        to_text_id = self.add_to_text(to_text, verbose)
        try:
            self.cursor.execute('''
                INSERT INTO translation (from_lang_id, from_text_id, to_lang_id, to_text_id) 
                VALUES (?, ?, ?, ?)
            ''', (from_lang_id, from_text_id, to_lang_id, to_text_id))
            self.connection.commit()
            # if verbose:
            #     to_lang_code = self.get_code_lang_by_id(to_lang_id)
            #     from_lang_code = self.get_code_lang_by_id(from_lang_id)
            #     if not to_lang_code or not from_lang_code:
            #         raise RuntimeError(f"Function '{currentframe().f_code.co_name}': No way! SQLite failed to get lang codes :/)
            #     self.logs.log(f"Added translation: {from_text} ({from_lang_code}) --> {to_text} ({to_lang_code})", c='ASK')
            return self.cursor.lastrowid  # Return the ID of the newly created record

        except sqlite3.IntegrityError:
            # If a duplicate entry is found, retrieve the existing record's ID
            self.cursor.execute('''
                SELECT id FROM translation 
                WHERE from_lang_id = ? AND from_text_id = ? AND to_lang_id = ? AND to_text_id = ?
            ''', (from_lang_id, from_text_id, to_lang_id, to_text_id))
            result = self.cursor.fetchone()
            if result:
                if verbose:
                    self.logs.log(f"Duplicate entry found in 'translation'. Returning existing ID {result[0]}.", c='ASK')
                return result[0]  # Return the existing record's ID
            else:
                raise RuntimeError(f"Function '{currentframe().f_code.co_name}': No way! SQLite failed to get record :/")

    def get_lang(self, id: int) -> Optional[Tuple[int, str, str]]:
        # Retrieving a record from 'langs'
        self.cursor.execute('SELECT * FROM langs WHERE id = ?', (id,))
        return self.cursor.fetchone()

    def get_id_lang_by_code(self, code: str) -> Optional[int]:
        # Get lang id by code
        self.cursor.execute('SELECT id FROM langs WHERE code = ?', (code,))
        result = self.cursor.fetchone()
        if result:
            return result[0]  # Return id if found
        return None

    def get_code_lang_by_id(self, id: int) -> Optional[str]:
        # Get lang id by code
        self.cursor.execute('SELECT code FROM langs WHERE id = ?', (id,))
        result = self.cursor.fetchone()
        if result:
            return result[0]  # Return code if found
        return None

    # def get_translation(self, id: int) -> Optional[Tuple[int, int, str, int, str, int, int]]:
    #     # Retrieving a record from 'translation'
    #     self.cursor.execute('SELECT * FROM translation WHERE id = ?', (id,))
    #     return self.cursor.fetchone()

    # def get_translation_to_text_by_from_text(self, from_text: str, from_lang_id: int, to_lang_id: int, verbose: Optional[bool] = False):
    def get_translation_to_text_by_from_text(self, from_text: str, verbose: Optional[bool] = False):
        # Get translation to_text by from_text
        query = '''
            SELECT
                to_text.text,
                to_text.id
            FROM translation
            JOIN from_text ON translation.from_text_id = from_text.id
            JOIN to_text ON translation.to_text_id = to_text.id
            WHERE translation.from_lang_id = ? 
            AND translation.to_lang_id = ? 
            AND translation.from_text_id = ?
        '''
        self.cursor.execute('SELECT id FROM from_text WHERE text = ?', (from_text,))
        from_text_id_result = self.cursor.fetchone()
        if from_text_id_result:
            from_text_id = from_text_id_result[0]
            self.cursor.execute(query, (self.lang_source_id, self.lang_target_id, from_text_id))
            result = self.cursor.fetchone()
            if result:
                # # Too much verbose 
                # if verbose:
                #     self.logs.log(f"to_text: {result[0]} ({result[1]})", c='ASK')
                return result[0]  # Return the translated text
            else:
                # # Too much verbose 
                # if verbose:
                #     self.logs.log(f"to_text: {None} ({None}) no translation is found for '{from_text}'", c='ASK')
                return None  # Return None if no translation is found
        # if verbose:
        #     self.logs.log(f"to_text: {None} ({None}) from_text does not exist for '{from_text}'", c='ASK')
        return None  # Return None if the from_text does not exist


    def get_all_translations(self, verbose: Optional[bool] = False):
        # Get all translations
        query = '''
            SELECT 
                from_text.id AS from_id, 
                from_text.text AS from_text, 
                to_text.id AS to_id,
                to_text.text AS to_text
            FROM 
                translation
            JOIN 
                from_text ON translation.from_text_id = from_text.id
            JOIN 
                to_text ON translation.to_text_id = to_text.id
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()

    # def get_all_langs(self) -> List[Tuple[int, str, str]]:
    #     # Retrieve all records in 'langs
    #     self.cursor.execute('SELECT * FROM langs')
    #     return self.cursor.fetchall()

    def get_all_translation(self) -> List[Tuple[int, int, int, int, int, int, int]]:
        # Retrieving all records from 'translation'
        self.cursor.execute('SELECT * FROM translation')
        return self.cursor.fetchall()

    def get_all_from_text(self) -> List[Tuple[int, int]]:
        # Retrieving all records from 'from_text'
        self.cursor.execute('SELECT * FROM from_text')
        return self.cursor.fetchall()

    def close(self, verbose: Optional[bool] = False):
        # Closing the connection
        self.connection.close()
        # if verbose:
        #     self.logs.log(f"Closed connection.", c='ASK')
