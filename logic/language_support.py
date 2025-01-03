from inspect import currentframe

class LanguageSupport:

    supported_languages = {
        "source": {
            "auto": { "label": "AUTO",               "type": "auto",     "deepl": "auto",    "google": "auto"  },  # Only for source language
            "ru":   { "label": "RUSSIAN",            "type": "cyrillic", "deepl": "ru",      "google": "ru"    },  # Only for source language
            "uk":   { "label": "UKRAINIAN",          "type": "cyrillic", "deepl": "uk",      "google": "uk"    },  # Only for source language
            "zh":   { "label": "CHINESE_SIMPLIFIED", "type": "han",      "deepl": "zh",      "google": "zh-cn" },
            "ja":   { "label": "JAPANESE_HIRAGANA",  "type": "han",      "deepl": "ja",      "google": "ja"    },
            "ko":   { "label": "KOREAN",             "type": "han",      "deepl": "ko",      "google": "ko"    },
        },
        "target": {
            "cs": { "label": "CZECH",              "type": "latin",    "deepl": "cs",      "google": "cs"    },
            "da": { "label": "DANISH",             "type": "latin",    "deepl": "da",      "google": "da"    },
            "de": { "label": "GERMAN",             "type": "latin",    "deepl": "de",      "google": "de"    },
            "en": { "label": "ENGLISH",            "type": "latin",    "deepl": "en-gb",   "google": "en"    },
            "es": { "label": "SPANISH",            "type": "latin",    "deepl": "es",      "google": "es"    },
            "fi": { "label": "FINNISH",            "type": "latin",    "deepl": "fi",      "google": "fi"    },
            "fr": { "label": "FRENCH",             "type": "latin",    "deepl": "fr",      "google": "fr"    },
            "hu": { "label": "HUNGARIAN",          "type": "latin",    "deepl": "hu",      "google": "hu"    },
            "it": { "label": "ITALIAN",            "type": "latin",    "deepl": "it",      "google": "it"    },
            "nl": { "label": "DUTCH",              "type": "latin",    "deepl": "nl",      "google": "nl"    },
            "pl": { "label": "POLISH",             "type": "latin",    "deepl": "pl",      "google": "pl"    },
            "pt": { "label": "PORTUGUESE",         "type": "latin",    "deepl": "pt-pt",   "google": "pt"    },
            "ro": { "label": "ROMANIAN",           "type": "latin",    "deepl": "ro",      "google": "ro"    },
            "sv": { "label": "SWEDISH",            "type": "latin",    "deepl": "sv",      "google": "sv"    },
            "zh": { "label": "CHINESE_SIMPLIFIED", "type": "han",      "deepl": "zh-hans", "google": "zh-cn" },
            "ja": { "label": "JAPANESE_HIRAGANA",  "type": "han",      "deepl": "ja",      "google": "ja"    },
            "ko": { "label": "KOREAN",             "type": "han",      "deepl": "ko",      "google": "ko"    },
        }
    }


    def __init__(self, logs, params_game):
        # Get logs object instance
        self.logs = logs
        # Get params_game
        self.params_game = params_game
        pass


    # Check source and target requested languages are supported
    def check_langs_supported(self, code_source, code_target):
        if not self.is_source_supported(code_source):
            raise RuntimeError(f"Function '{currentframe().f_code.co_name}': '{code_source}' is not a supported as source language.\n")
        if not self.is_target_supported(code_target):
            raise RuntimeError(f"Function '{currentframe().f_code.co_name}': '{code_target}' is not a supported as target language.\n")


    # Source languages
    def is_source_supported(self, code):
        return code in self.supported_languages['source']


    def get_source_language_name(self, code):
        lang = self.supported_languages['source'].get(code, None)
        if lang:
            return lang.get('label')
        else:
            return 'Unknown'


    def get_source_language_type(self, code):
        lang = self.supported_languages['source'].get(code, None)
        if lang:
            return lang.get('type')
        else:
            return 'Unknown'


    def get_source_language_name_by_translator(self, code, translator_name):
        lang = self.supported_languages['source'].get(code, None)
        if lang:
            return lang.get(translator_name)
        else:
            return 'Unknown'


    def get_source_language_codes(self):
        return self.supported_languages['source'].keys()


    # Target languages
    def is_target_supported(self, code):
        return code in self.supported_languages['target']


    def get_target_language_name(self, code):
        lang = self.supported_languages['target'].get(code, None)
        if lang:
            return lang.get('label')
        else:
            return 'Unknown'


    def get_target_language_type(self, code):
        lang = self.supported_languages['target'].get(code, None)
        if lang:
            return lang.get('type')
        else:
            return 'Unknown'


    def get_target_language_name_by_translator(self, code, translator_name):
        lang = self.supported_languages['target'].get(code, None)
        if lang:
            return lang.get(translator_name)
        else:
            return 'Unknown'


    def get_target_language_codes(self):
        return self.supported_languages['target'].keys()
