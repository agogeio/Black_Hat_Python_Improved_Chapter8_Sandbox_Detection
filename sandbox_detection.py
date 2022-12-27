import platform


#? This is a sendbox detection script that is focused on evading Joe Sandbox 
#? https://www.joesandbox.com/#windows
#? It looks as if the sandbox will only run for 500 seconds (8 min and 20 seconds)
#? We will focus on evading detecion on Windows systems 

SLEEP_TIMER = 520

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
        os_version = platform.system()

        return os_version


if __name__ == '__main__':
    sbd = SBD()