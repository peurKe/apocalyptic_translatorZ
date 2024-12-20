
class Cyrillic:

    def __init__(self, logs, params_game):
        # Get logs object instance
        self.logs = logs
        # Get params_game
        self.params_game = params_game

        # Allow to locate all sentences containing LATIN specific terms
        self.include_words = '|'.join(self.params_game.get('include_words')).encode('utf-8')

        # Regular expression for Cyrillic bytes (Russian + Specific + Ukrainian pattern)
        self.CYRILLIC_BYTES = rb'\xD0[\x80-\xBF]|\xD0[\xA0-\xFF]|\xD1[\x80-\xBF]|\xD2[\x80-\xBF]|\xD3[\x80-\xBF]|\xD4[\x80-\x8F]'
        # Regular latin letters (case-insensitive) # /!\ CAN BE A PROBLEM (REMOVE IF CHANGE BREAKING)
        self.LATIN_LETTERS_BYTES = rb'[a-zA-Z]'
        # 'P.S.|VR|Discord|DISCORD|SteamVR' bytes
        self.LATIN_BYTES = rb'\x50\x2E\x53\x2E|\x56\x52|\x44\x69\x73\x63\x6F\x72\x64|\x44\x49\x53\x43\x4F\x52\x44|\x53\x74\x65\x61\x6D\x56\x52'  # 'P.S.|VR|Discord|DISCORD|SteamVR'
        # Whitespace byte
        self.WSPACE_BYTE = rb'\x20'  # ' '
        # '–' dash bytes | '—' em dash bytes
        self.DASH_BYTES = rb'\xE2\x80\x93|\xE2\x80\x94'  # '–|—'
        # Line Feed byte
        self.CRLF_BYTES = rb'\x0D|\x0A'  # '\r|\n'
        # Numbers bytes
        self.NUMBERS_BYTES = rb'[\x30-\x39]'  # 0123456789
        # Latin punctuation bytes
        self.PUNCTUATION_BYTES = rb'\xC2\xAB|\xC2\xBB|\x21|\x22|\x27|\x28|\x29|\x2B|\x2C|\x2D|\x2E|\x2F|\x3A|\x3F|\x5C|\x5F'
        # Last bytes depend on game title or author
        self.CYRILLIC_LAST_BYTES_BY_AUTHOR =  {
            "AGamingPlus": self.CYRILLIC_BYTES + rb'|' + self.PUNCTUATION_BYTES,
            "NikZ": self.CYRILLIC_BYTES + rb'|' + self.PUNCTUATION_BYTES + rb'|' + self.NUMBERS_BYTES
        }
        # Initialize cyrillic pattern and regex
        self.initialize_cyrillic()

    def initialize_cyrillic(self):
        
        

        # Cyrillic content pattern
        self.CYRILLIC_CONTENT_PATTERN = (
            rb'(?:' + self.CYRILLIC_BYTES +
                      # Allow to locate all sentences containing LATIN specific terms
                      self.include_words +
            rb'|' + self.WSPACE_BYTE +
            rb'|' + self.DASH_BYTES +
            rb'|' + self.LATIN_BYTES +
            rb'|' + self.LATIN_LETTERS_BYTES +  # /!\ CAN BE A PROBLEM (REMOVE IF CHANGE BREAKING)
            rb'|' + self.CRLF_BYTES +
            rb'|' + self.NUMBERS_BYTES +
            rb'|' + self.PUNCTUATION_BYTES + rb')'
        )
        # Cyrillic Last bytes
        self.CYRILLIC_LAST_BYTES =  self.CYRILLIC_LAST_BYTES_BY_AUTHOR.get(self.params_game.get('author'))
        # Cyrillic Regex
        self.CYRILLIC_REGEX = (
            rb'((?:' + self.CYRILLIC_BYTES + rb')'  # Premier caractère : cyrillique
            + rb'(?:' + self.CYRILLIC_CONTENT_PATTERN + rb')*'  # Contenu valide
            + rb'(?:' + self.CYRILLIC_LAST_BYTES + rb')'  # Dernier caractère
            + rb')'
        )

