import deepl
import googletrans
from time import sleep
from sys import exit as sys_exit
from colorama import Fore, Style
# import re  # inject_line_breaks_dot_priority_2

class Translator:

    def __init__(self, logs, params_game, translators, translator_api_key, language_support):
        # Get logs object instance
        self.logs = logs
        # Get params_game
        self.params_game = params_game

        # Initialize translators list in order of preference
        self.translators_preferred = translators
        self.translators = []
        self.translator_api_key = translator_api_key

        # Initialize full sentences to exclude from translation
        self.exclude_full_sentences = self.params_game.get('translator').get('exclude_full_sentences')

        # Get language support
        self.language_support = language_support
        
        # Initialize lang source and target
        self.lang_source = dict(deepl='ru', google='ru')
        self.lang_target = dict(deepl='en', google='en')
        # Initialize lang source and target types
        self.lang_source_type = 'auto'
        self.lang_target_type = 'auto'

        # Initialize glossary
        self.glossary = {
            "deepl": None,
            "google": None
        }

        # Allow to set the first available translator in the list as the preferred one
        is_preferred_for_online_not_already_set = True
        # Allow to known if failback translator (currently Google one) is set
        is_failback_not_already_set = True

        # All translator in order of preference
        for translator in translators:

            # Select the translator to use
            try:

                # Google translator
                if translator == 'google':
                    # If failback is not alreday set
                    if is_failback_not_already_set:
                        # Attempt to instanciate the Google translator
                        t = googletrans.Translator()
                        self.translators.append(
                            dict(
                                translator=t,
                                translator_name=translator,
                                translator_args=self.params_game.get('translator').get(translator),
                                # Set 'preferred_for_online' flag
                                preferred_for_online=is_preferred_for_online_not_already_set
                            )
                        )
                        # Reset preferred and failback flags (Google is the failback translator)
                        is_preferred_for_online_not_already_set = False
                        is_failback_not_already_set = False

                # DeepL translator
                elif translator == 'deepl':
                    try:
                        # Attempt to use the DeepL translator only when an API authentication key is defined
                        if self.translator_api_key:
                            t = deepl.Translator(
                                self.translator_api_key,  # DeepL API Authentication key (secret)
                                send_platform_info=False  # without sending any platform info to DeepL python
                            )
                            self.translators.append(
                                dict(
                                    translator=t,
                                    translator_name=translator,
                                    translator_args=self.params_game.get('translator').get(translator),
                                    # Set 'preferred_for_online' flag
                                    preferred_for_online=is_preferred_for_online_not_already_set
                                )
                            )
                            # Reset preferred flags (DeepL is not the failback translator)
                            is_preferred_for_online_not_already_set = False

                        # API authentication key is not defined
                        else:
                            # raise an exception to force Google failback
                            raise ValueError(f"A DeepL API key is required for DeepL API authentication.")

                    except Exception as e:
                        self.logs.log(f" [WARN] DeepL translator failed. Check your DeepL API key and your DeepL API usage. Google translator will be used as failback.", c='FAIL', force=True)
 
                        # Attempting to use the Google translator as a failback solution
                        if is_failback_not_already_set:
                            t = googletrans.Translator()
                            self.translators.append(
                                dict(
                                    translator=t,
                                    translator_name='google',
                                    translator_args=self.params_game.get('translator').get('google'),
                                    # Set 'preferred_for_online' flag
                                    preferred_for_online=is_preferred_for_online_not_already_set
                                )
                            ),
                            is_preferred_for_online_not_already_set = False
                            is_failback_not_already_set = False

                # Unsupported translator
                else:
                    # Raise an error if translator is not supported
                    raise ValueError(f"Translator '{translator}' is not supported.")

            except Exception as e:
                raise RuntimeError(f"Translation initialization error: {type(e).__name__}: {e}")

        self.logs.log(f" [DEBUG] self.translators: {self.translators}", c='DEBUG', force=True)
        # input("Press any key to exit...")
        # sys_exit(0)

        pass


    def get_translators_preferred(self):
        """
        Get translators names form translators list.
        """
        return self.translators_preferred


    def get_translators_available(self):
        """
        Get translators names form translators list.
        """
        return list(map(lambda d: d.get('translator_name', None), self.translators))


    def set_langs(self, lang_source, lang_target):
        """
        Set source and target langs accordingly to supported languages for all available translators.
        """
        for available_translator in self.get_translators_available():
            self.lang_source[available_translator] = self.language_support.get_source_language_name_by_translator(
                code=lang_source,
                translator_name=available_translator
            )
            self.lang_target[available_translator] = self.language_support.get_target_language_name_by_translator(
                code=lang_target,
                translator_name=available_translator
            )
            self.lang_source_type = self.language_support.get_source_language_type(code=lang_source)
            self.lang_target_type = self.language_support.get_target_language_type(code=lang_target)


    def get_glossary(self, translator_name, lang_source, lang_target):
        """
        Get glossary from params game.
        """
        # # BEGIN TESTING PURPOSE ONLY
        # self.logs.log(f"self.lang_source.get(translator_name): {lang_source}", c='ASK', force=True)
        # self.logs.log(f"self.lang_target.get(translator_name): {lang_target}", c='ASK', force=True)
        # self.logs.log(f"glossary: {self.params_game.get('translator').get(translator_name).get('glossary').get(lang_source).get(lang_target)}", c='ASK', force=True)
        # input("Press enter to continue...")
        # sys_exit(0)
        # # END TESTING PURPOSE ONLY

        glossary_lang_source = self.params_game.get('translator').get(translator_name).get('glossary_lang_source')
        glossary_lang_target = self.params_game.get('translator').get(translator_name).get('glossary_lang_target')

        no_glossary = False
        if lang_source not in glossary_lang_source or lang_target not in glossary_lang_target:
            no_glossary = True

        # Source and/or target language is not defined in glossary params game
        if no_glossary:
            self.logs.log(f" No glossary for '{translator_name}' translator and '{lang_source}' source language and '{lang_target}' target language", c='DEBUG', force=True)
            # Return an empty glossary
            return self.params_game.get('translator').get(translator_name).get('glossary_empty')
        
        # Return glossary
        return self.params_game.get('translator').get(translator_name).get('glossary').get(lang_source).get(lang_target)


    def initialize_glossary(self):
        """
        Initialize glossary accordingly to source and target langs.
        """
        for translator in self.translators:
            if translator.get('translator_name') == 'deepl':
                lang_source = self.lang_source.get('deepl')
                lang_target = self.lang_target.get('deepl')
                # Attempt to create use the DeepL translator only when an API authentication key is defined
                self.glossary['deepl'] = translator.get('translator').create_glossary(
                    f"DeepL glossary for {lang_source} to {lang_target}",
                    source_lang=lang_source,
                    target_lang=lang_target,
                    entries=self.get_glossary('deepl', lang_source, lang_target)
                )


    def inject_line_breaks(self, source, translated):
        """
        Reinject line breaks (\n) from source text into the translated text,
        handling cases where the number of words differs between source and translated.
        """
        # Split the source text into segments based on '\n'
        source_segments = source.split('\n')

        # Flatten the translated text into a list of words
        translated_words = translated.split()

        # Total word count in the source text (for proportional distribution)
        total_source_word_count = sum(len(segment.split()) for segment in source_segments)

        # Avoid division by zero
        if total_source_word_count == 0:
            return translated  # If the source has no words, return the translated as-is

        # Reconstruct the translated text with '\n' injected
        result = []
        word_index = 0

        for segment in source_segments:
            # Word count for the current source segment
            segment_word_count = len(segment.split())

            # Calculate proportion of words to allocate from the translated text
            proportion = segment_word_count / total_source_word_count
            words_to_allocate = max(1, round(proportion * len(translated_words)))

            # Extract words for this segment from the translated text
            segment_translated = ' '.join(translated_words[word_index:word_index + words_to_allocate])
            result.append(segment_translated)

            # Update the word index
            word_index += words_to_allocate

        # Add any remaining words to the last segment to avoid loss
        if word_index < len(translated_words):
            result[-1] += ' ' + ' '.join(translated_words[word_index:])

        # Join results + Remove all trailing '\n'
        return ('\n'.join(result)).rstrip("\n")


    # def inject_line_breaks_dot_priority(self, source, translated):
    #     """
    #     Reinject line breaks (\n) from source text into the translated text,
    #     prioritizing placing line breaks right after '.' when possible.
    #     """
    #     # Split the source text into segments based on '\n'
    #     source_segments = source.split('\n')

    #     # Flatten the translated text into a list of words
    #     translated_words = translated.split()

    #     # Total word count in the source text (for proportional distribution)
    #     total_source_word_count = sum(len(segment.split()) for segment in source_segments)

    #     # Avoid division by zero
    #     if total_source_word_count == 0:
    #         return translated  # If the source has no words, return the translated as-is

    #     # Reconstruct the translated text with '\n' injected
    #     result = []
    #     word_index = 0

    #     for segment in source_segments:
    #         # Word count for the current source segment
    #         segment_word_count = len(segment.split())

    #         # Calculate proportion of words to allocate from the translated text
    #         proportion = segment_word_count / total_source_word_count
    #         words_to_allocate = max(1, round(proportion * len(translated_words)))

    #         # Extract words for this segment from the translated text
    #         segment_translated = translated_words[word_index:word_index + words_to_allocate]

    #         # 🔥 Prioritize placing a line break after the first '.' in the segment
    #         for i in range(len(segment_translated)):
    #             if segment_translated[i].endswith('.'):
    #                 # Insérer un saut de ligne juste après ce mot contenant le point
    #                 segment_translated[i] += '\n'
    #                 break  # On arrête après avoir inséré un saut de ligne

    #         result.append(' '.join(segment_translated))

    #         # Update the word index
    #         word_index += words_to_allocate

    #     # Add any remaining words to the last segment to avoid loss
    #     if word_index < len(translated_words):
    #         result[-1] += ' ' + ' '.join(translated_words[word_index:])

    #     return '\n'.join(result)


    # def inject_line_breaks_dot_priority_2(self, source, translated):
    #     """
    #     Reinject line breaks (\n) from source text into the translated text,
    #     prioritizing placing line breaks right after '.' when possible.
    #     """
    #     # Split the source text into segments based on '\n'
    #     source_segments = source.split('\n')

    #     # Flatten the translated text into a list of words
    #     translated_words = translated.split()

    #     # Total word count in the source text (for proportional distribution)
    #     total_source_word_count = sum(len(segment.split()) for segment in source_segments)

    #     # Avoid division by zero
    #     if total_source_word_count == 0:
    #         return translated  # If the source has no words, return the translated as-is

    #     # Reconstruct the translated text with '\n' injected
    #     result = []
    #     word_index = 0

    #     for segment in source_segments:
    #         # Word count for the current source segment
    #         segment_word_count = len(segment.split())

    #         # Calculate proportion of words to allocate from the translated text
    #         proportion = segment_word_count / total_source_word_count
    #         words_to_allocate = max(1, round(proportion * len(translated_words)))

    #         # Extract words for this segment from the translated text
    #         segment_translated = translated_words[word_index:word_index + words_to_allocate]

    #         # 🔥 Prioritize placing a line break after the first '.' in the segment
    #         for i in range(len(segment_translated)):
    #             if re.search(r'\.$', segment_translated[i]):  # Mot se terminant par un point
    #                 segment_translated[i] += '\n'
    #                 break  # On arrête après avoir inséré un saut de ligne

    #         # Si le segment se termine par un point mais qu'il n'a pas été pris en compte, on force le saut de ligne
    #         if len(segment_translated) > 0 and re.search(r'\.$', segment_translated[-1]):
    #             segment_translated[-1] += '\n'

    #         result.append(' '.join(segment_translated))

    #         # Update the word index
    #         word_index += words_to_allocate

    #     # Add any remaining words to the last segment to avoid loss
    #     if word_index < len(translated_words):
    #         result[-1] += ' ' + ' '.join(translated_words[word_index:])

    #     # 🔥 Force the insertion of line breaks after every "."
    #     final_text = '\n'.join(result)
    #     final_text = re.sub(r'(\.)(\s*)(?!\n)', r'\1\n', final_text)  # Forcer le \n après chaque point

    #     return final_text


    def google_translate(self, text, translator, translator_args):
        """
        Translate using Google Translate.
        Args in 'translator_args' for Google's translator are not yet in use
        """
        # # BEGIN TESTING PURPOSE ONLY
        # text = "Вы выжили!\n\nВсе найденные в этом рейде предметы будут проданы скупщику.\n\n\n\n\n\nНайдено хабара на:                руб."
        # text = "В этой демо-версии вы познакомитесь с Рейдами -\n" + \
        #        "бесконечным игровым режимом с прогрессией и процедурной генерацией уровней (доступно только Убежище).\n" + \
        #        "Присоединяйтесь к Discord, чтобы поделиться фидбэком, сообщить об ошибках и просто быть в курсе всех событий.\n" + \
        #        "А также не забудьте добавить игру в свой список желаемого!"
        # text = "Схватить                       Схватить"
        # text = "Онлайн рейтинги\n- Страховка снаряжения\n- Химический источник света\n- Шприц с адреналином\n- Патроны теперь можно перекладывать из одного \nмагазина в другой, зажав триггер, по аналогии с \nкоробкой патронов.\r\n- При продаже предметов торговцу, на экране \nкомпьютера теперь высвечивается их название и \nстоимость.\r\n- На часы добавлена полоска ХП."
        # text = "Отлично, все готово! \n\nПомните, что вы можете изменить эти параметры\nи настроить их более детально в любое время,\nвыбрав \"Управление\" в Меню."
        # text = "штук.\nСовместимость: АКМ.\nЗажмите триггер для\nиспользования"
        # text = "Сразитесь с новыми противниками \n- волками и используйте новые \nмеханики, такие как разделка."
        # text = "Исследуйте новую обширную \nоткрытую локацию - Лес, \nполную секретов."
        # text = "Отпустите рюкзак\r\nи он автоматически\r\nвернется на место"
        # text = "БЕССМЕРТИЕ\n\n\n\nДОБАВИТЬ 10000 РУБ.\n\n\n\nВЫПОЛНИТЬ ТЕКУЩЕЕ ЗАДАНИЕ\n\n\n\nМАКСИМАЛЬНАЯ РЕПУТАЦИЯ\n\n\n\nОБНУЛИТЬ СОХРАНЕНИЕ"
        # # END TESTING PURPOSE ONLY

        # # BEGIN TESTING PURPOSE ONLY
        # self.logs.log(f"{text}", c='ASK', force=True)
        # # END TESTING PURPOSE ONLY

        # Google specific:
        # Replace all LF with <LF> and all whitespaces with unbreakable spaces
        # text = text.replace("\n", "<LF>").replace("  ", "\u00A0\u00A0").replace("\r", "")
        # text = text.replace("\n", "<lf />").replace("  ", "\u00A0\u00A0").replace("\r", "")
        # Encoding (Before translation)
        encode_map = {
            "\n": "<lf />",
            "  ":
            "\u00A0\u00A0",
            "\r": ""
        }
        for old, new in encode_map.items():
            text = text.replace(old, new)

        translated = translator.translate(
            text,
            src=self.lang_source.get('google'),
            dest=self.lang_target.get('google')
        ).text

        # Google specific:
        # Replace all LF with <LF> and all whitespaces with unbreakable spaces
        # translated = translated.replace("<LF>", "\n").replace("\u00A0\u00A0", "  ")
        # translated = translated.replace("<lf />", "\n").replace("LF /", "\n").replace("Lf /", "\n").replace("lf /", "\n").replace("br /", "\n").replace("\u00A0\u00A0", "  ")
        # Decoding (After translation)
        decode_map = {
            "<lf />": "\n",
            "LF /": "\n",
            "Lf /": "\n",
            "lf /": "\n",
            "br /": "\n",
            "\u00A0\u00A0": "  "
        }
        for old, new in decode_map.items():
            translated = translated.replace(old, new)

        # # BEGIN TESTING PURPOSE ONLY
        # self.logs.log(f"self.lang_target_type={repr(self.lang_target_type)}", c='DEBUG', force=True)
        # self.logs.log(f"{repr(translated)}", c='ASK', force=True)
        # self.logs.log(f"{translated}", c='ASK', force=True)
        # input("Press enter to continue...")
        # sys_exit(0)
        # # END TESTING PURPOSE ONLY

        # Return translated text by Google
        return translated


    def deepl_translate(self, text, translator, translator_args):
        """
        Translator using Deepl.
        """
        # # BEGIN TESTING PURPOSE ONLY
        # text = "Вы выжили!\n\nВсе найденные в этом рейде предметы будут проданы скупщику.\n\n\n\n\n\nНайдено хабара на:                руб."
        # text = "В этой демо-версии вы познакомитесь с Рейдами -\n" + \
        #        "бесконечным игровым режимом с прогрессией и процедурной генерацией уровней (доступно только Убежище).\n" + \
        #        "Присоединяйтесь к Discord, чтобы поделиться фидбэком, сообщить об ошибках и просто быть в курсе всех событий.\n" + \
        #        "А также не забудьте добавить игру в свой список желаемого!"
        # text = "Схватить                       Схватить"
        # text = "Онлайн рейтинги\n- Страховка снаряжения\n- Химический источник света\n- Шприц с адреналином\n- Патроны теперь можно перекладывать из одного \nмагазина в другой, зажав триггер, по аналогии с \nкоробкой патронов.\r\n- При продаже предметов торговцу, на экране \nкомпьютера теперь высвечивается их название и \nстоимость.\r\n- На часы добавлена полоска ХП."
        # text = "Отлично, все готово! \n\nПомните, что вы можете изменить эти параметры\nи настроить их более детально в любое время,\nвыбрав \"Управление\" в Меню."
        # text = "штук.\nСовместимость: АКМ.\nЗажмите триггер для\nиспользования"
        # text = "Сразитесь с новыми противниками \n- волками и используйте новые \nмеханики, такие как разделка."
        # text = "Исследуйте новую обширную \nоткрытую локацию - Лес, \nполную секретов."
        # text = "Отпустите рюкзак\r\nи он автоматически\r\nвернется на место"
        # text = "БЕССМЕРТИЕ\n\n\n\nДОБАВИТЬ 10000 РУБ.\n\n\n\nВЫПОЛНИТЬ ТЕКУЩЕЕ ЗАДАНИЕ\n\n\n\nМАКСИМАЛЬНАЯ РЕПУТАЦИЯ\n\n\n\nОБНУЛИТЬ СОХРАНЕНИЕ"
        # text = "Требуется\nреп. 5"
        # # END TESTING PURPOSE ONLY

        # # BEGIN TESTING PURPOSE ONLY
        # self.logs.log(f"{text}", c='ASK', force=True)
        # # END TESTING PURPOSE ONLY

        # # DeepL specific:
        # # Replace all LF and WhiteSpace characters with xml tag (Produces translation errors)
        # text = text.replace("\n", "<w><x>LF</x></w> ").replace(" ", "<w><x>WS</x></w> ")

        # Replace all LF and double WhiteSpace characters with xml tag
        # text = text.replace("\n ", " __L1__ ").replace(" \n", " __L2__ ").replace("\r ", " __C1__ ").replace(" \r", " __C2__ ").replace("  ", "__W__ ")
        # text = text.replace("  ", " __WS__ ").replace("\n", " __LF__ ").replace("\r", "")
        # text = text.replace("  ", " __WS__ ").replace("\n", "<LF>").replace("\r", "")
        
        # # Replace all double whitespaces with __LF__ placeholders + Remove all CR to have only LF characters
        # text = text.replace("  ", " __WS__ ").replace("\r", "")
        # # Exception for text with enumerated list
        # if text.count('\n- ') > 1:
        #     text = text.replace("\n", "<w><x>LF</x></w> ")

        # text = text.replace("\r", "").replace("\n", "<w><x>LF</x></w>").replace("  ", " __WS__ ")
        # text = text.replace("\r", "").replace("\n", "<lf />").replace("  ", " <ws /> ")
        # Encoding (Before translation)
        encode_map = {
            "\r": "",
            "\n": "<lf />",
            "  ": "<ws />"
        }
        for old, new in encode_map.items():
            text = text.replace(old, new)

        # # BEGIN TESTING PURPOSE ONLY
        # self.logs.log(f"self.lang_source.get('deepl'): {self.lang_source['deepl']}", c='ASK', force=True)
        # self.logs.log(f"self.lang_target.get('deepl'): {self.lang_target['deepl']}", c='ASK', force=True)
        # self.logs.log(f"self.glossary.get('deepl'): {self.glossary.get('deepl')}", c='ASK', force=True)
        # input("Press enter to continue...")
        # sys_exit(0)
        # # END TESTING PURPOSE ONLY

        # /!\ language source is forced on 'auto' ('source_lang' argument is commented)
        # 'glossary' argument cannot be used when 'source_lang' argument is commented
        # Usefull When multiple lang sources
        if self.lang_source_type in ['auto']:
            translated = translator.translate_text(
                text,
                target_lang=self.lang_target.get('deepl'),
                model_type=translator_args.get('model_type'),
                formality=translator_args.get('formality'),
                split_sentences=translator_args.get('split_sentences'),
                preserve_formatting=translator_args.get('preserve_formatting'),
                context=translator_args.get('context')
            ).text
        else:
            translated = translator.translate_text(
                text,
                source_lang=self.lang_source.get('deepl'),
                target_lang=self.lang_target.get('deepl'),
                model_type=translator_args.get('model_type'),
                formality=translator_args.get('formality'),
                split_sentences=translator_args.get('split_sentences'),
                preserve_formatting=translator_args.get('preserve_formatting'),
                context=translator_args.get('context'),
                glossary=self.glossary.get('deepl')
            ).text

        # # BEGIN TESTING PURPOSE ONLY
        # self.logs.log(f"{translated}", c='ASK', force=True)
        # # END TESTING PURPOSE ONLY

        # # BEGIN TESTING PURPOSE ONLY
        # translated = "Cette démo te présente les Raids, un mode de jeu sans fin avec progression et niveaux générés de manière procédurale (seul Sanctuaire est disponible). Rejoins Discord pour partager tes commentaires, signaler les bugs et simplement te tenir au courant. N'oublie pas non plus d'ajouter le jeu à ta liste de souhaits !"
        # # END TESTING PURPOSE ONLY

        # # DeepL specific:
        # # Restore all LF and WhiteSpace characters (Produces translation errors)
        # translated = translated.replace("<w><x>LF</x></w> ", "\n").replace("<w><x>WS</x></w> ", " ")

        # # Restore all LF characters and double WhiteSpace characters
        # translated = translated.replace("<w><x>LF</x></w> ", "\n").replace("<w><x>WS</x></w> ", "  ")
        # # Restore all residual LF characters and double WhiteSpace characters
        # translated = translated.replace(" __L1__ ", "\n ").replace(" __L2__ ", " \n").replace(" __C1__ ", "\r ").replace(" __C2__ ", " \r").replace("__W__ ", "  ")
        # translated = translated.replace("<br>", "\n")

        # translated = translated.replace(" __LF__ ", "\n").replace("__LF__", "\n").replace("__lf__", "\n").replace("\n ", "\n").replace(" \n.", ".").replace(" .", ".").replace(" :", ":")
        # translated = translated.replace("<LF>", "\n").replace("\n.", ".").replace(" :", ":")
        # translated = translated.replace(" __WS__ ", "  ").replace("__WS__", "  ").replace("__ws__", "  ")

        # translated = translated.replace("<w><x>LF</x></w>", "\n").replace(" __WS__ ", "  ").replace("__WS__", "  ").replace("__ws__", "  ")
        # translated = translated.replace("<lf />", "\n").replace("lf /", "\n").replace("br /", "\n").replace(" <ws /> ", "  ").replace("<ws />", "  ")
        # Decoding (After translation)
        decode_map = {
            "<lf />": "\n",
            "lf /": "\n",
            "br /": "\n",
            "<ws />": "  ",
            " <ws /> ": "  "
        }
        for old, new in decode_map.items():
            translated = translated.replace(old, new)

        # # BEGIN TESTING PURPOSE ONLY
        # self.logs.log(f"{translated}\n", c='ASK', force=True)
        # # END TESTING PURPOSE ONLY

        # # BEGIN Inject '\n' from text to translated (Produces translation errors)
        # if '<w><x>LF</x></w>' in translated:
        #     # print("'<w><x>LF</x></w>' FOUND")
        #     translated = translated.replace("<w><x>LF</x></w> ", "\n").replace("<w><x>LF</x></w>", "\n").replace("<LF >", "\n").replace("< LF>", "\n")
        # elif '\n' in text:
        #     # print("'<w><x>LF</x></w>' NOT FOUND")
        #     translated = self.inject_line_breaks(text, translated)
        #     # translated = self.inject_line_breaks_dot_priority(text, translated)
        #     # translated = self.inject_line_breaks_dot_priority_2(text, translated)
        # # END Inject '\n' from text to translated (Produces translation errors)

        # # # BEGIN TESTING PURPOSE ONLY
        # self.logs.log(f"self.lang_source_type={repr(self.lang_source_type)}", c='DEBUG', force=True)
        # self.logs.log(f"{repr(translated)}", c='ASK', force=True)
        # self.logs.log(f"{translated}", c='ASK', force=True)
        # input("Press enter to continue...")
        # sys_exit(0)
        # # # END TESTING PURPOSE ONLY

        # Return translated text by DeepL
        return translated


    def translate(self, translator, text):
        """
        Dynamically calls the translation method based on self.name.
        """
        # Build the method name dynamically
        method_name = f"{translator.get('translator_name')}_translate"
        # Dynamically retrieve the corresponding method
        translate_method = getattr(self, method_name, None)
        
        # Call the retrieved method
        try:
            return translate_method(
                text=text,
                translator=translator.get('translator'),
                translator_args=translator.get('translator_args')
            )
        except Exception as e:
            try:
                self.logs.log(f" [WARN] First translation error with {translator.get('translator_name')}. New attemp in 1s.", c='WARN')
                sleep(1)
                return translate_method(text)
            except Exception as e:
                try:
                    self.logs.log(f" [WARN] Second translation error with {translator.get('translator_name')}. New attemp in 1s.", c='WARN')
                    sleep(1)
                    return translate_method(text)
                except Exception as e:
                    error_msg = f" [ERROR] Third Translation error with {translator.get('translator_name')}. No more attempt. {type(e).__name__}: {e}"
                    self.logs.log(error_msg, c='FAIL')
                    raise RuntimeError(error_msg)
