from __future__ import annotations

from collections import OrderedDict
from datetime import datetime
import inspect
import types
from typing import Callable, Type, Union

from core.utils import elapsed_time_string_short, escape

def task_description(task: str, return_cls_name: str = None) -> str:
    if return_cls_name:
        task += "\n\n" + f"When you complete the task, please instantiate and return an object of class {return_cls_name}."

    return f"""\
<task_description>
{task}
</task_description>"""


def render_return_cls(return_cls: Type) -> str:
    if isinstance(return_cls, types.UnionType) or isinstance(return_cls, types.GenericAlias):
        return str(return_cls)
    if isinstance(return_cls.__init__, types.FunctionType):
        return "return_cls" + str(inspect.signature(return_cls)).replace(" -> None", "")
    return return_cls.__name__


def return_cls_description(return_cls: Type) -> str:
    if not return_cls:
        return ""
    txt = "When you complete the task, please "
    return_str = render_return_cls(return_cls)
    if "return_cls" in return_str:
        return txt + "instantiate and return an object of class return_cls whose constructor has the following signature: " + return_str
    return txt + "return a value of type " + return_str


GUIDELINES = OrderedDict()

GUIDELINES["response_format"] = """\
Response format

Please use the following format to structure your inner monologue and tool calls:
<inner_monologue>
Your thinking goes here (analysing the situation, planning)
</inner_monologue>
<run_ipython>
This is where you implement the first step of your plan by running a cell in iPython.
</run_ipython>"""


MONOLOGUE_PROMPT = "Please proceed with your inner monologue to prepare your next action."
MONOLOGUE_INST = """\
 Strictly follow the XML-like format below:
<inner_monologue>
Thoughts
</inner_monologue>"""
TOOL_CALL_PROMPT = "Please act by running an iPython cell."
TOOL_CALL_INST = """\
 Strictly follow the XML-like format below:
<run_ipython>
# iPython cell goes here
</run_ipython>"""


class SectionedContent:
    def __init__(self,
        separator: str = "\n\n",
        top: str = "",
        bottom: str = "",
    ):
        self.sections: list[str | SectionedContent] = []
        self.separator = separator
        self._top = top
        self._bottom = bottom

    def add(self, content: str | SectionedContent, for_teacher: bool = False):
        "Argument `for_teacher` is ignored in this class."
        self.sections.append(content)

    def render(self) -> str:
        content = self._top
        for i, section in enumerate(self.sections):
            separator = self.separator if i > 0 else ""
            content += self._render_section(separator, section)
        content += self._bottom
        return content

    def _render_section(self, separator: str, section: Union[str, SectionedContent]) -> str:
        # This method is overridden in ExerciseSectionedContent
        s_content = section.render() if hasattr(section, "render") else section
        return separator + s_content


class ExerciseSectionedContent(SectionedContent):
    """SectionedContent in which sections can be marked with the teacher tags.
    This class is used for creating exercises.
    """
    def __init__(self,
        separator: str = "\n\n",
        top: str = "",
        bottom: str = "",
    ):
        self.sections: list[tuple[str | ExerciseSectionedContent, bool]] = []
        self.separator = separator

        self._top = escape(top) if top else ""
        self._bottom = escape(bottom) if bottom else ""

    def add(self, content: Union[str, ExerciseSectionedContent], for_teacher: bool = False):
        self.sections.append((content, for_teacher))

    def _render_section(self, separator: str, section: tuple[str | ExerciseSectionedContent, bool]) -> str:
        s_content = escape(separator)
        section, for_teacher = section
        is_string = not hasattr(section, "render")
        s_content += escape(section) if is_string else section.render()
        if for_teacher:
            s_content = f"<student_dropout>{s_content}</student_dropout>"

        return s_content


def render_time_and_date(now: datetime | None = None):
    now = now or datetime.now()
    return " ".join([now.date().isoformat(), now.time().strftime('%H:%M:%S')])


def render_status(status: dict):
    start_time = datetime.fromisoformat(status["start_time"])
    now = datetime.fromisoformat(status["now"])
    return f"""\
<status>
Current date and time: {render_time_and_date(now)}
Time elapsed since the project beginning: {elapsed_time_string_short(start_time, now)}
You are on step {status["step"]}
Resources spent so far: {status["n_calls"]}
Number of input tokens remaining: {status["remaining_input_tokens"]}
</status>"""


def get_docs(tools: dict[str, Callable], tool_names: list[str], long: bool = True) -> list[str]:
    missing_tools = set(tool_names) - set(tools.keys())
    if missing_tools:
        raise KeyError(f"Tools {missing_tools} are not in the list of tools.")
    docs = [tools[name].__doc__ for name in tool_names]
    if long:
        return docs
    else:
        return [doc.split("\n")[0] for doc in docs]
