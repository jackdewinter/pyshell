import sys
from cmd import Cmd
from dataclasses import dataclass
from typing import List

# pylint: disable=unused-import, bare-except
try:
    try:
        if sys.platform.startswith("win"):
            import readline
        else:
            import gnureadline as readline
    except ImportError:
        import pyreadline as readline  # noqa: F401
    HAVE_READLINE = True
except:  # noqa: E722
    HAVE_READLINE = False
# pylint: enable=unused-import, bare-except


class ParseError(Exception):
    def __init__(self, bad_token: str) -> None:
        self.bad_token = bad_token


@dataclass
class Robert:
    current_digits: str = ""
    max_digits = -1
    number_base = 10


@dataclass
class Separator:
    xx: str


@dataclass
class Bob:
    have_backslash: bool = False
    have_single_quotes: bool = False
    have_double_quotes: bool = False
    have_whitespace: bool = False
    have_dollar_sign: bool = False
    have_ansi_quotes: bool = False
    have_ascii_backslash: bool = False
    have_backslash_number_start: bool = False
    have_backslash_control_start = False
    have_command_separator_start = False
    backslash_number: Robert = Robert()
    line_part: str = ""
    parse_error: Exception = None

    def __init__(self):
        super.__init_subclass__()
        self.line_segment = []

    @property
    def is_incomplete(self):
        return (
            self.have_backslash
            or self.have_single_quotes
            or self.have_double_quotes
            or self.have_ansi_quotes
        )

    def reset_collection(self):
        self.line_segment.clear()
        self.line_part = ""

    def save_separator_and_reset(self):
        if not self.line_segment or isinstance(self.line_segment[-1], Separator):
            raise ParseError(self.line_part)
        self.line_segment.append(Separator(self.line_part))
        self.line_part = ""
        self.have_backslash = self.have_single_quotes = self.have_double_quotes = (
            self.have_whitespace
        ) = self.have_dollar_sign = self.have_ansi_quotes = (
            self.have_ascii_backslash
        ) = False

    def save_line_part_and_reset(self):
        if self.line_part:
            self.line_segment.append(self.line_part)
        self.line_part = ""
        self.have_backslash = self.have_single_quotes = self.have_double_quotes = (
            self.have_whitespace
        ) = self.have_dollar_sign = self.have_ansi_quotes = (
            self.have_ascii_backslash
        ) = False

    def __str__(self) -> str:
        return f"back={self.have_backslash},squote={self.have_single_quotes},dquote={self.have_double_quotes},ws={self.have_whitespace},part={self.line_part},segments={self.line_segment}"


