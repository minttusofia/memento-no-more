from copy import deepcopy
import glob
from pathlib import Path

from core.steps import StepMessages
from core.tags import Tag
from .conversion_utils import get_steps_from_run


def trim_tool_output(step_messages: StepMessages) -> StepMessages:
    if len(step_messages) > 0 and Tag.TOOL_OUTPUT in step_messages[-1].tags:
        step_messages = deepcopy(step_messages)
        step_messages.pop()
    return step_messages


def trim_tool_call(step_messages: StepMessages) -> StepMessages:
    if len(step_messages) > 0 and Tag.TOOL_CALL in step_messages[-1].tags:
        step_messages = deepcopy(step_messages)
        step_messages.pop()
    return step_messages


def trim_tool_call_instruction(step_messages: StepMessages) -> StepMessages:
    if len(step_messages) > 0 and Tag.TOOL_CALL_INSTRUCTION in step_messages[-1].tags:
        step_messages = deepcopy(step_messages)
        step_messages.pop()
    return step_messages


def trim_monologue(step_messages: StepMessages) -> StepMessages:
    if len(step_messages) > 0 and Tag.MONOLOGUE in step_messages[-1].tags:
        step_messages = deepcopy(step_messages)
        step_messages.pop()
    return step_messages


def monologue_prompt_from_step(step_messages: StepMessages) -> StepMessages:
    step_messages = trim_tool_output(step_messages)
    step_messages = trim_tool_call(step_messages)
    step_messages = trim_tool_call_instruction(step_messages)
    step_messages = trim_monologue(step_messages)
    assert len(step_messages) > 0 and Tag.MONOLOGUE_INSTRUCTION in step_messages[-1].tags or Tag.FEEDBACK in step_messages[-1].tags
    return step_messages


def ipython_response_from_step(step_messages: StepMessages) -> str | None:
    step_messages = trim_tool_output(step_messages)
    response = step_messages[-1]
    if Tag.TOOL_CALL in response.tags:
        return response.content
    else:
        return None


def agent_and_status_messages_from_step(step_messages: StepMessages) -> list | None:
    step_messages = trim_tool_output(step_messages)
    agent_and_step_messages = []
    for message in step_messages:
        if message.role.value == 'assistant' or Tag.STATUS in message.tags:
            agent_and_step_messages.append(message)
    if len(agent_and_step_messages) > 0:
        return agent_and_step_messages
    else:
        return None


def agent_status_task_messages_from_step(step_messages: StepMessages) -> list | None:
    step_messages = trim_tool_output(step_messages)
    agent_and_step_messages = []
    for message in step_messages:
        if message.role.value == 'assistant' or Tag.STATUS in message.tags or Tag.BRIEFING in message.tags:
            agent_and_step_messages.append(message)
    if len(agent_and_step_messages) > 0:
        return agent_and_step_messages
    else:
        return None


def load_history_xml_dataset(dir_patterns) -> list[StepMessages]:
    steps: list[StepMessages] = []
    for dir_pattern in dir_patterns:
        for run_path in sorted(glob.glob(str(dir_pattern))):
            steps += get_steps_from_run(Path(run_path))
    return steps


def load_steps_xml_dataset(dir_patterns) -> list[StepMessages]:
    steps: list[StepMessages] = []
    for dir_pattern in dir_patterns:
        for step_file in sorted(glob.glob(str(dir_pattern))):
            steps.append(StepMessages.from_xml_path(step_file))
    return steps


def save_steps_dataset(steps: list[StepMessages], out_dir: Path):
    if not out_dir.exists():
        out_dir.mkdir(parents=True)
    for i, step_messages in enumerate(steps):
        step_messages.to_xml_path(out_dir / f"step_{i:06d}.xml")
