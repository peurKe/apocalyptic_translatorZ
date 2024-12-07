import os

class Params :

    game_exec_list = [ 'Paradox of Hope.exe', 'CONVRGENCE.exe', 'ZONA.exe', 'ZONAORIGIN.exe' ]
    game_exec = None
    game = None
    default_games = {
        "backup_dir_name": "BACKUP",
        "translations_dir_name": "translations",
        "watermark_in_binary": "THIS_FILE_IS_TRANSLATED",
        "done_file": "done.txt",
        "assets": {
            "min_size": 3,
            "start_address_hex_label": "UnityEngine.Object, UnityEngine",
            "start_address_hex": "55 6E 69 74 79 45 6E 67 69 6E 65 2E 4F 62 6A 65 63 74 2C 20 55 6E 69 74 79 45 6E 67 69 6E 65"
        },
        "levels": {
            "min_size": 2,
            "start_address_hex_label": "....Ç?..Ç?..Ç?..Ç?",
            "start_address_hex": "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 80 3F 00 00 80 3F 00 00 80 3F 00 00 80 3F"
         },
        "need_replace_accentuations": True,
        "need_replace_special_ponctuations": True,
        "need_replace_asian_ponctuations": False,
        "need_remove_specials": True,
        "database": {
            "type": "json",  # json|sqlite
            "db_file": "game.json",  # .json|.sqlite
        },
        "translator": {
            "google": {},
            "deepl": {
                "formality": "prefer_less",
                "split_sentences": "nonewlines",
                "context": "",
                "tag_handling": "xml",
                "ignore_tags": ["x"]
            }
        }
    }
    games = {
        "Paradox of Hope.exe": {
            "steam": {
                "name": "Paradox of Hope",
                "log_path": default_games.get('steam').get('log_path'),
                "app_id": None,
                "manifest_acf_file": None
            },
            "author": "NikZ",
            "name": "Paradox of Hope",
            "safe_name": "Paradox_of_Hope",
            # "name_regex": rb'\x50\x61\x72\x61\x64\x6F\x78\x20\x6F\x66\x20\x48\x6F\x70\x65',  # 'Paradox of Hope'
            "dir_name": "Paradox of Hope",
            "data_dir_name": "Paradox of Hope_Data",
            "backup_dir_name": default_games.get('backup_dir_name'),
            "translations_dir_name": default_games.get('translations_dir_name'),
            "watermark_in_binary": default_games.get('watermark_in_binary'),
            "log_file": "apocalyptic_translatorZ_Paradox_of_Hope.log",
            "done_file": default_games.get('done_file'),
            "default_lang_src": "ru",
            "default_lang_src_force": True,
            "files": {
                "starts": ['level'],
                "ends": [],
                "not_starts": [],
                "not_ends": ['.resS']
            },
            "allowed_ranges": {
                "assets": default_games.get('assets'),
                "levels": default_games.get('levels')
            },
            "need_replace_accentuations": default_games.get('need_replace_accentuations'),
            "need_replace_special_ponctuations": default_games.get('need_replace_special_ponctuations'),
            "need_replace_asian_ponctuations": default_games.get('need_replace_asian_ponctuations'),
            "need_remove_specials": default_games.get('need_remove_specials'),
            "database": {
                "type": "json",  # json|sqlite
                "db_file": "Paradox_of_Hope.json",  # .json|.sqlite
            },
            "translator": default_games.get('translator'),
            # Allow to locate all sentences containing LATIN specific terms
            "include_words": [
                "Paradox of Hope",
            ],
            # Allow to exclude all sentences containing LATIN specific terms
            "exclude_words": []
        },
        "CONVRGENCE.exe": {
            "steam": {
                "name": "CONVRGENCE",
                "log_path": default_games.get('steam').get('log_path'),
                "app_id": 2609610,  # https://store.steampowered.com/app/2609610/CONVRGENCE/
                "manifest_acf_file": f"..\\..\\appmanifest_2609610.acf"
            },
            "author": "NikZ",
            "name": "CONVRGENCE",
            "safe_name": "CONVRGENCE",
            # "name_regex": rb'\x43\x4F\x4E\x56\x52\x47\x45\x4E\x43\x45',  # 'CONVRGENCE'
            "dir_name": "CONVRGENCE",
            "data_dir_name": "CONVRGENCE_Data",
            "backup_dir_name": default_games.get('backup_dir_name'),
            "translations_dir_name": default_games.get('translations_dir_name'),
            "watermark_in_binary": default_games.get('watermark_in_binary'),
            "log_file": "apocalyptic_translatorZ_CONVRGENCE.log",
            "done_file": default_games.get('done_file'),
            "default_lang_src": "ru",
            "default_lang_src_force": True,
            "files": {
                "starts": ['level', 'sharedassets'],
                "ends": [],
                "not_starts": [],
                "not_ends": ['.resource', '.resS']
            },
            "allowed_ranges": {
                "assets": default_games.get('assets'),
                "levels": default_games.get('levels')
            },
            # 0x38dfec
            "need_replace_accentuations": default_games.get('need_replace_accentuations'),
            "need_replace_special_ponctuations": default_games.get('need_replace_special_ponctuations'),
            "need_replace_asian_ponctuations": default_games.get('need_replace_asian_ponctuations'),
            "need_remove_specials": default_games.get('need_remove_specials'),
            "database": {
                "type": "json",  # json|sqlite
                "db_file": "CONVRGENCE.json",  # .json|.sqlite
            },
            "translator": {
                "google": {},
                "deepl": {
                    "formality": "prefer_less",
                    "split_sentences": "nonewlines",
                    "context": "Постапокалиптическая игра в жанре survival horror (похожая на STALKER), " + \
                               "действие которой разворачивается в таинственной и страшной Чернокаменской зоне отчуждения, " + \
                               "куда игроки совершают вылазки в поисках хабара и мистических артефактов, " + \
                               "попутно отбиваясь от бандитов, дикой фауны и демонов, выходящих на охоту под покровом ночи.",
                    "tag_handling": "xml",
                    "ignore_tags": ["x"]
                }
            },
            # Allow to locate all sentences containing LATIN specific terms
            "include_words": [
                "CONVRGENCE",
                "Paradox of Hope",
            ],
            # Allow to exclude all sentences containing LATIN specific terms
            "exclude_words": [
                "Paradox of Hope",
            ]
        },
        "ZONA.exe": {
            "steam": {
                "name": "Z.O.N.A Project X",
                "log_path": default_games.get('steam').get('log_path'),
                "app_id": 2142450, # https://store.steampowered.com/app/2142450/ZONA_Project_X_VR/
                "manifest_acf_file": f"..\\..\\appmanifest_2142450.acf"
            },
            "author": "AGamingPlus",
            "name": "ZONA",
            "safe_name": "ZONA",
            # "name_regex": rb'\x5A\x2E\x4F\x2E\x4E\x2E\x41',  # 'Z.O.N.A'
            "dir_name": "ZONA",
            "data_dir_name": "ZONA_Data",
            "backup_dir_name": default_games.get('backup_dir_name'),
            "translations_dir_name": default_games.get('translations_dir_name'),
            "watermark_in_binary": default_games.get('watermark_in_binary'),
            "log_file": "apocalyptic_translatorZ_ZONA.log",
            "done_file": default_games.get('done_file'),
            "default_lang_src": "uk",
            "default_lang_src_force": True,
            "files": {
                "starts": ['level', 'resources.assets'],
                "ends": [],
                "not_starts": [],
                "not_ends": ['.resource', '.resS']
            },
            "allowed_ranges": {
                "assets": {
                    "min_size": 6,
                    "start_address_hex_label": "AFU _OTSTUPNIK",
                    "start_address_hex": "41 46 55 20 5F 4F 54 53 54 55 50 4E 49 4B"
                },
                "levels": default_games.get('levels')
            },
            "need_replace_accentuations": default_games.get('need_replace_accentuations'),
            "need_replace_special_ponctuations": default_games.get('need_replace_special_ponctuations'),
            "need_replace_asian_ponctuations": default_games.get('need_replace_asian_ponctuations'),
            "need_remove_specials": default_games.get('need_remove_specials'),
            "database": {
                "type": "json",  # json|sqlite
                "db_file": "ZONA.json",  # .json|.sqlite
            },
            "translator": default_games.get('translator'),
            # Allow to locate all sentences containing LATIN specific terms
            "include_words": [
                "Z.O.N.A",
            ],
            # Allow to exclude all sentences containing LATIN specific terms
            "exclude_words": []
        },
        "ZONAORIGIN.exe": {
            "steam": {
                "name": "Z.O.N.A Origin",
                "log_path": default_games.get('steam').get('log_path'),
                "app_id": 2539520, # https://store.steampowered.com/app/2539520/ZONA_Origin/
                "manifest_acf_file": f"..\\..\\appmanifest_2539520.acf"
            },
            "author": "AGamingPlus",
            "name": "ZONAORIGIN",
            "safe_name": "ZONAORIGIN",
            # "name_regex": rb'\x5A\x2E\x4F\x2E\x4E\x2E\x41\x20\x4F\x52\x49\x47\x49\x4E',  # 'Z.O.N.A ORIGIN'
            "dir_name": "ZONAORIGIN",
            "data_dir_name": "ZONAORIGIN_Data",
            "backup_dir_name": default_games.get('backup_dir_name'),
            "translations_dir_name": default_games.get('translations_dir_name'),
            "watermark_in_binary": default_games.get('watermark_in_binary'),
            "log_file": "apocalyptic_translatorZ_ZONAORIGIN.log",
            "done_file": default_games.get('done_file'),
            "default_lang_src": "uk",
            "default_lang_src_force": True,
            "files": {
                "starts": ['level', 'resources.assets'],
                "ends": [],
                "not_starts": [],
                "not_ends": ['.resource', '.resS']
            },
            "allowed_ranges": {
                "assets": {
                    "min_size": 6,
                    "start_address_hex_label": "AFU _OTSTUPNIK",
                    "start_address_hex": "41 46 55 20 5F 4F 54 53 54 55 50 4E 49 4B"
                },
                "levels": default_games.get('levels')
            },
            "need_replace_accentuations": default_games.get('need_replace_accentuations'),
            "need_replace_special_ponctuations": default_games.get('need_replace_special_ponctuations'),
            "need_replace_asian_ponctuations": default_games.get('need_replace_asian_ponctuations'),
            "need_remove_specials": default_games.get('need_remove_specials'),
            "database": {
                "type": "json",  # json|sqlite
                "db_file": "ZONAORIGIN.json",  # .json|.sqlite
            },
            "translator": default_games.get('translator'),
            # Allow to locate all sentences containing LATIN specific terms
            "include_words": [
                "Z.O.N.A ORIGIN",
            ],
            # Allow to exclude all sentences containing LATIN specific terms
            "exclude_words": [
                "Z.O.N.A ProjectX",
            ]
        }
    }


    def __init__(self):
        game_found = False
        for game_exec in self.game_exec_list:
            if os.path.exists(game_exec):
                # Set specific game params
                self.game_exec = game_exec
                if self.games.get(self.game_exec, None):
                    self.game = self.games[self.game_exec]
                game_found = True

        if not game_found:
            raise FileNotFoundError(f" Heck! The script is not where it should be. Move this script in one of the same directory as the '{'\' or \''.join(self.game_exec_list)}' executable file. Then run this moved script again.")
