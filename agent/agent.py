from __future__ import annotations

import asyncio
from datetime import datetime
from functools import partial
import logging
import os
from pathlib import Path
import pickle
import shutil
import sys
import traceback
from typing import Any, Callable

from prettyprinter import pformat
from core.utils import git_sha

from core.messages import Message, Role
from core.llm import ResponseFormat
from core.steps import StepMessages
from core.utils import Colors, shallow_copy, random_id

from .clients import BaseClient
from .configs import AgentConfig
from .history import History, Tag
from .stats import Stats
from . import tips as tip
from .tips import SectionedContent, ExerciseSectionedContent
from .tool_calls import parse_run_ipython, dump_tool_output
from .tool_call_status import TCStatus as TCS
from .trajectory import Trajectory
from .workspace import Workspace

class Agent:
    """Agent class that runs a task using a client and a workspace.
    The agent is responsible for managing the task execution, including
    handling the workspace, logging, and communication with the client.
    """

    def __init__(self,
        task: str,
        *,
        run_path: Path = None,  # None means no saving
        return_cls_name: str = None,
        config: AgentConfig = None,
        client: BaseClient = None,
        max_llm_calls: int = None,
        input_variables: dict[str, Any] = None,
        initial_status: dict = None,
        init_script: str = None,
    ):
        self.task: str = task
        self.stats = Stats.from_status(initial_status)
        self.client = client
        self.config = config or AgentConfig()
        self.max_llm_calls = max_llm_calls

        self.msg_builder = MessageBuilder(config)
        self.workspace: Workspace = Workspace()
        self.init_script = init_script

        self.history = History()

        self.step: int = 0

        self.setup_logging(run_path)

        self.return_value = None
        self.return_cls_name = return_cls_name

        tools = config.engine_config.get_tools()
        self.core_tools = CoreTools(tools, agent=self)
        self.workspace.add_variables({"tools": self.core_tools})
        self.tool_docs_list = self.config.prompt_config.tool_docs_list
        if self.tool_docs_list is None:
            self.tool_docs_list = list(tools.keys())

        if input_variables:
            self.workspace.add_variables(input_variables)

        if config and config.engine_config.modify_agent:
            config.engine_config.modify_agent(self)

        trajectory_metadata = {
            "model": self.client.model if hasattr(self.client, "model") else None,
            "git_sha": git_sha(),
        }
        self.trajectory = Trajectory(
            task=task,
            return_cls_name=return_cls_name,
            input_variables=input_variables,
            init_script=init_script,
            metadata=trajectory_metadata,
        )

    def __getstate__(self):
        state = {
            "task": self.task,
            "workspace": self.workspace.__getstate__(),
            "step": self.step,
            "run_path": self.run_path,
            "config": self.config,
        }
        return state

    def __setstate__(self, state):
        workspace = Workspace()
        workspace.__setstate__(state["workspace"])
        state["workspace"] = workspace

        self.__dict__.update(state)

        self.history = self.load_history()

    def __copy__(self):
        "Create a shallow copy."
        new_agent = shallow_copy(self)
        new_agent.workspace = self.workspace.copy()
        new_agent.history = self.history.copy()
        return new_agent

    copy = __copy__

    def save(self):
        if self.run_path is not None:
            filename = self.run_path / f"state_{self.step:03d}.pkl"
            self._log_and_print(f"Saving state to {filename}")
            with open(filename, 'wb') as file:
                pickle.dump(self, file)

    @classmethod
    def from_saved(cls, state_filename: os.PathLike) -> "Agent":
        with open(state_filename, 'rb') as file:
            agent = pickle.load(file)

        return agent

    def __str__(self):
        s = (
            "STATE:\n"
            f"Task: {self.task}\n"
            f"\nHistory contains {len(self.history.messages)} messages."
        )

        return s

    def _print(self, *args, **kw):
        if self.config.verbose:
            # This will print to the console even if the output is redirected
            print(*args, **kw, flush=True, file=sys.__stdout__)

    def _log(self, obj: Any):
        if self.logger:
            self.logger.debug(str(obj))

    def _log_and_print(self, obj: Any):
        self._log(obj)
        self._print(obj)

    def log_stats(self):
        if self.config.log_stats:
            stats = self.stats.get_root_stats()
            #costs = get_cost(self.model, stats.usage)
            costs = float("NaN")
            s = (
                f'{Colors.ITALIC}'
                "===== STATS =====\n"
                f'{stats}\n'
                f'costs: {costs: .2f}\n'
                f"===== /STATS =====\n{Colors.DEFAULT}"
            )
            self._log_and_print(s)

    def briefing_message(self) -> Message:
        sections = self.msg_builder.sectioned_content(separator="\n\n")
        sections.add(tip.task_description(self.task, self.return_cls_name))

        return Message(
            role=Role.USER,
            content=sections.render(),
            tags={Tag.BRIEFING},
        )

    def process_init_script(self):
        if not self.init_script:
            return
        self.workspace.zero_cell_counter()
        code = f"""\
<run_ipython>
# The following script was executed to initialize your workspace
{self.init_script}
</run_ipython>"""
        tc_msg = Message(role=Role.USER, content=code, tags={Tag.TOOL_CALL, Tag.INIT_SCRIPT})
        self.add_to_history(tc_msg, log=True, print=True)
        asyncio.run(self.execute_ipython_code(code, extra_tag=Tag.INIT_SCRIPT))

    def setup_logging(self, run_path: Path):
        self.run_path = run_path

        logger_name = str(run_path) if run_path else random_id(8)
        self.logger = logger = logging.Logger(logger_name)
        self.logger.setLevel(logging.DEBUG)
        # Remove all existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        if run_path:
            if not run_path.exists():
                run_path.mkdir()
            else:
                # NOTE: We always wipe the existing run path
                shutil.rmtree(run_path)
                run_path.mkdir()

            # Save config
            config_path = run_path / "config.json"
            config_path.write_text(self.config.to_json())

            # View the log file in vscode:
            # * Install ANSI Colors extension in vscode
            # * Open the log file in vscode
            # * Press Ctrl+Shift+P and select "ANSI Text: Open Preview"
            self.output_log = run_path / 'output.ans' if run_path else None
            self._print(f"Project log: {self.output_log}")

            file_handler = logging.FileHandler(self.output_log)
            file_handler.setLevel(logging.DEBUG)
            #format = '%(asctime)s - %(message)s'
            format = '\n====== %(asctime)s ======\n%(message)s'
            file_formatter = logging.Formatter(format)
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    @property
    def history_save_path(self):
        return self.run_path / f"{self.step:03d}.xml" if self.run_path else None

    def save_step_messages(self):
        if self.run_path:
            self.history.save(self.history_save_path)

    def add_to_history(self, msg: Message, log=False, print=False):
        self.history.add_message(msg)
        self.save_step_messages()
        if log:
            self._log(msg)
        if print:
            self._print(msg)

    def _report_error(self, error: str):
        self._log_and_print(error)
        self.final_report = error
        self.return_value = Exception(error)

    def _report_exception(self, e: Exception):
        self.logger.exception("An error occurred: %s", e)
        if self.config.verbose:
            traceback.print_exc()
        self.final_report = str(e)
        self.return_value = e

    async def run(
        self,
        *,
        client: BaseClient = None,
        max_llm_calls: int = None,
    ) -> bool:
        """Run the agent."""
        self.client = client or self.client
        if not self.client:
            raise ValueError("Client has not been set.")
        self.max_llm_calls = max_llm_calls or self.max_llm_calls
        if self.max_llm_calls is None:
            raise ValueError("Max LLM calls is not set.")

        self._log(f"Starting the project with the LLM call quota: {self.max_llm_calls}.\n")
        self._log(f"Current working directory: {os.getcwd()}")

        if self.max_llm_calls <= 0:
            self._report_error(f"The quota of LLM calls is {self.max_llm_calls} which is not enough to run the project.")
            return False

        try:
            while self.step < self.max_llm_calls:  # We should not quit here, this is just a precaution.
                if self.stats.n_calls >= self.max_llm_calls:
                    self._report_error("The project's quota of LLM calls is used up.")
                    return False

                self.prepare_step()
                await self.get_monologue()
                self.trajectory.next_step()
                tool_calls_string = await self.get_ipython_code()

                done = await self.execute_ipython_code(tool_calls_string)
                self.stats.set_duration()
                self.trajectory.save("trajectory", self.run_path)
                if done:
                    if isinstance(self.return_value, Exception):
                        self._log_and_print(f"Project failed: {self.return_value}")
                    else:
                        self._log_and_print('The project is completed successfully.')
                        self._log(self.get_detailed_report())
                    return True

            self._log_and_print(f"Number of step exceeds max_llm_calls which should not be possible: step={self.step}, max_llm_calls={self.max_llm_calls}")

        except Exception as e:
            self._report_exception(e)
            return False

        self._log_and_print("Function Agent.run should not reach here.")

    def get_status(self):
        n_input_tokens = self.client.count_tokens(self.history.get_messages())
        return {
            "now": datetime.now().isoformat(),
            "start_time": self.stats.start_time.isoformat(),
            "step": self.step,
            "n_calls": self.stats.n_calls,
            "max_llm_calls": self.max_llm_calls,
            "remaining_input_tokens": self.config.engine_config.max_input_tokens - n_input_tokens,
        }

    def initialize_history(self, msgs: list[Message]):
        for msg in msgs:
            self.history.add_message(msg)
            self._log_and_print(msg)

    def prepare_step(self, status: dict = None):
        if self.step == 0:
            msgs = [
                self.briefing_message(),
                self.msg_builder.guidelines_message(),
                self.msg_builder.tool_docs_message(),
            ]
            self.initialize_history(msgs)
            self.process_init_script()

        self.log_stats()
        self.step += 1

        self.save_step_messages()

        self.history.mark_messages_outdated([Tag.MONOLOGUE_INSTRUCTION, Tag.TOOL_CALL_INSTRUCTION])
        status = status or self.get_status()
        status_msg = Message(
            Role.USER,
            tip.render_status(status),
            short_content="",
            color=Colors.GREEN,
            tags={Tag.STATUS},
        )
        self.add_to_history(status_msg)
        if self.config.log_status:
            self._log(status_msg)
            self._print(status_msg)
        self.trajectory.next_step(status=status)

    async def get_response(self, response_format: ResponseFormat) -> str:
        kwargs = {"stream": self.config.verbose and self.config.stream}
        kwargs["response_format"] = response_format
        title = response_format.value.upper()
        self._print(Colors.BLUE + f"==== <{title}> ====")
        messages = self.history.get_messages()
        content = await self.client.call(
            messages,
            stats=self.stats,
            verbose=self.config.verbose,
            **kwargs,
        )
        if not self.config.stream:
            self._print(content)
        self._print(f"==== </{title}> ====" + Colors.DEFAULT)

        return content

    async def get_monologue(self) -> None:
        think_inst_msg = self.msg_builder.monologue_instruction_message()
        self.add_to_history(think_inst_msg, log=True, print=True)

        content = await self.get_response(ResponseFormat.MONOLOGUE)
        monologue_msg = Message(Role.AI, content, tags={Tag.MONOLOGUE})
        self.add_to_history(monologue_msg, log=True, print=False)
        self.trajectory.set_response(content)

    async def get_ipython_code(self) -> str:
        sys_msg = self.msg_builder.tool_call_instruction_message()
        self.add_to_history(sys_msg, log=True, print=True)

        content = await self.get_response(ResponseFormat.IPYTHON)
        tc_msg = Message(role=Role.AI, content=content, tags={Tag.TOOL_CALL})
        self.add_to_history(tc_msg, log=True, print=False)
        self.trajectory.set_response(content)

        return content

    async def execute_ipython_code(self, tool_calls_string: str, extra_tag: Tag = None) -> bool:
        "Execute ipython code and return True if the task is completed."
        try:
            code = parse_run_ipython(tool_calls_string)
            status, tool_output = self.workspace.run_ipython(code)
            output = dump_tool_output(tool_output, self.workspace)
        except Exception as e:
            status = TCS.ERROR
            output = "Parsing of IPython cell resulted in the following error:\n"
            output += "\n".join(traceback.format_exception(e))

        to_msg = Message(
            role=Role.USER,
            content=output,
            color=Colors.YELLOW,
            tags={Tag.TOOL_OUTPUT} | ({extra_tag} if extra_tag else set()),
        )
        self.add_to_history(to_msg, log=True, print=True)

        return status == TCS.COMPLETE_TASK

    def print_report(self):
        s = self.get_detailed_report()
        print(s)

    def get_detailed_report(self):
        s = Colors.RED + "==== REPORT ====\n" + self.final_report
        if self.return_value:
            s += f"\nReturn value: {pformat(self.return_value)}\n"
        s += "================" + Colors.DEFAULT
        return s


