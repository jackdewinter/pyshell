"""Module to help deal with file paths in a common manner.
"""

import logging
import os
import subprocess  # nosec blacklist
from dataclasses import dataclass
from typing import List

# pylint: disable=too-few-public-methods

LOGGER = logging.getLogger(__name__)


class FilePathHelpers:
    """Class to help deal with file paths in a common manner."""

    @dataclass(frozen=True)
    class MountNamePathPair:
        """Provide for simple storage of the name of a mount and the local path associated with it."""

        mount_name: str
        mounth_path: str

    __MOUNTED_DIRECTORIES: List[MountNamePathPair] = []
    __MOUNT_RETURN_CODE = -1

    @staticmethod
    def normalize_path(incoming_path: str, change_to_posix: bool = False) -> str:
        """Provide a normalized form of an incoming path."""
        if (
            len(incoming_path) >= 2
            and incoming_path[0] == "~"
            and incoming_path[1] in ["/", "\\"]
        ):
            incoming_path = os.path.expanduser("~") + incoming_path[1:]
        absolute_path = os.path.abspath(incoming_path)
        if len(absolute_path) >= 2 and absolute_path[1] == ":":
            absolute_path = absolute_path[0].upper() + absolute_path[1:]

        if change_to_posix and os.name.lower() == "nt":
            if FilePathHelpers.__MOUNT_RETURN_CODE < 0:
                FilePathHelpers.__load_mount_points()
            if FilePathHelpers.__MOUNT_RETURN_CODE == 0:
                x1 = ""
                x2 = ""
                for xxx in FilePathHelpers.__MOUNTED_DIRECTORIES:
                    ff = xxx.mounth_path + "\\"
                    if absolute_path.startswith(ff) and len(ff) > len(x1):
                        x1 = ff
                        x2 = (
                            xxx.mount_name + "/"
                            if not xxx.mount_name.endswith("/")
                            else xxx.mount_name
                        )
                if x2:
                    absolute_path = x2 + absolute_path[len(x1) :].replace("\\", "/")

        return absolute_path

    @staticmethod
    def __load_mount_points() -> None:
        # $ df -a
        # Filesystem                        1K-blocks     Used Available Use% Mounted on
        # C:/Program Files/Git              997702652 88940028 908762624   9% /
        # C:/Program Files/Git/usr/bin              -        -         -    - /bin
        # C:/Users/jackd/AppData/Local/Temp         -        -         -    - /tmp
        # C:                                        -        -         -    - /c

        cp = subprocess.run(  # nosec start_process_with_partial_path
            ["df", "-a"],
            text=True,
            shell=True,  # nosec subprocess_popen_with_shell_equals_true
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        FilePathHelpers.__MOUNT_RETURN_CODE = cp.returncode
        if FilePathHelpers.__MOUNT_RETURN_CODE != 0:
            LOGGER.warning(
                "Unable to use 'df -a' to access mount information: %d",
                FilePathHelpers.__MOUNT_RETURN_CODE,
            )
            LOGGER.warning("STDOUT: %s", cp.stdout if cp.stdout else "")
            LOGGER.warning("STDERR: %s", cp.stderr if cp.stderr else "")
        else:
            ert = []
            fx = cp.stdout.split("\n")
            for file_path in fx:
                if not (
                    file_path
                    and (
                        (file_path[0] >= "a" and file_path[1] <= "z")
                        or (file_path[0] >= "A" and file_path[1] <= "Z")
                    )
                ):
                    continue
                fy = file_path.split(" ")
                fz = len(fy) - 1
                while not fy[fz].startswith("/"):
                    fz -= 1
                mount_prefix = " ".join(fy[fz:])
                fz -= 1
                assert fy[fz].endswith("%") or fy[fz] == "-"
                fz -= 1
                for _ in range(3):
                    while fy[fz] == "":
                        fz -= 1
                    fz -= 1
                while fy[fz] == "":
                    fz -= 1
                fff = " ".join(fy[0 : fz + 1])
                ert.append(
                    FilePathHelpers.MountNamePathPair(
                        mount_prefix, fff.replace("/", "\\")
                    )
                )
            FilePathHelpers.__MOUNTED_DIRECTORIES.extend(ert)


# pylint: enable=too-few-public-methods