# \x56\x52\x3F\x20 = 'VR? '
# \xE2\x84\x96 = '№' (finally not translated because translation in french is quite bad: no)
# \xE2\x80\x94 = '—' (long dash) (finally not translated because translation in french is not usefull: no)
# \xD0[\x81\x86-\xBF]|\xD1[\x80-\x8F]|\xD2[\x90-\x91]|\xD2[\x84\x94]|\xD1\x96|\xD0[\x90-\xAF] = Cyrillic
# \x0a|\x20|\x21|\x22|\x27|\x28|\x29|\x2B|\x2C|\x2D|\x2E|\x2F|\x3A|\x3F|\x5C|\x5F = Punctuation

# # Cyrillic bytes to select
# \xD0[\x81\x86-\xBF] : Correspond aux caractères UTF-8 cyrilliques dans la plage D0 81, D0 86, et de D0 90 à D0 BF.
# \xD1[\x80-\x8F] : Correspond aux caractères cyrilliques de D1 80 à D1 8F.
# \xD2[\x90-\x91] et \xD2[\x84\x94] : Correspond aux caractères spécifiques comme Ґ et Є.
# \xD1\x96 et \xD0[\x90-\xAF] : Inclut le caractère ukrainien і et d'autres caractères de base de la langue russe et ukrainienne.
# cyrillic_bytes = [
#     b'\xD0\x90', b'\xD0\x91', b'\xD0\x92', b'\xD0\x93', b'\xD0\x94',
#     b'\xD0\x95', b'\xD0\x81', b'\xD0\x96', b'\xD0\x97', b'\xD0\x98',
#     b'\xD0\x99', b'\xD0\x9A', b'\xD0\x9B', b'\xD0\x9C', b'\xD0\x9D',
#     b'\xD0\x9E', b'\xD0\x9F', b'\xD0\xA0', b'\xD0\xA1', b'\xD0\xA2',
#     b'\xD0\xA3', b'\xD0\xA4', b'\xD0\xA5', b'\xD0\xA6', b'\xD0\xA7',
#     b'\xD0\xA8', b'\xD0\xA9', b'\xD0\xAA', b'\xD0\xAB', b'\xD0\xAC',
#     b'\xD0\xAD', b'\xD0\xAE', b'\xD0\xAF', b'\xD0\xB0', b'\xD0\xB1',
#     b'\xD0\xB2', b'\xD0\xB3', b'\xD0\xB4', b'\xD0\xB5', b'\xD0\xB6',
#     b'\xD0\xB7', b'\xD0\xB8', b'\xD0\xB9', b'\xD0\xBA', b'\xD0\xBB',
#     b'\xD0\xBC', b'\xD0\xBD', b'\xD0\xBE', b'\xD0\xBF', b'\xD1\x80',
#     b'\xD1\x81', b'\xD1\x82', b'\xD1\x83', b'\xD1\x84', b'\xD1\x85',
#     b'\xD1\x86', b'\xD1\x87', b'\xD1\x88', b'\xD1\x89', b'\xD1\x8A',
#     b'\xD1\x8B', b'\xD1\x8C', b'\xD1\x8D', b'\xD1\x8E', b'\xD1\x8F',
#     # PONCTUATION
#     b'\xc2\xab', # «
#     b'\xc2\xbb', # »
#     b'\x0a',   # LF
#     b'\x20'    # Whitespace
#     b'\x21',   # !
#     b'\x22',   # "
#     b'\x27',   # '
#     b'\x28',   # (
#     b'\x29',   # )
#     b'\x2B',   # +
#     b'\x2C',   # ,
#     b'\x2D',   # -
#     b'\x2E',   # .
#     b'\x2F',   # /
#     b'\x3A',   # :
#     b'\x3F',   # ?
#     b'\x5C',   # \
#     b'\x5F',   # _
# ]