class MessageBuilder:
    """Construct messages that do not depend on the agent."""
    def __init__(self, config: AgentConfig):
        self.config = config

    def sectioned_content(self, separator: str, top: str = "", bottom: str = "") -> SectionedContent:
        return SectionedContent(separator, top, bottom)

    def guidelines_message(self) -> Message:
        prompt_config = self.config.prompt_config
        if prompt_config.guidelines:
            sections = self.sectioned_content(
                separator="\n\n-------\n",
                top="<guidelines>\n",
                bottom="\n</guidelines>",
            )
            for guideline in prompt_config.guidelines:
                sections.add(guideline, for_teacher=True)

            return Message(
                role=Role.USER,
                content=sections.render(),
                tags={Tag.GUIDELINES},
            )
        else:
            return None

    def tool_docs_message(self) -> Message:
        prompt_config = self.config.prompt_config
        if prompt_config.tool_docs != "none":
            tools = self.config.engine_config.get_tools()

            tool_docs_list = self.config.prompt_config.tool_docs_list
            if tool_docs_list is None:
                tool_docs_list = list(tools.keys())
            docs = tip.get_docs(tools, tool_docs_list,
                long=prompt_config.tool_docs == "long"
            )
            docs = ("\n-------\n" if prompt_config.tool_docs == "long" else "\n").join(docs)
            docs = "<tools_documentation>\n" + docs + "\n</tools_documentation>"

            return Message(
                role=Role.USER,
                content=docs,
                tags={Tag.TOOL_DOCS},
            )
        else:
            return None

    def monologue_instruction_message(self):
        sections = self.sectioned_content(separator="")
        sections.add(tip.MONOLOGUE_PROMPT)
        if self.config.prompt_config.monologue_format:
            sections.add(tip.MONOLOGUE_INST, for_teacher=True)

        return Message(
            role=Role.USER,
            content=sections.render(),
            tags={Tag.MONOLOGUE_INSTRUCTION},
            short_content=tip.MONOLOGUE_PROMPT,
        )

    def tool_call_instruction_message(self):
        sections = self.sectioned_content(separator="")
        sections.add(tip.TOOL_CALL_PROMPT)
        if self.config.prompt_config.monologue_format:
            sections.add(tip.TOOL_CALL_INST, for_teacher=True)

        return Message(
            role=Role.USER,
            content=sections.render(),
            tags={Tag.TOOL_CALL_INSTRUCTION},
            short_content=tip.TOOL_CALL_PROMPT,
        )


