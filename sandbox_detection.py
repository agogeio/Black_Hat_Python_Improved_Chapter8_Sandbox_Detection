import datetime
import platform
import subprocess
import threading
import time

from pynput import keyboard 


#? This is a sendbox detection script that is focused on evading Joe Sandbox 
#? https://www.joesandbox.com/#windows
#? It looks as if the sandbox will only run for 500 seconds (8 min and 20 seconds)
#? We will focus on evading detecion on Windows systems 

SLEEP_TIMER = 520

SRV_MONTH_THRESHOLD = 1
SRV_DAY_THRESHOLD = 5
SRV_HOUR_THRESHOLD = 0
SRV_MIN_THRESHOLD = 0

WORKSTATION_MONTH_THRESHOLD = 0
WORKSTATION_DAY_THRESHOLD = 0
WORKSTATION_HOUR_THRESHOLD = 8
WORKSTATION_MIN_THRESHOLD = 0

WORKSTATION_KEY_COUNT = 50
SERVER_KEY_COUNT = 10

MEASURE_TIME = 5 * 60



#? Objectives:
#? 1. Sleep beyond the sandbox time out feature
#? 2. Check for the OS version:
#?  Desktops should have more key strokes 
#?  Servers we be expected to have fewer 
#? Get the uptime for the system, the longer the uptime the less likely it's a sandbox

class SBD:
    def __init__(self) -> None:
        self.os_version = ''
        self.uptime = ''
        self.key_count = 0


    def get_os(self):
        os_platform = platform.system()

        if os_platform == 'Windows':
            result = subprocess.run('systeminfo', capture_output=True, text=True, universal_newlines=True)
            # print(f'Result: {result.stdout}')
            if 'Microsoft Windows Server' in result.stdout:
                # print('The OS is likely Windows Server')
                return 'Windows Server'
            else:
                # print('The OS is likely a Windows workstation')
                return 'Windows Workstation'


    def get_boot_diff(self):
        result = subprocess.run('systeminfo', capture_output=True, text=True, universal_newlines=True)
        #* https://www.windows-commandline.com/find-windows-os-version-from-command/
        #? systeminfo | findstr /B /C:"OS Name" /C:"OS Version"

        search_term = "System Boot Time:"
        # Split the text into a list of lines
        lines = result.stdout.split("\n")
        for line in lines:
            if search_term in line:
                system_boot = line.split('          ')[1]
                # print(system_boot)

                system_boot_date = system_boot.split(',')[0]
                system_boot_hr_min_sec = system_boot.split(',')[1]
                system_boot_hr_min_sec = system_boot_hr_min_sec.strip()
                system_boot_hr_min = system_boot_hr_min_sec.split(' ')[0]

                system_boot_month = system_boot_date.split('/')[0]
                system_boot_day = system_boot_date.split('/')[1]
                system_boot_year = system_boot_date.split('/')[2]
                system_boot_hour = system_boot_hr_min.split(':')[0]
                system_boot_min = system_boot_hr_min.split(':')[1]
                system_boot_ampm = system_boot_hr_min_sec.split(' ')[1]

                if system_boot_ampm == 'PM':
                    system_boot_hour = int(system_boot_hour) + 12

                current_date = datetime.datetime.now()
                current_date = current_date.strftime('%m/%d/%Y %H:%M %p')

                current_date_month = current_date.split('/')[0]
                # print(current_date_month)
                current_date_day = current_date.split('/')[1]
                # print(current_date_day)
                current_date_year = (current_date.split('/')[2]).split(' ')[0]
                # print(current_date_year)
                current_date_time, current_ampm = (current_date.split('/')[2]).split(' ')[1:]
                current_date_hour = current_date_time.split(':')[0]
                current_date_min = current_date_time.split(':')[1]

                if current_ampm == 'PM':
                    current_date_hour = int(current_date_hour) + 12

                year_diff = int(system_boot_year) - int(current_date_year)
                month_diff = int(system_boot_month) - int(current_date_month)
                day_diff = int(system_boot_day) - int(current_date_day)
                hour_diff = int(system_boot_hour) - int(current_date_hour)
                min_diff = int(system_boot_min) - int(current_date_min)

                # print(f'Boot diff: {year_diff} {month_diff} {abs(day_diff)} {abs(hour_diff)} {abs(min_diff)}')

                diff = {
                    'year': abs(year_diff),
                    'month': abs(month_diff),
                    'day': abs(day_diff),
                    'hour': abs(hour_diff),
                    'min': abs(min_diff)
                }

                return diff


    def on_press(self, key):
        self.key_count += 1


    def count_keys(self):
        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()


    def get_key_count(self):
        return self.key_count

    def hibernate(self, timer):
        time.sleep(timer)


if __name__ == '__main__':
    sbd = SBD()
    # sbd.hibernate(SLEEP_TIMER)
    os = sbd.get_os()
    # print(os)
    diff = sbd.get_boot_diff()
    sbd.count_keys()

    while True:

        if os == "Windows Server":

            if diff['day'] >= SRV_DAY_THRESHOLD or \
                diff['month'] >= SRV_MONTH_THRESHOLD or \
                diff['hour'] >= SRV_HOUR_THRESHOLD:
                print('Server uptime pass')

                # print("Windows Server")
                if WORKSTATION_KEY_COUNT < sbd.get_key_count():
                    print('Workstation key count hit')
                else:
                    # Key count not hit
                    pass

        elif os == "Windows Workstation":

            if diff['day'] >= WORKSTATION_DAY_THRESHOLD or diff['hour'] >= WORKSTATION_HOUR_THRESHOLD:
                print('Workstation uptime pass')

                # print("Windows Workstation")
                if WORKSTATION_KEY_COUNT < sbd.get_key_count():
                    print('Workstation key count hit')
                else:
                    # Key count not hit
                    pass
        
        else:
            print('Likely Linux or MacOS')

        time.sleep(SLEEP_TIMER)
