from abc import ABC, abstractmethod
import ast
import contextlib
import io
from IPython.core.interactiveshell import InteractiveShell
from IPython.core.ultratb import FormattedTB
import sys
from typing import Any, Optional

from .tool_call_status import TCStatus
from core.utils import check_for_input_function_in_string


def is_plain_variable_name(name: str) -> bool:
    try:
        # Parse the string into an AST
        parsed = ast.parse(name, mode="eval")

        # Check if the parsed tree's body is a simple Name node
        return isinstance(parsed.body, ast.Name)
    except SyntaxError:
        # If parsing fails, it's not a valid Python expression
        return False


class WorkspaceBase(ABC):
    def __init__(self):
        self._cell_outputs: dict[str, str] = {}

    def __repr__(self) -> str:
        return str(self)

    @abstractmethod
    def eval_expr(self, expr: str) -> Any:
        pass

    @abstractmethod
    def execute_expr(self, expr: str) -> tuple[str, str, Optional[Exception]]:
        pass

    @abstractmethod
    def run_ipython(self, code: str) -> dict[str, Any]:
        pass

    @abstractmethod
    def add_variables(self, variables: dict[str, Any]) -> None:
        """Add variables to the workspace."""
        pass

    @abstractmethod
    def add_variables_from_other(self, other: "Workspace", variable_names: list[str]) -> None:
        """Add variables from another workspace."""
        pass

    @abstractmethod
    def __copy__(self) -> "WorkspaceBase":
        pass

    def copy(self):
        return self.__copy__()

    @abstractmethod
    def get_variable(var: str) -> Any:
        pass


class CustomInteractiveShell(InteractiveShell):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Disable colored output
        self.InteractiveTB = FormattedTB(color_scheme='NoColor', mode='Plain')

    "The same as InteractiveShell except the errors are printed to stderr instead of stdout."
    def _showtraceback(self, etype, evalue, stb: str):
        """Actually show a traceback.

        Subclasses may override this method to put the traceback on a different
        place, like a side channel.
        """
        if etype.__name__ == "CoreToolInterruption":
            return  # Don't render our internal interruptions
        val = self.InteractiveTB.stb2text(stb)
        try:
            print(val, file=sys.stderr)
        except UnicodeEncodeError:
            print(val.encode("utf-8", "backslashreplace").decode(), file=sys.stderr)


class Workspace(WorkspaceBase):
    def __init__(self):
        self._shell = CustomInteractiveShell()
        self._variables = self._shell.user_ns
        super().__init__()

    def get_cell_counter(self):
        return self._shell.execution_count

    def zero_cell_counter(self):
        "The default starting value for cell counter is 1."
        self._shell.execution_count = 0

    def increment_cell_counter(self):
        self._shell.execution_count += 1

    def add_cell_output(self, name: str, content: str):
        self._cell_outputs[name] = content

    def get_cell_output(self, name: str) -> str | None:
        if name not in self._cell_outputs:
            raise KeyError(f"No cell output with name '{name}' found.")
        return self._cell_outputs.get(name, None)

    def get_variable_names(self) -> list[str]:
        return list(self._variables.keys())

    def get_variable(self, name: str) -> Any:
        return self._variables[name]

    def eval_expr(self, expr: str) -> Any:
        return eval(expr, self._variables.copy())

    def execute_expr(self, expr: str) -> tuple[str, str, Exception | None]: # python 3.10
    # def execute_expr(self, expr: str) -> Tuple[str, str, Optional[Exception]]: # python 3.9
        stdout, stderr, exception = None, None, None
        with (
            io.StringIO() as stdout_buf, contextlib.redirect_stdout(stdout_buf),
            io.StringIO() as stderr_buf, contextlib.redirect_stderr(stderr_buf),
        ):
            try:
                result = self._shell.run_cell(expr)
                exception = result.error_before_exec or result.error_in_exec
            except Exception as e:  # noqa: BLE001
                exception = e

            finally:
                stdout = stdout_buf.getvalue()
                stderr = stderr_buf.getvalue()

        return stdout, stderr, exception

    def run_ipython(self, code: str) -> tuple[TCStatus, dict[str, Any]]:
        if check_for_input_function_in_string(code):
            raise ValueError("The code uses 'input', which is not allowed.")

        stdout, stderr, exception = self.execute_expr(code)
        status = TCStatus.REGULAR_CALL
        # Tool status is delivered in CoreToolInterruption
        if type(exception).__name__ == "CoreToolInterruption":
            status = exception.args[0]
            exception = None

        cell_number = self.get_cell_counter()
        self.increment_cell_counter()
        suffix = f"#{cell_number}" if cell_number is not None else ""
        out = {
            f"stdout{suffix}": stdout,
            f"stderr{suffix}": stderr,
            f"exception{suffix}": exception,
        }

        return status, out

    def append_outputs(self, stdout: str = None, stderr: str = None, exception: Exception = None) -> None:
        out = {}
        for name, var in (("stdouts", stdout), ("stderrs", stderr), ("exceptions", exception)):
            self._variables[name].append(var)
            ix = len(self._variables[name]) - 1
            out[f"{name}[{ix}]"] = var

        return out

    def add_variables(self, variables: dict[str, Any]) -> None:
        self._variables.update(variables)

    def add_variables_from_other(self, other: "Workspace", variable_names: list[str]) -> None:
        missing_names = set(variable_names) - set(other.get_variable_names())
        if missing_names:
            msg = f"Variables {missing_names} are not found in the workspace"
            raise KeyError(msg)

        for name in variable_names:
            self._variables[name] = other._variables[name]  # noqa: SLF001

    def __copy__(self) -> "Workspace":
        new_workspace = Workspace()
        new_workspace._variables = self._variables.copy()  # noqa: SLF001
        return new_workspace