# М     Ы     Л     О
# D0 9C D0 AB D0 9B D0 9E

# Револьвер
# Р     е     в     о     л     ь     в     е     р     
# D0 9F D0 B5 D0 B2 D0 BE D0 BB D0 AC D0 B2 D0 B5 D1 80
# D0 9F D0 95 D0 92 D0 9E

# ЦЕНА НЕИЗ
# Ц     Е     Н     А        Н     Е     И     З
# D0 A6 D0 95 D0 9D D0 90 20 D0 9D D0 95 D0 98 D0 97

# С     У     Х     А     Р     И     К     И
# D0 A1 D0 A3 D0 A5 D0 90 D0 A0 D0 98 D0 9A D0 98

# С     у     х     а     р     и     к     и
# D0 A1 D1 83 D1 85 D0 B0 D1 80 D0 B8 D0 BA D0 B8

# К     а     с     с     е     т     а
# D0 9A D0 B0 D1 81 D1 81 D0 B5 D1 82 D0 B0

# Н     е     т
# D0 9D D0 B5 D1 82

# ######################################
# BEGIN NOT TRANSLATED IN sharedassets1.assets
# ######################################
# Ч     а     й     (0x06D56B34) / Tea
# D0 A7 D0 B0 D0 B9
# Х     И     С     (0x06D56C5C) / Glow Stick ['SON': restore words will be needed]
# D0 A5 D0 98 D0 A1
# П     л     а     т     а     (0x06D5D1C4) / Circuit Board ['Payer': restore words will be needed]
# D0 9F D0 BB D0 B0 D1 82 D0 B0
# И     з     м     е     н     е     н     н     а     я        п     л     а     т     а     (0x06D5D1E8) / Altered Circuit Board ['Frais modifies': restore words will be needed]
# D0 98 D0 B7 D0 BC D0 B5 D0 BD D0 B5 D0 BD D0 BD D0 B0 D1 8F 20 D0 BF D0 BB D0 B0 D1 82 D0 B0
# ######################################
# END NOT TRANSLATED IN sharedassets1.assets
# ######################################