class ExerciseMessageBuilder(MessageBuilder):
    def __init__(self, config: AgentConfig):
        super().__init__(config)

    def sectioned_content(self, separator: str, top: str = "", bottom: str = "") -> ExerciseSectionedContent:
        return ExerciseSectionedContent(
            separator, top, bottom,
        )

    def recreate_messages(self, step_messages: StepMessages) -> StepMessages:
        """Add the teacher/dropout tags for exercise creation."""
        # The second element of the tuple tells what tags to add
        # IMPORTANT: Makre sure that the tags are set correctly
        funcs_tags = {
            Tag.GUIDELINES: (self.guidelines_message, {Tag.ESCAPED}),
            Tag.TOOL_DOCS: (self.tool_docs_message, {Tag.STUDENT_DROPOUT}),
            Tag.MONOLOGUE_INSTRUCTION: (self.monologue_instruction_message, {Tag.ESCAPED}),
            Tag.TOOL_CALL_INSTRUCTION: (self.tool_call_instruction_message, {Tag.ESCAPED}),
        }
        for j, msg in enumerate(step_messages):
            new_msg = None
            for tag, (func, new_tags) in funcs_tags.items():
                if tag in msg.tags:
                    if Tag.TOOL_DOCS not in msg.tags:
                        new_msg = func()
                    else:
                        new_msg = msg.copy()
                    new_msg.tags |= new_tags

            if new_msg:
                step_messages[j] = new_msg

        return step_messages


class CoreTools:
    def __init__(self, tools: dict[str, Callable], agent: Agent):
        self._agent = agent

        new_class = type("CoreTools", (object,), {})
        self.__class__ = new_class

        self.tool_names = list(tools.keys())
        for name, method in tools.items():
            tool_method = partial(method, self._agent)
            tool_method.__doc__ = method.__doc__
            setattr(self, name, tool_method)
