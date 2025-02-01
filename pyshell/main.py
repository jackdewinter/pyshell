import argparse
import logging
import os
import runpy
import shutil
import sys
import traceback
from typing import List, Optional

from application_properties import ApplicationProperties
from colorama import Back, Fore, Style, init

from pyshell.application_logging import ApplicationLogging
from pyshell.command_processor import CommandProcessor

LOGGER = logging.getLogger(__name__)


class PyShell:

    def __init__(
        self,
        show_stack_trace: bool = False,
        inherit_logging: bool = False,
    ):
        self.__version_number = PyShell.__get_semantic_version()
        self.__properties: ApplicationProperties = ApplicationProperties()
        self.__show_stack_trace = show_stack_trace
        self.__logging = (
            None
            if inherit_logging
            else ApplicationLogging(
                self.__properties,
                default_log_level="CRITICAL",
                show_stack_trace=show_stack_trace,
            )
        )

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

        # ApplicationPropertiesUtilities.add_default_command_line_arguments(parser)
        parser.add_argument(
            "--stack-trace",
            dest="show_stack_trace",
            action="store_true",
            default=False,
            help="if an error occurs, print out the stack trace for debug purposes",
        )
        ApplicationLogging.add_default_command_line_arguments(parser)
        # ReturnCodeHelper.add_command_line_arguments(parser)

        subparsers = parser.add_subparsers(dest="primary_subparser")
        # ExtensionManager.add_argparse_subparser(subparsers)
        # FileScanHelper.add_argparse_subparser(subparsers, True)
        # PluginManager.add_argparse_subparser(subparsers)
        # FileScanHelper.add_argparse_subparser(subparsers, False)
        subparsers.add_parser("init", help="Initialize the...")
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
        if self.__logging:
            self.__logging.pre_initialize_with_args(args)

        # ApplicationConfigurationHelper.apply_configuration_layers(
        #     args, self.__properties, self.__handle_error
        # )

        LOGGER.info("Configuration loaded and applied.  Initial state setup completed.")

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

        if self.__logging:
            self.__logging.initialize(args)

        if direct_args is None:
            LOGGER.debug("Using supplied command line arguments.")
        else:
            LOGGER.debug("Using direct arguments: %s", str(direct_args))

        # self.__initialize_plugins_and_extensions(args)
        return args

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
        if exit_on_error:
            sys.exit(1)

    def main(self, direct_args: Optional[List[str]] = None) -> None:
        try:
            args = self.__initialize_subsystems(direct_args)

            # do stuff here
            print(args.primary_subparser)

        except Exception as this_exception:
            formatted_error = (
                f"Unexpected Error({type(this_exception).__name__}): {this_exception}"
            )
            self.__handle_error(formatted_error, this_exception)
        finally:
            if self.__logging:
                self.__logging.terminate()
            self.__logging = None

    def start(self):

        parser = argparse.ArgumentParser(description="Lint any found Markdown files.")
        parser.add_argument(
            "-c",
            dest="c_mode",
            action="store",
            default="",
        )  # bash: -c: option requires an argument
        parser.add_argument("rest", nargs=argparse.REMAINDER)

        parse_arguments = parser.parse_args()

        if parse_arguments.c_mode:
            x = str(parse_arguments)
            print(x)
            return CommandProcessor().collect_and_process_commands()
        if parse_arguments.rest:
            print("NIY")
            return

        print(parse_arguments)

        init()

        # print("\033[2J\033[;H")
        print(Fore.RED + "some red text")
        print(Back.GREEN + "and with a green background")
        print(Style.DIM + "and in dim text")
        print(Style.RESET_ALL)
        print("back to normal now")

        # where the first part makes the text red (31), bold (1), underlined (4) and the last part clears all this (0).
        print("\033[31;1;4mHello\033[0m")
        print("\033[38;2;255;82;82;48;2;82;82;255mHello\033[0m")

        print("\u03B5")
        print("sys.getdefaulencoding()=", sys.getdefaultencoding())
        print("  \ue0b0  \ue0b0")

        # am = AnsiMarkup()
        # print(am.parse("<b><r>bold red</r></b>"))
        # print(am.parse("<r>red</r>"))
        # print(am.parse("<BLUE><red>bold red</red></BLUE>"))

        print("Number of columns and Rows: " + str(os.get_terminal_size()))
        print("Number of columns and Rows: " + str(shutil.get_terminal_size()))
        d = shutil.which("where")
        print("cmd=" + str(d))

        print("os-->" + os.name)  # "nt"

        return CommandProcessor().collect_and_process_commands()
