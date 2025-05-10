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
                best_mopunt_path = ""
                best_mount_name = ""
                for next_mount_name_path_pair in FilePathHelpers.__MOUNTED_DIRECTORIES:
                    adjusted_path = next_mount_name_path_pair.mounth_path + "\\"
                    if absolute_path.startswith(adjusted_path) and len(
                        adjusted_path
                    ) > len(best_mopunt_path):
                        best_mopunt_path = adjusted_path
                        best_mount_name = (
                            next_mount_name_path_pair.mount_name + "/"
                            if not next_mount_name_path_pair.mount_name.endswith("/")
                            else next_mount_name_path_pair.mount_name
                        )
                if best_mount_name:
                    absolute_path = best_mount_name + absolute_path[
                        len(best_mopunt_path) :
                    ].replace("\\", "/")

        return absolute_path

    @staticmethod
    def clear_mount_points() -> None:
        """Clear the mount points. Note that this should only be used for testing and is not thread safe."""
        FilePathHelpers.__MOUNTED_DIRECTORIES.clear()
        FilePathHelpers.__MOUNT_RETURN_CODE = -1

    @staticmethod
    def __load_mount_points() -> None:
        # $ df -a
        # Filesystem                        1K-blocks     Used Available Use% Mounted on
        # C:/Program Files/Git              997702652 88940028 908762624   9% /
        # C:/Program Files/Git/usr/bin              -        -         -    - /bin
        # C:/Users/brmay/AppData/Local/Temp         -        -         -    - /tmp
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
            new_mount_list = []
            for split_line in cp.stdout.split("\n"):
                if not (
                    split_line
                    and (
                        (split_line[0] >= "a" and split_line[1] <= "z")
                        or (split_line[0] >= "A" and split_line[1] <= "Z")
                    )
                ):
                    continue
                line_split_by_spaces = split_line.split(" ")
                line_split_index = len(line_split_by_spaces) - 1
                while not line_split_by_spaces[line_split_index].startswith("/"):
                    line_split_index -= 1
                mount_prefix = " ".join(line_split_by_spaces[line_split_index:])
                line_split_index -= 1
                assert (
                    line_split_by_spaces[line_split_index].endswith("%")
                    or line_split_by_spaces[line_split_index] == "-"
                )
                line_split_index -= 1
                for _ in range(3):
                    while line_split_by_spaces[line_split_index] == "":
                        line_split_index -= 1
                    line_split_index -= 1
                while line_split_by_spaces[line_split_index] == "":
                    line_split_index -= 1
                new_mount_list.append(
                    FilePathHelpers.MountNamePathPair(
                        mount_prefix,
                        (
                            " ".join(line_split_by_spaces[0 : line_split_index + 1])
                        ).replace("/", "\\"),
                    )
                )
            FilePathHelpers.__MOUNTED_DIRECTORIES.extend(new_mount_list)


# pylint: enable=too-few-public-methods
