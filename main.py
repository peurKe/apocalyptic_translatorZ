import os
import sys
import argparse
import re
import traceback
from pathlib import Path
from apocalyptic_translatorZ.logic.apocalyptic_translatorZ import apocalyptic_translatorZ
from colorama import init as colorama_init, Fore, Style

def main():

    # Initialize Colorama for cross-platform color support
    colorama_init(autoreset=True)
        
    try:
        # Get script arguments
        argparser = argparse.ArgumentParser()
        argparser.add_argument("-t", "--translators", type=str, default='deepl,google', choices=['deepl,google', 'google,deepl', 'deepl', 'google'], help="List of translators in order of preference to be used for translating. (default value: 'deepl,google')")
        argparser.add_argument("-ta", "--auth-key", type=str, default='', help="Your Translator API authentivation key. (default value: '')")
        argparser.add_argument("-ls", "--lang-sources", type=str, default='ru', help="List of language to translate from. if more than one language then '--lang-sources' parameter must be comma separated (eg. 'ru,uk'). (default value: 'ru').")
        argparser.add_argument("-l", "--lang-targets", type=str, default='en', help="List of languages to translate to. if more than one language then '--lang-targets' parameter must be comma separated (eg. 'fr,cs'). (default value: 'en')")
        argparser.add_argument("-r", "--restore", action='store_true', help="Restore backup files (reset)")
        argparser.add_argument("-f", "--files", type=str, default='', help="Comma separated str. Default is with all 'levelN' and '.assets' files. if '--files' is specified then '--files' parameter must be comma separated (eg. 'level7,level11')")
        argparser.add_argument("-s", "--min-size", type=int, default=2, help="Minimum size for string to translate is set to 2")
        argparser.add_argument("-v", "--verbose", action='store_true', help="Execute verbose mode (show translation results")
        argparser.add_argument("-w", "--wait-on-success", action='store_true', help="Allow to wait input when script succeed.")
        # argparser.add_argument("-c", "--check-translations", action='store_true', help="Allow to check all translations.")
        argparser.add_argument("--force", action='store_true', help=f"Force translate even if translated files are already existing in game directory")
        argparser.add_argument("-g", "--game_dir", type=str, default=None, help="Game directory (CLI execution)")
        args = argparser.parse_args()

        i_translators = re.sub(r'\s+', '', args.translators).lower().split(',')
        i_auth_key = args.auth_key
        i_lang_sources = re.sub(r'\s+', '', args.lang_sources).lower().split(',')
        i_lang_targets = re.sub(r'\s+', '', args.lang_targets).lower().split(',')
        i_restore = args.restore
        i_files = re.sub(r'\s+', '', args.files).split(',')
        i_min_size = args.min_size
        i_verbose = args.verbose
        i_wait_on_success = args.wait_on_success
        # i_check_translations = args.check_translations
        i_force = args.force        
        # i_game_dir = "D:\\SteamLibrary\\steamapps\\common\\CONVRGENCE"
        i_game_dir = args.game_dir

        # Get the current directory
        if getattr(sys, 'frozen', False):
            print(f"{Fore.LIGHTYELLOW_EX} • [Running as an executable]")
            game_dir = Path(sys.executable).parent.resolve()
        else:
            print(f"{Fore.LIGHTYELLOW_EX} • [Running as a script]")
            game_dir = os.path.abspath(os.path.dirname(__file__))

        if i_game_dir:
            game_dir = i_game_dir

        print(f"{Fore.MAGENTA}   {game_dir}\n")
        os.chdir(game_dir)

        if i_files == ['']:
            i_files.pop()
        
        manager = apocalyptic_translatorZ(
            game_dir=game_dir,
            lang_sources=i_lang_sources,
            lang_targets=i_lang_targets,
            translators_preferred=i_translators,
            translator_api_key=i_auth_key,
            restore=i_restore,
            files=i_files,
            min_size=i_min_size,
            force=i_force,
            verbose=i_verbose
        )
        manager.run()
    
        if i_wait_on_success:
            input(f"{Fore.CYAN}Press enter to exit...")

    except Exception as e:
        error_msg = traceback.format_exc()  # Get full traceback for debugging
        print(f"{Fore.LIGHTRED_EX}{e}{Style.RESET_ALL}\n{Fore.RED}{error_msg}{Style.RESET_ALL}")
        input(f"{Fore.CYAN}Press enter to exit...{Style.RESET_ALL}")
        sys.exit(0)

if __name__ == "__main__":
    main()