class ExtendedCmd(Cmd):
    __end_of_text = "\x03"
    __whitespace_characters = [" ", "\t", "\n"]
    __distinct_part_characters = [" ", "\t", "\n", ";", "&", "|"]
    __command_separators = [";", "&&", "||"]

    def __init__(self, stdout, stderr, use_rawinput=True, supplied_input=None):
        super().__init__(completekey="tab", stdin=None, stdout=stdout)

        self.stderr = stderr

        self.__line_collection_state = Bob()

        self.old_completer = None
        self.readline_rl = None

        self.use_rawinput = use_rawinput
        self.supplied_input = (
            supplied_input.split("\n") if supplied_input is not None else None
        )

    @property
    def is_interactive(self) -> bool:
        return bool(self.supplied_input is None)

    def command_loop(self, intro=None) -> None:
        try:
            self.preloop()
            if self.is_interactive:
                self.initialize_read_line()

            if self.supplied_input is not None:
                if intro:
                    self.stdout.write(f"{intro}\n")
            while self.process_next_line():
                pass
            if self.__line_collection_state.is_incomplete:
                if (
                    self.__line_collection_state.have_single_quotes
                    or self.__line_collection_state.have_ansi_quotes
                ):
                    print(
                        "bash: unexpected EOF while looking for matching `'`",
                        file=self.stderr,
                    )
                elif self.__line_collection_state.have_double_quotes:
                    print(
                        'bash: unexpected EOF while looking for matching `"`',
                        file=self.stderr,
                    )
                else:
                    assert False
        finally:
            if self.is_interactive:
                self.terminate_read_line()
            self.postloop()

    def process_next_line(self):
        try:
            line = self.get_next_line()
            if line == ExtendedCmd.__end_of_text:
                return False

            # line = self.precmd(line)
            self.parse_line(line)
            if self.__line_collection_state.is_incomplete:
                if self.is_interactive:
                    print(f"incomplete>>{self.__line_collection_state}")
            elif self.__line_collection_state.parse_error is not None:
                print(
                    f"bash: syntax error near unexpected token `{self.__line_collection_state.parse_error}`"
                )
                self.__line_collection_state.reset_collection()
                self.set_return_code(2)
            else:
                self.__line_collection_state.save_line_part_and_reset()
                if self.is_interactive:
                    print(f"complete>>{self.__line_collection_state}")

                if not self.process_completed_command_line(
                    self.__line_collection_state.line_segment
                ):
                    return False
                self.__line_collection_state.reset_collection()
            return True
            # return self.postcmd(continue_processing, line)
        finally:
            pass
        return True

    def get_next_line(self):
        if self.supplied_input is not None:
            if self.supplied_input:
                line = self.supplied_input.pop(0)
            else:
                line = ExtendedCmd.__end_of_text
        else:
            prompt = "> " if self.__line_collection_state.is_incomplete else "$ "
            if self.use_rawinput:
                try:
                    line = input(prompt)
                except EOFError:
                    line = ExtendedCmd.__end_of_text
            else:
                self.stdout.write(prompt)
                self.stdout.flush()
                line = self.stdin.readline()
                line = line.rstrip("\r\n") if line else ExtendedCmd.__end_of_text
        return line

    def my_complete(self, text, state):
        """Return the next possible completion for 'text'.

        If a command has not been entered, then complete against command list.
        Otherwise try to call complete_<command> to get list of completions.
        """
        return None

    def initialize_read_line(self):
        """
        Initialize the readline support for this instance.
        """

        if self.use_rawinput and self.completekey:
            if HAVE_READLINE:
                # pylint: disable=import-outside-toplevel, redefined-outer-name
                import readline  # noqa: F811
                from readline import rl

                self.old_completer = readline.get_completer()
                self.readline_rl = rl
                readline.set_completer(self.my_complete)
                readline.parse_and_bind(self.completekey + ": complete")

    def terminate_read_line(self):
        """
        Terminate the readline support by this instance.
        """

        if self.old_completer:
            # pylint: disable=import-outside-toplevel, redefined-outer-name
            import readline  # noqa: F811

            readline.set_completer(self.old_completer)
            self.old_completer = None

    def __finish_collecting_backslash_number(self):
        number_base = (
            8
            if self.__line_collection_state.backslash_number.number_base[-1] == "7"
            else 16
        )
        x = int(
            self.__line_collection_state.backslash_number.current_digits, number_base
        )
        # print(f">>digits={self.__line_collection_state.backslash_number.current_digits},base={number_base},x={x}")
        self.__line_collection_state.line_part += chr(x)
        self.__line_collection_state.have_backslash_number_start = False
        self.__line_collection_state.have_ascii_backslash = False

    def __complete_separator(self):
        self.__line_collection_state.save_separator_and_reset()
        self.__line_collection_state.have_command_separator_start = False

    def parse_line(self, line) -> None:

        special_double_quote_characters = '$`"\\\n'

        ansi_special_map = {
            "a": "\a",
            "b": "\b",
            "e": "\x1b",
            "E": "\x1b",
            "f": "\f",
            "n": "\n",
            "r": "\r",
            "t": "\t",
            "v": "\v",
        }

        line = line.strip()
        if not line:
            return None, None, line, None

        try:
            if self.__line_collection_state.have_backslash_number_start:
                self.__finish_collecting_backslash_number()

            if (
                self.__line_collection_state.have_single_quotes
                or self.__line_collection_state.have_double_quotes
            ):
                self.__line_collection_state.line_part += "\n"
            elif self.__line_collection_state.have_ansi_quotes:
                if self.__line_collection_state.have_ascii_backslash:
                    self.__line_collection_state.have_ascii_backslash = False
                    self.__line_collection_state.line_part += "\\"
                self.__line_collection_state.line_part += "\n"
            self.__line_collection_state.have_backslash = False

            for i in line:
                have_consumed_character = False
                if self.__line_collection_state.have_backslash_number_start:
                    continue_collecting = False
                    if i in self.__line_collection_state.backslash_number.number_base:
                        have_consumed_character = True
                        self.__line_collection_state.backslash_number.current_digits += (
                            i
                        )
                        if (
                            len(
                                self.__line_collection_state.backslash_number.current_digits
                            )
                            < self.__line_collection_state.backslash_number.max_digits
                        ):
                            continue_collecting = True
                    if not continue_collecting:
                        self.__finish_collecting_backslash_number()

                if self.__line_collection_state.have_command_separator_start:
                    command_complete = True
                    if (
                        i in ExtendedCmd.__distinct_part_characters
                        and i not in ExtendedCmd.__whitespace_characters
                    ):
                        command_complete = False
                        self.__line_collection_state.line_part += i
                        if (
                            self.__line_collection_state.line_part
                            not in ExtendedCmd.__command_separators
                        ):
                            raise ParseError(self.__line_collection_state.line_part)
                    if command_complete:
                        self.__complete_separator()
                if self.__line_collection_state.have_whitespace:
                    if i in ExtendedCmd.__whitespace_characters:
                        pass
                    else:
                        self.__line_collection_state.have_whitespace = False
                if (
                    self.__line_collection_state.have_backslash_number_start
                    or have_consumed_character
                ):
                    pass
                elif self.__line_collection_state.have_backslash:
                    if self.__line_collection_state.have_double_quotes:
                        if i in special_double_quote_characters:
                            self.__line_collection_state.line_part += i
                        else:
                            self.__line_collection_state.line_part += f"\\{i}"
                    else:
                        self.__line_collection_state.line_part += i
                    self.__line_collection_state.have_backslash = False
                elif self.__line_collection_state.have_backslash_control_start:
                    xxx = ord(i)
                    if xxx < 128:
                        self.__line_collection_state.line_part += chr(xxx % 32)
                    else:
                        self.__line_collection_state.line_part += f"\c{i}"
                    self.__line_collection_state.have_backslash_control_start = False
                    self.__line_collection_state.have_ascii_backslash = False
                elif self.__line_collection_state.have_ascii_backslash:
                    if i in ["\\", "'", '"', "?"]:
                        self.__line_collection_state.line_part += i
                        self.__line_collection_state.have_ascii_backslash = False
                    elif i in ansi_special_map:
                        self.__line_collection_state.line_part += ansi_special_map[i]
                        self.__line_collection_state.have_ascii_backslash = False
                    elif i in ["e", "E"]:
                        self.__line_collection_state.line_part += f"\{i}"
                        self.__line_collection_state.have_ascii_backslash = False
                    elif i == "c":
                        self.__line_collection_state.have_backslash_control_start = True
                    elif i in "01234567":
                        self.__line_collection_state.backslash_number.current_digits = i
                        self.__line_collection_state.backslash_number.number_base = (
                            "01234567"
                        )
                        self.__line_collection_state.backslash_number.max_digits = 3
                        self.__line_collection_state.have_backslash_number_start = True
                    elif i == "x":
                        self.__line_collection_state.backslash_number.current_digits = (
                            ""
                        )
                        self.__line_collection_state.backslash_number.number_base = (
                            "0123456789abcdefABCDEF"
                        )
                        self.__line_collection_state.backslash_number.max_digits = 2
                        self.__line_collection_state.have_backslash_number_start = True
                    elif i == "u":
                        self.__line_collection_state.backslash_number.current_digits = (
                            ""
                        )
                        self.__line_collection_state.backslash_number.number_base = (
                            "0123456789abcdefABCDEF"
                        )
                        self.__line_collection_state.backslash_number.max_digits = 4
                        self.__line_collection_state.have_backslash_number_start = True
                    elif i == "U":
                        self.__line_collection_state.backslash_number.current_digits = (
                            ""
                        )
                        self.__line_collection_state.backslash_number.number_base = (
                            "0123456789abcdefABCDEF"
                        )
                        self.__line_collection_state.backslash_number.max_digits = 8
                        self.__line_collection_state.have_backslash_number_start = True
                    else:
                        self.__line_collection_state.line_part += f"\\{i}"
                        self.__line_collection_state.have_ascii_backslash = False
                elif self.__line_collection_state.have_single_quotes:
                    if i == "'":
                        self.__line_collection_state.have_single_quotes = False
                    else:
                        self.__line_collection_state.line_part += i
                elif self.__line_collection_state.have_double_quotes:
                    if i == '"':
                        self.__line_collection_state.have_double_quotes = False
                    elif i == "\\":
                        self.__line_collection_state.have_backslash = True
                    else:
                        self.__line_collection_state.line_part += i
                elif self.__line_collection_state.have_ansi_quotes:
                    if i == "'":
                        self.__line_collection_state.have_ansi_quotes = False
                    elif i == "\\":
                        self.__line_collection_state.have_ascii_backslash = True
                    else:
                        self.__line_collection_state.line_part += i
                elif self.__line_collection_state.have_dollar_sign:
                    if i == "'":
                        self.__line_collection_state.have_dollar_sign = False
                        self.__line_collection_state.have_ansi_quotes = True
                    else:
                        self.__line_collection_state.have_dollar_sign = False
                elif i == "$":
                    self.__line_collection_state.have_dollar_sign = True
                elif i == "\\":
                    self.__line_collection_state.have_backslash = True
                elif i == '"':
                    self.__line_collection_state.have_double_quotes = True
                elif i == "'":
                    self.__line_collection_state.have_single_quotes = True
                elif i in ExtendedCmd.__distinct_part_characters:
                    if not self.__line_collection_state.have_command_separator_start:
                        self.__line_collection_state.save_line_part_and_reset()
                    if i in ExtendedCmd.__whitespace_characters:
                        self.__line_collection_state.have_whitespace = True
                    else:
                        if (
                            not self.__line_collection_state.have_command_separator_start
                        ):
                            self.__line_collection_state.line_part += i
                            self.__line_collection_state.have_command_separator_start = (
                                True
                            )
                else:
                    self.__line_collection_state.line_part += i
            # cmd, arg = line[:i], line[i:].strip()
            if self.__line_collection_state.have_command_separator_start:
                self.__complete_separator()
        except ParseError as this_exception:
            self.__line_collection_state.parse_error = this_exception

    def process_completed_command_line(self, arguments):
        return 0

    def set_return_code(self, return_code):
        pass
