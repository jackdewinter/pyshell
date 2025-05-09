"""
Main module for the project
"""

import argparse
import logging
import os
import runpy
import sys
import traceback
from typing import Dict, List, Optional

from application_properties import ApplicationProperties, ApplicationPropertiesUtilities

from pyshell.application_configuration_helper import ApplicationConfigurationHelper
from pyshell.application_logging import ApplicationLogging
from pyshell.data_source_manager import DataSourceManager
from pyshell.line_item_manager import LineItemManager

LOGGER = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods, too-many-instance-attributes
class PyShell:
    """
    Main class.
    """

    def __init__(
        self,
        show_stack_trace: bool = False,
    ):
        self.__version_number = PyShell.__get_semantic_version()
        self.__properties: ApplicationProperties = ApplicationProperties()
        self.__show_stack_trace = show_stack_trace
        self.__logging = ApplicationLogging(
            self.__properties,
            default_log_level="CRITICAL",
            show_stack_trace=show_stack_trace,
        )

        self.__dsm = DataSourceManager()
        self.__lim = LineItemManager()
        self.__was_invoked_from_ps1 = os.environ.get("IS_PYSHELL_PS1", 0)
        self.__did_error_on_config_load = False

    @staticmethod
    def __get_semantic_version() -> str:
        file_path = __file__
        assert os.path.isabs(
            file_path
        ), "This should hold on all operating systems.  This is to be sure of that assumption."
        file_path = file_path.replace(os.sep, "/")
        last_index = file_path.rindex("/")
        file_path = f"{file_path[: last_index + 1]}version.py"
        version_meta = runpy.run_path(file_path)
        return str(version_meta["__version__"])

    def __parse_arguments(self, direct_args: Optional[List[str]]) -> argparse.Namespace:
        parser = argparse.ArgumentParser(description="Lint any found Markdown files.")

        ApplicationPropertiesUtilities.add_default_command_line_arguments(parser)
        parser.add_argument(
            "--stack-trace",
            dest="show_stack_trace",
            action="store_true",
            default=False,
            help="if an error occurs, print out the stack trace for debug purposes",
        )
        parser.add_argument(
            "-x-exception",
            dest="x_test_exception",
            action="store_true",
            default="",
            help=argparse.SUPPRESS,
        )
        ApplicationLogging.add_default_command_line_arguments(parser)

        subparsers = parser.add_subparsers(dest="primary_subparser")
        subparsers.add_parser("init", help="Initialize the...")
        subparsers.add_parser("run", help="Initialize the...")
        subparsers.add_parser("version", help="Version of the application.")

        parse_arguments = parser.parse_args(args=direct_args)
        if not parse_arguments.primary_subparser:
            parser.print_help()
            sys.exit(2)
        elif parse_arguments.primary_subparser == "version":
            print(f"{self.__version_number}")
            sys.exit(0)
        return parse_arguments

    def __set_initial_state(self, args: argparse.Namespace) -> None:
        self.__logging.pre_initialize_with_args(args)

        if args.primary_subparser != "init":
            self.__did_error_on_config_load = False
            ApplicationConfigurationHelper.apply_configuration_layers(
                args, self.__properties, self.__handle_error2
            )
            if self.__did_error_on_config_load and self.__was_invoked_from_ps1:
                needed_arguments = sys.argv[:]
                needed_arguments[0] = __file__
                needed_arguments.insert(0, sys.executable)
                print(
                    "An error occurred. To debug the error, run the command line:\n  "
                    + " ".join(needed_arguments)
                )
                self.__properties = ApplicationProperties()
                self.__properties.load_from_dict(
                    {"items": {"simple-prompt": {"type": "text", "text": "$ "}}}
                )
        else:
            LOGGER.info(
                "Configuration loaded and applied.  Initial state setup completed."
            )

    def __handle_error2(
        self,
        formatted_error: str,
        thrown_error: Optional[Exception],
        exit_on_error: bool = True,
        print_prefix: str = "\n\n",
    ) -> None:
        if self.__was_invoked_from_ps1:
            self.__did_error_on_config_load = True
        else:
            self.__handle_error(
                formatted_error, thrown_error, exit_on_error, print_prefix
            )

    # pylint: disable=broad-exception-raised
    def __initialize_subsystems(
        self, direct_args: Optional[List[str]]
    ) -> argparse.Namespace:

        args = self.__parse_arguments(direct_args=direct_args)
        self.__set_initial_state(args)

        self.__show_stack_trace = args.show_stack_trace
        if not self.__show_stack_trace and self.__properties:
            self.__show_stack_trace = self.__properties.get_boolean_property(
                "log.stack-trace"
            )

        self.__logging.initialize(args)
        LOGGER.info("Logging subsystem setup completed.")

        # self.__initialize_plugins_and_extensions(args)
        LOGGER.info("Subsystems setup completed.")

        if args.x_test_exception:
            raise Exception("Test exception.")

        return args
        # pylint: enable=broad-exception-raised

    def __handle_error(
        self,
        formatted_error: str,
        thrown_error: Optional[Exception],
        exit_on_error: bool = True,
        print_prefix: str = "\n\n",
    ) -> None:
        LOGGER.warning(formatted_error, exc_info=thrown_error)

        stack_trace = (
            "\n" + traceback.format_exc()
            if self.__show_stack_trace
            and thrown_error
            and not isinstance(thrown_error, ValueError)
            else ""
        )

        print(f"{print_prefix}{formatted_error}{stack_trace}", file=sys.stderr)
        assert exit_on_error
        sys.exit(1)

    def __init(self) -> None:
        self.__dsm.from_properties(self.__properties)
        self.__lim.from_properties(self.__properties)

    def __handle_init(self) -> None:

        # export PS1="\$(/c/Users/jackd/.virtualenvs/pyshell-ebIUQutz/Scripts/python.exe /c/enlistements/pyshell/main.py run)"
        # eval "$(python "c:\\enlistments\\pre-commit-test\\test.py" init)"

        # print(os.getenv("PWD"))
        # print(os.getenv("HOME"))
        # print(sys.executable)
        #
        # C:\Users\jack\.virtualenvs\pyshell-lw4-13FC\Scripts\python.exe ==> /c/Users/jack/.virtualenvs/pyshell-lw4-13FC/Scripts/python.exe
        print(
            'export PS1="\\$(IS_PYSHELL_PS1=1 /c/Users/jack/.virtualenvs/pyshell-lw4-13FC/Scripts/python.exe /c/enlistments/pyshell/main.py run)"'
        )
        LOGGER.info("Command 'init' completed successfully.")
        sys.exit(0)

    def __handle_run(self, args: argparse.Namespace) -> None:
        assert args.primary_subparser == "run"
        self.__init()
        value_cache: Dict[str, str] = {}
        self.__dsm.evaluate(value_cache, self.__lim)
        print(self.__lim.generate(value_cache))
        LOGGER.info("Command 'run' completed successfully.")

    # pylint: disable=broad-exception-caught
    def main(self, direct_args: Optional[List[str]] = None) -> None:
        """
        Handle the main line.
        """
        try:
            args = self.__initialize_subsystems(direct_args)

            LOGGER.info("Processing command: %s", args.primary_subparser)
            if args.primary_subparser == "init":
                self.__handle_init()
            else:
                self.__handle_run(args)
        except Exception as this_exception:
            formatted_error = (
                f"Unexpected Error({type(this_exception).__name__}): {this_exception}"
            )
            self.__handle_error(formatted_error, this_exception)
        finally:
            self.__logging.terminate()
        sys.exit(0)

    # pylint: enable=broad-exception-caught


# pylint: enable=too-few-public-methods, too-many-instance-attributes

# TODO test_mainline_log_file_bad for unix

# TODO way to get at last command return code

# TODO should config pyshell.cfg try all, but pyshell.json only try JSON?
# TODO way to display prefix + suffix (only those) if value is present
# TODO way to display prefix + suffix (only those) if value is equal to X
# TODO way to display prefix + suffix (only those) if value is not equal to X
# TODO disable built in data sources
# TODO handle various column widths
# TODO more logging messages in main areas
# TODO add "datetime" and format field and way to pass similar property configuration
# TODO make 'init' command work for windows
# TODO make 'init' command work generally i.e. init gitbash
# TODO way to initialize the command line easily
# TODO add color to line items
# TODO provide ability to translate windows paths to linux paths, switchable
# TODO add "location" to line items , left, right, title
# TODO filters? i.e. way to shorten long file paths
# TODO plugins for data sources

# TODO template application_configuration_helper and move to application_properties
# TODO logging subsystem
# TODO testing functionality to own package
# TODO template mainline using subcommand objects for subparsers/subcommands
