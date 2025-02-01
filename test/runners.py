import io
import sys
from test.pytest_execute import InProcessResult, SystemState

from pyshell.command_processor import CommandProcessor


def execute_script_with_direct_inline(supplied_input) -> InProcessResult:
    try:
        saved_state = SystemState()

        std_output = io.StringIO()
        std_error = io.StringIO()

        sys.stdout = std_output
        sys.stderr = std_error

        cmd_processor = CommandProcessor(script_input=supplied_input)
        return_code = cmd_processor.collect_and_process_commands()

        return InProcessResult(return_code, std_output, std_error)
    finally:
        saved_state.restore()
