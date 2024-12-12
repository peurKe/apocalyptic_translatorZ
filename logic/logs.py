import re
from colorama import Fore, Style

class Logs :

    colors = dict(
        INFO=Fore.LIGHTYELLOW_EX,
        DEBUG=Fore.MAGENTA,
        OK=Fore.GREEN,
        WARN=Fore.RED,
        FAIL=Fore.LIGHTRED_EX,
        ASK=Fore.CYAN,
        NOTIF=Fore.LIGHTGREEN_EX
    )


    def __init__(self, params_game, verbose=False):
        # Get verbose
        self.verbose = verbose
        # Get params_game
        self.params_game = params_game
        # Set log file
        self.log_file = self.params_game.get('log_file')


    def log(self, msg, c='INFO', end='\n', force=False):
        if self.verbose or force:
            if not c:
                print(msg, end=end)
            else:
                print(f"{self.colors[c]}{msg}{Style.RESET_ALL}", end=end)

        # Remove ANSI escape characters for colored string
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
        msg = ansi_escape.sub('', msg)

        # Open the log file in 'append' mode and write msg
        with open(self.log_file, 'a', encoding="utf-8") as f:
            f.write(f"{msg}\n")


    def input(self, prompt, c='ASK'):
        if not c:
            res = input(prompt)
        else:
            res = input(f"{self.colors[c]}{prompt}{Style.RESET_ALL}")
        return res
