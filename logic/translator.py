import deepl
import googletrans
from time import sleep
from sys import exit as sys_exit
# import re  # inject_line_breaks_dot_priority_2

class Translator:

    def __init__(self, logs, params_game, translator_name, translator_api_key, language_support):
        # Get logs object instance
        self.logs = logs
        # Get params_game
        self.params_game = params_game

        # Initialize translator
        self.translator_name = translator_name        
        self.translator_api_key = translator_api_key
        self.translator_args = self.params_game.get('translator').get(self.translator_name)

        # Get language support
        self.language_support = language_support
        
        # Initialize lang source and target
        self.lang_source = 'unknown'
        self.lang_target = 'unknown'

        try:
            if self.translator_name == 'google':
                self.translator = googletrans.Translator()
            elif self.translator_name in 'deepl':
                self.translator = deepl.Translator(self.translator_api_key)
            else:
                # Raise an error if the method does not exist
                raise ValueError(f"Translate method '{self.translator_name}' is not supported.")

        except Exception as e:
            raise RuntimeError(f"Translation initialization error: {type(e).__name__}: {e}")
        pass


    def set_langs(self, lang_source, lang_target):
        """
        Set source and target langs accordingly to supported languages.
        """
        self.lang_source = self.language_support.get_source_language_name_by_translator(
            lang_source,
            self.translator_name
        )
        self.lang_target = self.language_support.get_target_language_name_by_translator(
            lang_target,
            self.translator_name
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


    def google_translate(self, text):
        """
        Translate using Google Translate.
        """
        # text = "Схватить                       Схватить"
        # text = "Исследуйте новую обширную \nоткрытую локацию - Лес, \nполную секретов."
        # text = "Сразитесь с новыми противниками \n- волками и используйте новые \nмеханики, такие как разделка."
        # text = "Схватить                       Схватить"
        text = "Онлайн рейтинги\n- Страховка снаряжения\n- Химический источник света\n- Шприц с адреналином\n- Патроны теперь можно перекладывать из одного \nмагазина в другой, зажав триггер, по аналогии с \nкоробкой патронов.\r\n- При продаже предметов торговцу, на экране \nкомпьютера теперь высвечивается их название и \nстоимость.\r\n- На часы добавлена полоска ХП."

        # # BEGIN TESTING PURPOSE ONLY
        # self.logs.log(f"{text}", c='ASK', force=True)
        # # END TESTING PURPOSE ONLY

        # Google specific:
        # Replace all LF with <LF> and all whitespaces with unbreakable spaces
        text = text.replace("\n", "<LF>").replace("  ", "\u00A0\u00A0").replace("\r", "")

        translated = self.translator.translate(
            text,
            src=self.lang_source,
            dest=self.lang_target
        ).text

        # Google specific:
        # Replace all LF with <LF> and all whitespaces with unbreakable spaces
        translated = translated.replace("<LF>", "\n").replace("\u00A0\u00A0", "  ")

        # # BEGIN TESTING PURPOSE ONLY
        # self.logs.log(f"{repr(translated)}", c='ASK', force=True)
        # self.logs.log(f"{translated}", c='ASK', force=True)
        # input("Press enter to continue...")
        # sys_exit(0)
        # # END TESTING PURPOSE ONLY

        # Return translated text by Google
        return translated


    def deepl_translate(self, text):
        """
        Translator using Deepl.
        """
        # # BEGIN TESTING PURPOSE ONLY
        # text = "Схватить                       Схватить"
        # text = "В этой демо-версии вы познакомитесь с Рейдами -\n" + \
        #        "бесконечным игровым режимом с прогрессией и процедурной генерацией уровней (доступно только Убежище).\n" + \
        #        "Присоединяйтесь к Discord, чтобы поделиться фидбэком, сообщить об ошибках и просто быть в курсе всех событий.\n" + \
        #        "А также не забудьте добавить игру в свой список желаемого!"
        # text = "Исследуйте новую обширную \nоткрытую локацию - Лес, \nполную секретов."
        # text = "Сразитесь с новыми противниками \n- волками и используйте новые \nмеханики, такие как разделка."
        # text = "Схватить                       Схватить"
        # text = "Онлайн рейтинги\n- Страховка снаряжения\n- Химический источник света\n- Шприц с адреналином\n- Патроны теперь можно перекладывать из одного \nмагазина в другой, зажав триггер, по аналогии с \nкоробкой патронов.\r\n- При продаже предметов торговцу, на экране \nкомпьютера теперь высвечивается их название и \nстоимость.\r\n- На часы добавлена полоска ХП."
        # # END TESTING PURPOSE ONLY

        # # BEGIN TESTING PURPOSE ONLY
        # self.logs.log(f"{text}", c='ASK', force=True)
        # # END TESTING PURPOSE ONLY

        # # DeepL specific:
        # # Replace all LF and WhiteSpace characters with xml tag (Produces translation errors)
        # text = text.replace("\n", "<w><x>LF</x></w> ").replace(" ", "<w><x>WS</x></w> ")

        # Replace all LF and double WhiteSpace characters with xml tag
        # text = text.replace("  ", "<w><x>WS</x></w> ").replace("\n", "<w><x>LF</x></w> ")
        # text = text.replace("\n ", " __L1__ ").replace(" \n", " __L2__ ").replace("\r ", " __C1__ ").replace(" \r", " __C2__ ").replace("  ", "__W__ ")
        # text = text.replace("\n", "<br>")
        
        # Replace all double whitespaces with __LF__ placeholders + Remove all CR to have only LF characters
        text = text.replace("  ", " __WS__ ").replace("\r", "")
        # Exception for text with enumerated list
        if text.count('\n- ') > 1:
            text = text.replace("\n", "<w><x>LF</x></w> ")

        # # BEGIN TESTING PURPOSE ONLY
        # self.logs.log(f"{repr(text)}", c='ASK', force=True)
        # # END TESTING PURPOSE ONLY

        translated = self.translator.translate_text(
            text,
            source_lang=self.lang_source,
            # target_lang=self.lang_target,
            target_lang='zh-hans',
            model_type=self.translator_args.get('model_type'),
            formality=self.translator_args.get('formality'),
            split_sentences=self.translator_args.get('split_sentences'),
            preserve_formatting=self.translator_args.get('preserve_formatting'),
            context=self.translator_args.get('context'),
            tag_handling=self.translator_args.get('tag_handling'),
            ignore_tags=self.translator_args.get('ignore_tags'),
            non_splitting_tags=self.translator_args.get('non_splitting_tags'),
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
        # translated = translated.replace("<w><x>LF</x></w>", "\n").replace("<w><x>WS</x></w>", "  ")
        # translated = translated.replace(" __L1__ ", "\n ").replace(" __L2__ ", " \n").replace(" __C1__ ", "\r ").replace(" __C2__ ", " \r").replace("__W__ ", "  ")
        # translated = translated.replace("<br>", "\n")
        translated = translated.replace(" __WS__ ", "  ").replace("__WS__", "  ")

        # # BEGIN TESTING PURPOSE ONLY
        # self.logs.log(f"{translated}\n", c='ASK', force=True)
        # # END TESTING PURPOSE ONLY

        # BEGIN Inject '\n' from text to translated (Produces translation errors)
        if '<w><x>LF</x></w>' in translated:
            # print("'<w><x>LF</x></w>' FOUND")
            translated = translated.replace("<w><x>LF</x></w> ", "\n").replace("<w><x>LF</x></w>", "\n")
        elif '\n' in text:
            # print("'<w><x>LF</x></w>' NOT FOUND")
            translated = self.inject_line_breaks(text, translated)
            # translated = self.inject_line_breaks_dot_priority(text, translated)
            # translated = self.inject_line_breaks_dot_priority_2(text, translated)
        # END Inject '\n' from text to translated (Produces translation errors)

        # # BEGIN TESTING PURPOSE ONLY
        # self.logs.log(f"{repr(translated)}", c='ASK', force=True)
        # self.logs.log(f"{translated}", c='ASK', force=True)
        # input("Press enter to continue...")
        # sys_exit(0)
        # # END TESTING PURPOSE ONLY

        # Return translated text by DeepL
        return translated


    def translate(self, text):
        """
        Dynamically calls the translation method based on self.name.
        """
        # Build the method name dynamically
        method_name = f"{self.translator_name}_translate"
        # Dynamically retrieve the corresponding method
        translate_method = getattr(self, method_name, None)
        
        # Call the retrieved method
        try:
            return translate_method(text)
        except Exception as e:
            try:
                self.logs.log(f"Translation error with {self.translator_name}. New attemp in 1s.", c='WARN')
                sleep(1)
                return translate_method(text)
            except Exception as e:
                try:
                    self.logs.log(f"Translation error with {self.translator_name}. New attemp in 1s.", c='WARN')
                    sleep(1)
                    return translate_method(text)
                except Exception as e:
                    self.logs.log(f"Translation error: {type(e).__name__}: {e}", c='FAIL')
                    return text
