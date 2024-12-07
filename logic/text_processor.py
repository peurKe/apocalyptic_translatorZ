import re
from unicodedata import normalize as unicodedata_normalize, category as unicodedata_category
# from apocalyptic_translatorZ.logic.utils.restore import RESTORE_SPECIFIC_WORDS

class TextProcessor:

    def __init__(self, logs, params_game):
        # Get logs object instance
        self.logs = logs

        # Get params_game
        self.params_game = params_game
        # Need to replace accentuations ?
        self.need_replace_accentuations = self.params_game.get('need_replace_accentuations')
        # Need to replace special ponctuations ?
        self.need_replace_special_ponctuations = self.params_game.get('need_replace_special_ponctuations')
        # Need to replace asian ponctuations ?
        self.need_replace_asian_ponctuations = self.params_game.get('need_replace_asian_ponctuations')
        # Need to remove specials ?
        self.need_remove_specials = self.params_game.get('need_remove_specials')

        # Initialise original and translated texts
        self.original_text = ''
        self.original_text_len = 0
        self.original_text_binary_len = 0
        self.original_text_origin = 'UNKNOWN'
        self.translated_text = ''
        self.translated_text_len = 0
        self.translated_text_binary_len = 0
        self.translated_origin = 'UNKNOWN'
        pass


    def len_bytes(self, text):
        return len(text.encode('utf-8'))


    # # Truncate without breaking UTF-8 characters
    # def truncate_utf8(self, text):
    #     encoded = text
    #     if len(encoded) > self.original_text_binary_len:
    #         truncated = encoded[:self.original_text_binary_len]
    #         # Make sure we don't cut in the middle of a character
    #         while (truncated[-1] & 0b11000000) == 0b10000000:
    #             truncated = truncated[:-1]
    #         # return truncated + b'\xE2\x80\xA6'  # Add a b'\xE2\x80\xA6' ('…') ellipsis character to indicate truncation
    #         # return truncated + b'\x7E'  # Add a b'\x7E' ('~') ellipsis character to indicate truncation
    #         return truncated
    #     return text
    #     # CONVRGENCE_Data\level4;0x38dfec
    #     # CONVRGENCE_Data\level4;0x40759c


    def truncate_utf8(self, utf8_text):
        """
        Truncate a UTF-8 string to ensure it fits within max_bytes,
        always ending with '…' (ellipsis) if truncation occurs.

        :param utf8_text: Input UTF-8 string to truncate
        :return: UTF-8 string truncated to fit max_bytes
        """
        # # Already done in 'ljust_and_crop_bytes(self)'
        # # If the text fits within max_bytes, return it as is
        # if len(utf8_text) <= self.original_text_binary_len:
        #     return utf8_text

        # UTF-8 for '…' ellipsis
        ellipsis = b'\xE2\x80\xA6'
        # UTF-8 for '~' ellipsis
        ellipsis = b'\x7E'

        # Reserve space for the ellipsis
        max_main_bytes = self.original_text_binary_len - len(ellipsis)

        # Truncate the text, ensuring not to cut through a multibyte character
        truncated = utf8_text[:max_main_bytes]
        while (truncated[-1] & 0b11000000) == 0b10000000:  # Check for continuation byte
            truncated = truncated[:-1]

        # Append the ellipsis
        result = truncated + ellipsis
        return result


    def ljust_and_crop_bytes(self):
        text_bytes = self.translated_text.encode('utf-8')
        len_text_bytes = len(text_bytes)
        # Calculate the number of bytes \x20 to add to reach the target size
        N = self.original_text_binary_len - len_text_bytes

        # Most frequent cases (translated text is shorter than original text)
        if N > 0:
            # Left justify
            text_bytes = text_bytes + b'\x20' * N
            
        # Less frequent cases (translated text is longer than original text)
        elif N < 0:
            justified = False
            self.logs.log(f" len_text_bytes={len_text_bytes}|N={N}|text_bytes={text_bytes}|justified?={justified}", c='NOTIF')

            # Last chance is crop bytes using truncate_utf8 method
            # text_bytes = text_bytes[:self.original_text_binary_len]
            text_bytes = self.truncate_utf8(text_bytes)

            # Get new bytes length for cropped text
            text_bytes_crop = text_bytes.decode('utf-8', errors='ignore')
            text_bytes_crop = text_bytes_crop.encode('utf-8')

            # Get crop length result
            len_text_bytes = len(text_bytes_crop)

            # Re-Calculate the number of bytes \x20 to add to reach the target size
            N = self.original_text_binary_len - len_text_bytes
            if N > 0:
                justified = True
                # Left justify
                text_bytes = text_bytes + b'\x20' * N  # Fill with whitepaces b'\x20' (' ') character to indicate truncation
            self.logs.log(f" len_text_bytes={len_text_bytes}|N={N}|text_bytes={text_bytes}|justified?={justified}", c='NOTIF')

        # # BEGIN TEST PURPOSE ONLY
        # DEBUG CONVRGENCE_Data\level1;0x53d2e4;ONLINE;254;254;143;252
        # print(f"[{text}] | [{repr(text_bytes)}]")
        # # END TEST PURPOSE ONLY
        self.translated_text = text_bytes.decode('utf-8', errors='ignore')


    def replace_accentuations(self):
        # Decompose the string into characters and diacritics
        nfkd_form = unicodedata_normalize('NFKD', self.translated_text)
        # Filter out diacritic marks (category 'Mn') and recompose the string
        self.translated_text = ''.join(char for char in nfkd_form if not unicodedata_category(char).startswith('M'))


    def replace_special_ponctuations(self):
        # # Google Translator double-quotes
        # self.translated_text = self.translated_text.replace('« ', '"').replace(' »', '"')
        # # DeepL Translator double-quotes
        # self.translated_text = self.translated_text.replace('“', '"').replace('”', '"')
        # # Google and DeepL Translator ligature
        # self.translated_text = self.translated_text.replace('œ', 'oe')
        to_replace = {
            '« ': '"', ' »': '"', '«': '"', '»': '"',               # Google Translator double-quotes
            '“ ': '"', ' ”': '"', '“': '"', '”': '"',               # DeepL Translator double-quotes
            ' ,': ',', ' .': '.', ' !': '!', ' ?': '?', ' :': ':',  # Google and DeepL Translator ponctuations
            'œ': 'oe',                                              # Google and DeepL Translator ligature
        }        
        for original, new in to_replace.items():
            self.translated_text = self.translated_text.replace(original, new)


    def replace_asian_ponctuations(self):
        # to_replace = {
        #     '。': '.', '，': ',', '、': ',', '：': ':', '；': ';', '？': '?', '！': '!', '（': '(', '）': ')', '【': '[', 
        #     '】': ']', '「': '"', '」': '"', '『': '"', '』': '"', '〈': '<', '〉': '>', '《': '<', '》': '>', '“': '"', 
        #     '”': '"', '‘': "'", '’': "'", '—': '-', '–': '-', '．': '.', '‥': '..', '…': '...', '゛': '', '゜': '', 'ㅡ': '-', '·': '.', '﹏': '_'
        # }
        to_replace = {
            '。': '.', '，': ',', '、': ',', '：': ':', '；': ';', '？': '?', '！': '!', '（': '(', '）': ')', '【': '[', 
            '】': ']', '「': '"', '」': '"', '『': '"', '』': '"', '“': '"', '”': '"', '‘': "'", '’': "'", '—': '-', '–': '-', 
            '．': '.', '‥': '..', '…': '...', '゛': '', '゜': '', 'ㅡ': '-', '·': '.', '﹏': '_'
        }
        for original, new in to_replace.items():
            self.translated_text = self.translated_text.replace(original, new)


    def remove_specials(self):
        # Define the regex pattern to include allowed characters
        # regex_pattern = r'[^\w\s\.\'",!?/\\\(\)-:\u4e00-\u9fff\u3040-\u309f\uac00-\ud7af]'
        # regex_pattern = r'[^\w\s\.\'",!?/\\\(\)-+=:\u4e00-\u9fff\u3040-\u309f\uac00-\ud7af]'
        # '\-' = hyphen  (escaped)
        #  '–' = en dash (not escaped)
        #  '—' = em dash (not escaped)
        # regex_pattern = r'[^\w\s\.\'",!?\[\]/\\\(\)\-–—\+=:·。，！？：…\u4e00-\u9fff\u3040-\u309f\uac00-\ud7af\u0300-\u036f]'
        regex_pattern = r'[^\w\s\.\'",!?\[\]/\\\(\)\-–—\+=:~\u4e00-\u9fff\u3040-\u309f\uac00-\ud7af\u0300-\u036f]'
        # Apply cleaning
        self.translated_text = re.sub(regex_pattern, "", self.translated_text)


    def set_original_text(self, b_string, origin = 'FILE'):
        # Set original text origin
        self.original_text_origin = origin
        # Set original text
        self.original_text = b_string.s
        # Set original text offset
        self.original_text_offset = b_string.offset
        # Set original text and binary length
        self.original_text_len = b_string.char_length
        self.original_text_binary_len = b_string.binary_length


    def set_translated_text(self, text, alphabet, origin = 'ONLINE'):
        # Set translated text origin
        self.translated_origin = origin
        # Set translated text
        self.translated_text = text

        # Need to replace accentuations ?
        if self.need_replace_accentuations:
            if alphabet in ['latin']:
                self.replace_accentuations()

        # Need to replace special accentuations ?
        if self.need_replace_special_ponctuations:
            self.replace_special_ponctuations()

        # Need to replace asian accentuations ?
        if self.need_replace_asian_ponctuations:
            self.replace_asian_ponctuations()

        # Need to remove specials ?
        if self.need_remove_specials:
            if alphabet in ['latin']:
                self.remove_specials()

        # # ljust and crop needed only for ONLINE translations
        # if self.translated_origin in ['ONLINE']:
        #     self.ljust_and_crop_bytes()
        
        # Now, ljust and crop are needed for ONLINE and custom fixed DB translations
        self.ljust_and_crop_bytes()

        # Following will be used to test binary max length
        # Set binary translated text
        self.translated_text_binary = self.translated_text.encode('utf-8')
        # Set translated text and binary length
        self.translated_text_len = len(self.translated_text)
        self.translated_text_binary_len = len(self.translated_text_binary)


    # def process(self, text):
    #     self.logs.log("Processing text...")
    #     # Exemple : restaurer certains mots spécifiques
    #     for rule in RESTORE_SPECIFIC_WORDS.get("ZONA", {}).get("en", []):
    #         text = text.replace(rule["from"], rule["to"])
    #     return text
