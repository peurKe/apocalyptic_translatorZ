import os
import sys
import re
from datetime import datetime
import subprocess
from time import sleep as time_sleep, time as time_time
import pygetwindow as gw

class Steam:

    def __init__(self, logs, game_exec, steam_game_params):
        # Get logs object instance
        self.logs = logs        
        self.game_exec = game_exec
        # Steam game params
        self.game_name = steam_game_params.get('name')
        self.log_path = steam_game_params.get('log_path')
        self.app_id = steam_game_params.get('app_id')
        self.manifest_acf_file = steam_game_params.get('manifest_acf_file')
        self.buildid = 'no_builid'
        self.start_timestamp = None
        
        if self.app_id:
            if not os.path.exists(self.manifest_acf_file):
                self.logs.log(f" '{self.manifest_acf_file}' manifest game file not found.", c='FAIL')
                # self.logs.input(f" Press Enter to exit...")
                # Raise an error if the 'manifest' game file does not exist
                raise ValueError(f" '{self.manifest_acf_file}' manifest game file not found.")
            else:
                self.extract_buildid()
        else:
            self.logs.log(f" '{self.game_name}' is not a Steam game, it does not have APP ID or manifest game file.", c='WARN')


    def extract_buildid(self):
        with open(self.manifest_acf_file, 'r', encoding='utf-8') as file:
            content = file.read()
            # Regex to get field "buildid" value
            match = re.search(r'"buildid"\s+"(\d+)"', content)
            if match:
                buildid = match.group(1)
                self.buildid = buildid  # Get current buildid game
            else:
                self.logs.log(f" No valid build id found in '{self.manifest_acf_file}' manifest game file.", c='FAIL')
                # self.logs.input(f" Press Enter to exit...")
                # Raise an error if the 'manifest' game file does not exist
                raise ValueError(f" No valid build id found in '{self.manifest_acf_file}' manifest game file.")

        return self.buildid


    # Function to get the current timestamp in YYYY-MM-DD HH:MM:SS format
    def get_current_timestamp(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


    def steam_update_game_files(self):
        """
        Run update files for a Steam game's files using its app ID.
        """
        # App ID is not Steam game (see 'DEFAULT_ZONA_GAME_ID' variables)
        if not self.app_id:
            self.logs.log(f" • [Cannot validates the integrity of '{self.game_name}' because it is not a Steam Game.] Failed", c='FAIL', force=True)
            self.logs.log(f" Tips: Execute the 'auto_ZONA_translator (restore)' shortcut located in your '{self.game_name}' game folder.", c='INFO', force=True)
            self.logs.log(f"       Or reinstall (delete and download again) this '{self.game_name}' game.\n", c='INFO', force=True)
            self.logs.input(f" Press Enter to exit...\n", c='ASK')
            sys.exit(-1)
        else:
            self.logs.log(f" • [Validate '{self.game_name}' (app ID '{self.app_id}') files integrity from Steam console. Monitoring logs] ...", c='INFO', force=True)
            # Get the timestamp before starting the integrity check
            self.start_timestamp = self.get_current_timestamp()
            # Run the integrity check in the background
            process = self.verify_steam_game_integrity()
            
            # Periodically check the logs while the integrity check continues in the background
            while process.poll() is None:  # While the process is still running
                time_sleep(5)  # Wait for 5 seconds before checking the logs again
            
            # Once the verification is complete, check the logs for the "Fully Installed" status
            while not self.check_log_for_integrity_verification():
                time_sleep(5)  # Wait for 5 seconds before checking the logs again
            
            # Minimize all open Steam windows
            # Retrieve all open windows containing "Steam" in their title
            steam_windows = [window for window in gw.getAllWindows() if 'Steam' in window.title]
            # Minimize each Steam window
            for window in steam_windows:
                window.minimize()

            try:
                # Get the window for the current translator Python process
                current_window = gw.getWindowsWithTitle('')  # This will get the window that matches an empty title, i.e., the current script's window
                if current_window:
                    # Activate the current translator window
                    current_window[0].activate()
            except Exception as e:
                self.logs.log(f" • [No current translator Python process found] WARN", c='WARN', force=True)

            self.logs.log(f" • [Validate '{self.game_name}' (app ID '{self.app_id}') files integrity from Steam console. Monitoring logs] OK", c='OK', force=True)
            return True


    # Function to execute the Steam integrity check in the background
    def verify_steam_game_integrity(self):
        # command = f'{steam_path} -applaunch {self.app_id} validate'  # Command to launch the integrity check
        command = f"\"C:\\Program Files (x86)\\Steam\\steam.exe\" -silent steam://validate/{self.app_id}"  # Command to launch the integrity check
        
        # Run the command in the background
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process


    # Function to read the log file and check if the "Fully Installed" status is found
    def check_log_for_integrity_verification(self):
        # Regular expression pattern to find lines with the timestamp and "Fully Installed" status
        pattern = r'^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] AppID (\d+) state changed : Fully Installed,$'
        
        # Open the log file and read each line
        with open(self.log_path, 'r', encoding='utf-8') as file:
            for line in file:
                # Search for matching lines using the pattern
                match = re.match(pattern, line.strip())
                if match:
                    timestamp_str = match.group(1)  # Extract timestamp from the line
                    app_id_found = match.group(2)  # Extract AppID (optional if needed)
                    
                    # Convert the timestamp from the log to a datetime object for comparison
                    log_timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    last_check_time = datetime.strptime(self.start_timestamp, '%Y-%m-%d %H:%M:%S')
                    
                    # print(f"if ({app_id_found} == {self.app_id}) and ({log_timestamp} > {last_check_time}) ?")
                    # Check if self.app_id is le good one AND the log timestamp is later than the timestamp of the integrity check
                    if (str(app_id_found) == str(self.app_id)) and (log_timestamp > last_check_time):
                        return True
        return False


    def get_game_exec(self):
        return self.game_exec


    def get_manifest_acf_file(self):
        return self.manifest_acf_file


    def get_buildid(self):
        return self.buildid
