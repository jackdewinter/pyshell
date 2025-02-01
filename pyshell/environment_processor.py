

import os


class EnvironmentProcessor:

    __TO_REMOVE = ["LOCALAPPDATA", "PSModulePath", "PROCESSOR_ARCHITECTURE", "CommonProgramW6432", "CommonProgramFiles(x86)", "ProgramFiles(x86)",
                   "PROCESSOR_LEVEL", "ALLUSERSPROFILE", "DriverData", "APPDATA", "OneDrive", "CommonProgramFiles", "OS", "USERDOMAIN_ROAMINGPROFILE",
                   "PROCESSOR_IDENTIFIER", "OneDriveConsumer", "ProgramFiles", "ProgramData", "ProgramW6432", "windir", "PROCESSOR_REVISION", "PUBLIC",
                   "PROMPT"]

    def __init__(self):
        env_dict = {}
        for xx in os.environ:
            xy = os.environ[xx]
            env_dict[xx] = xy

        if "ComSpec" in env_dict:
            del env_dict["ComSpec"]

        for i in EnvironmentProcessor.__TO_REMOVE:
            if i in env_dict:
                del env_dict[i]


# COMPUTERNAME=DISCOVERY
# USERPROFILE=C:\Users\jack
# HOMEPATH=\Users\jack
# TERM=xterm-256color
# LOGONSERVER=\\DISCOVERY
# PATHEXT=.COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC
# HOMEDRIVE=C:
# SystemRoot=C:\Windows
# Path=C:\Windows\system32;C:\Windows;C:\Windows\System32\Wbem;C:\Windows\System32\WindowsPowerShell\v1.0\;C:\Windows\System32\OpenSSH\;C:\Users\jack\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.8_qbz5n2kfra8p0\LocalCache\local-packages\Python38\Scripts;C:\Users\jack\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.8_qbz5n2kfra8p0\LocalCache\local-packages\Python38\site-packages;c:\enlistments\batch;C:\Program Files\dotnet\;C:\Program Files\Git\cmd;C:\Users\jack\AppData\Local\Microsoft\WindowsApps;C:\Users\jack\AppData\Local\Programs\Microsoft VS Code\bin;C:\enlistments\batch;C:\Users\jack\spicetify-cli
# USERNAME=jack
# TERM_PROGRAM_VERSION=0.7.7.0
# USERDOMAIN=DISCOVERY
# SystemDrive=C:
# TEMP=C:\Users\jack\AppData\Local\Temp
# NUMBER_OF_PROCESSORS=16
# TMP=C:\Users\jack\AppData\Local\Temp

