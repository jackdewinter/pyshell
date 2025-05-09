"""Data source for properties belonging to the Git VCS.
"""

from typing import List

from pyshell.data_sources.base_data_source import (
    BaseDataSource,
    PropertyDependency,
    PropertyPath,
    property_resolver,
)
from pyshell.file_path_helpers import FilePathHelpers


class GitDataSource(BaseDataSource):
    """Data source for git properties."""

    def __init__(self) -> None:
        dynamic_dependencies_to_inject: List[PropertyDependency] = [
            PropertyDependency(
                "git.root_directory", PropertyPath.from_one("project.root_directory")
            )
        ]
        super().__init__(
            name="git", dependencies_to_inject=dynamic_dependencies_to_inject
        )

    @property_resolver("branch")
    def __get_branch_name(self) -> str:
        """TBD"""
        if not (
            subcommand_response := self._execute_subprocess(
                ["git", "branch", "--no-color"], check_for_success=False
            )
        ).returncode:
            for i in subcommand_response.stdout.split("\n"):  # pragma: no cover
                if i.startswith("* "):  # pragma: no cover
                    return i[2:]
        return ""

    @property_resolver("root_directory")
    def __get_root_directory(self) -> str:
        """TBD"""
        if not (
            subcommand_response := self._execute_subprocess(
                ["git", "rev-parse", "--show-toplevel"], check_for_success=False
            )
        ).returncode:
            return FilePathHelpers.normalize_path(subcommand_response.stdout[:-1])
        return ""

    # remote project name
    # git config --local remote.origin.url|sed -n 's#.*/\([^.]*\)\.git#\1#p'
    # git remote -v | head -n1 | awk '{print $2}' | sed -e 's,.*:\(.*/\)\?,,' -e 's/\.git$//'