# ######################################
# BEGIN NOT TRANSLATED IN sharedassets2.assets
# ######################################
# ш     т     .  (0x53ef59d) / pcs. ['piece': restore words will be needed]
# D1 88 D1 82 2E
# ######################################
# END NOT TRANSLATED IN sharedassets2.assets
# ######################################
# А     И   АИ   
# D0 90 D0 98 
# 
# Д     а
# D0 94 D0 B0
# 
# И     г     р     а     т     ь
# D0 98 D0 B3 D1 80 D0 B0 D1 82 D1 8C
# 
# Latin	Char Unicode	Hex (UTF-8)	Binaire (UTF-8)
# A	    А	U+0410	D0 90	11010000 10100000
# B	    Б	U+0411	D0 91	11010000 10100001
# V	    В	U+0412	D0 92	11010000 10100010
# G	    Г	U+0413	D0 93	11010000 10100011
# D	    Д	U+0414	D0 94	11010000 10100100
# E	    Е	U+0415	D0 95	11010000 10100101
# Yo	Ё	U+0401	D0 81	11010000 10000001
# Zh	Ж	U+0416	D0 96	11010000 10100110
# Z 	З	U+0417	D0 97	11010000 10100111
# I 	И	U+0418	D0 98	11010000 10101000
# Y 	Й	U+0419	D0 99	11010000 10101001
# K 	К	U+041A	D0 9A	11010000 10101010
# L 	Л	U+041B	D0 9B	11010000 10101011
# M 	М	U+041C	D0 9C	11010000 10101100
# N 	Н	U+041D	D0 9D	11010000 10101101
# O 	О	U+041E	D0 9E	11010000 10101110
# P 	П	U+041F	D0 9F	11010000 10101111
# R 	Р	U+0420	D0 A0	11010000 10110000
# S 	С	U+0421	D0 A1	11010000 10110001
# T 	Т	U+0422	D0 A2	11010000 10110010
# U 	У	U+0423	D0 A3	11010000 10110011
# F 	Ф	U+0424	D0 A4	11010000 10110100
# Kh	Х	U+0425	D0 A5	11010000 10110101
# Ts	Ц	U+0426	D0 A6	11010000 10110110
# Ch	Ч	U+0427	D0 A7	11010000 10110111
# Sh	Ш	U+0428	D0 A8	11010000 10111000
# Shch	Щ	U+0429	D0 A9	11010000 10111001
# Hard Sign	Ъ	U+042A	D0 AA	11010000 10111010
# Y (with hook)	Ы	U+042B	D0 AB	11010000 10111011
# Soft Sign	Ь	U+042C	D0 AC	11010000 10111100
# E 	Э	U+042D	D0 AD	11010000 10111101
# Yu	Ю	U+042E	D0 AE	11010000 10111110
# Ya	Я	U+042F	D0 AF	11010000 10111111
# a	    а	U+0430	D0 B0	11010000 10110000
# b	    б   U+0431	D0 B1	11010000 10110001
# v	    в	U+0432	D0 B2	11010000 10110010
# g 	г	U+0433	D0 B3	11010000 10110011
# d 	д	U+0434	D0 B4	11010000 10110100
# e 	е	U+0435	D0 B5	11010000 10110101
# yo	ё	U+0451	D1 91	11010001 10010001
# zh	ж	U+0436	D0 B6	11010000 10110110
# z 	з	U+0437	D0 B7	11010000 10110111
# i 	и	U+0438	D0 B8	11010000 10111000
# y 	й	U+0439	D0 B9	11010000 10111001
# k 	к	U+043A	D0 BA	11010000 10111010
# l 	л	U+043B	D0 BB	11010000 10111011
# m 	м	U+043C	D0 BC	11010000 10111100
# n 	н	U+043D	D0 BD	11010000 10111101
# o 	о	U+043E	D0 BE	11010000 10111110
# p 	п	U+043F	D0 BF	11010000 10111111
# r 	р	U+0440	D1 80	11010001 10000000
# s 	с	U+0441	D1 81	11010001 10000001
# t 	т	U+0442	D1 82	11010001 10000010
# u 	у	U+0443	D1 83	11010001 10000011
# f 	ф	U+0444	D1 84	11010001 10000100
# kh	х	U+0445	D1 85	11010001 10000101
# ts	ц	U+0446	D1 86	11010001 10000110
# ch	ч	U+0447	D1 87	11010001 10000111
# sh	ш	U+0448	D1 88	11010001 10001000
# shch	щ	U+0449	D1 89	11010001 10001001
# hard sign	ъ	U+044A	D1 8A	11010001 10001010
# y (with hook)	ы	U+044B	D1 8B	11010001 10001011
# soft sign	ь	U+044C	D1 8C	11010001 10001100
# e 	э	U+044D	D1 8D	11010001 10001101
# yu	ю	U+044E	D1 8E	11010001 10001110
# ya	я	U+044F	D1 8F	11010001 10001111

# 3000-303F   (CJK Symbols and Punctuation)
# 3040-309F   (Hiragana)
# 30A0-30FF   (Katakana)
# 3400-4DBF   (CJK Unified Ideographs Extension A)
# 4E00-9FFF   (CJK Unified Ideographs)
# AC00-D7A3   (Hangul Syllables)
# 1100-11FF   (Hangul Jamo Basic consonants and vowels)
# 3130-318F   (Hangul Compatibility Jamo Compatibility with legacy systems)

# TextMeshPro Unicode range
# 3000-303F,3040-309F,30A0-30FF,3400-4DBF,4E00-9FFF,AC00-D7A3,1100-11FF,3130-318F

# https://chinesefonts.org/fonts/noto-sans-cjk-regular
# 
