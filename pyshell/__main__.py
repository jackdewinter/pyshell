"""
Module to provide for "-m pymarkdown" access to the module,
as if it was run from the console.
"""

from pyshell.main import PyShell


def main() -> None:
    """
    Main entry point.  Exposed in this manner so that the setup
    entry_points configuration has something to execute.
    """
    PyShell().main()


if __name__ == "__main__":
    main()
