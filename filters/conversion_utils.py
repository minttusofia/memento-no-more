# %%
from copy import deepcopy
import os
from pathlib import Path
import shutil
from xml.etree import ElementTree as ET

from agent import AGENT_DATASET_PATH
from agent.agent import ExerciseMessageBuilder
from agent.configs import AgentConfig
from core.llm import ResponseFormat, START_SEQUENCES, STOP_SEQUENCES
from core.steps import StepMessages
from core.tags import Tag
from core.utils import escape
from training.student_teacher_dataset import AgentExercise


REQUIRE_TEACHER = True  # Only create samples if teacher has extra information
MERGE_MESSAGES = False

# %%
def get_steps_from_run(run_path: Path) -> list[StepMessages]:
    step_paths = sorted([p for p in run_path.glob("[0-9][0-9][0-9].xml") if p.name != "000.xml"])
    steps: list[StepMessages] = []
    for step_path in step_paths:
        step_messages = StepMessages.from_xml_path(step_path)
        step_messages.metadata.update({
            "path": absolute_to_relative_path(str(step_path)),
            "agent_config": AgentConfig.from_run_path(run_path),
        })
        steps.append(step_messages)

    return steps


# %%
# The following functions are used for the new-style exercise files
SEQUENCE_DICT = {
    "monologue": (
        START_SEQUENCES[ResponseFormat.MONOLOGUE],
        STOP_SEQUENCES[ResponseFormat.MONOLOGUE],
    ),
    "ipython": (
        START_SEQUENCES[ResponseFormat.IPYTHON],
        STOP_SEQUENCES[ResponseFormat.IPYTHON],
    ),
}


def prepare_step_for_exercise(step_messages: StepMessages, strict=True, inplace=True) -> StepMessages:
    """Prepare step messages for exercise:

    * Remove trailing messages which are not assistant messages.
    * Remove start and end sequences (e.g. <inner_monologue>) from all assistant messages.
    * Add Tag.TARGET to the assistant messages produced at this step.
    * Recreate messages which should have <student_dropout> tags

    The input list `step_msgs` is modified in place by default."""

    if not inplace:
        step_messages = deepcopy(step_messages)

    # Remove trailing non-assistant messages
    for i in range(len(step_messages) - 1, -1, -1):
        if step_messages[i].role.value != "assistant":
            del step_messages[i]
        break

    target_processed = False
    for i in range(len(step_messages) - 1, -1, -1):
        msg = step_messages[i]
        if msg.role.value != "assistant":
            continue

        if not target_processed:
            msg.tags.add(Tag.TARGET)
        # All assistant messages before the last monologue are not targets
        if Tag.MONOLOGUE in msg.tags:
            target_processed = True

        # Strip start and stop sequences from assistant messages
        if Tag.MONOLOGUE in msg.tags:
            msg_tag = Tag.MONOLOGUE
            response_format = "monologue"
        elif Tag.TOOL_CALL in msg.tags:
            msg_tag = Tag.TOOL_CALL
            response_format = "ipython"
        else:
            raise RuntimeError(f"No response format recognised in {msg}")

        start_seq, stop_seq = SEQUENCE_DICT[response_format]
        if msg.content.startswith(start_seq):
            msg.content = msg.content[len(start_seq):]
        else:
            err_msg = f"Message is tagged with {msg_tag} but it does not start with {repr(start_seq)}.\n{msg}"
            raise RuntimeError(err_msg)

        if msg.content.endswith(stop_seq):
            msg.content = msg.content[: -len(stop_seq)]
        else:
            err_msg = f"Message is tagged with {msg_tag} but it does not end with {repr(stop_seq)}.\n{msg}"
            if strict:
                raise RuntimeError(err_msg)
            else:
                print(err_msg)

    # Recreate student_dropout messages
    ExerciseMessageBuilder(step_messages.metadata["agent_config"]).recreate_messages(step_messages)

    return step_messages


def format_attrib(attrib: dict[str, str]) -> str:
    ret = ""
    for k, v in attrib.items():
        ret += f" {k}={repr(v)}"
    return ret


def absolute_to_relative_path(path: os.PathLike) -> str:
    path = str(path)
    path = path.replace(str(AGENT_DATASET_PATH), "AGENT_DATASET_PATH")
    return path


def step_to_exercise(step_messages: StepMessages, metadata_as_json: bool = False) -> str:
    xml_content = "<exercise>\n\n"
    if metadata_as_json:
        xml_content += f'<metadata>\n{escape(step_messages.metadata.to_json())}\n</metadata>\n\n'
    elif path := step_messages.metadata.get("path"):
        xml_content += f'<metadata path="{path}" />\n\n'
    for msg in step_messages:
        msg_tag = msg.role.value
        attrib = {}
        if msg_tag == "assistant":
            if Tag.TARGET in msg.tags:
                msg_tag += "_target"
            if Tag.MONOLOGUE in msg.tags:
                attrib["response_format"] = ResponseFormat.MONOLOGUE.value
            elif Tag.TOOL_CALL in msg.tags:
                attrib["response_format"] = ResponseFormat.IPYTHON.value
            else:
                # Assume no response format
                pass
        else:
            if Tag.STUDENT_DROPOUT in msg.tags:
                attrib["recipient"] = "student_dropout"
            elif Tag.TEACHER in msg.tags:
                attrib["recipient"] = "teacher"
            elif Tag.STUDENT in msg.tags:
                attrib["recipient"] = "student"
        xml_content += f"<{msg_tag}{format_attrib(attrib)}>"
        xml_content += msg.content if Tag.ESCAPED in msg.tags else escape(msg.content)
        xml_content += f"</{msg_tag}>\n\n"
    return xml_content + "</exercise>\n\n"


HEADER = '<?xml version="1.0" encoding="UTF-8"?>'

def save_steps_as_exercises(
    steps: list[StepMessages],
    xml_path: os.PathLike,
    metadata_as_json: bool = False,
):
    exercises_str = f'{HEADER}\n\n'
    exercises_str += "<exercises>\n\n"
    for step_messages in steps:
        ret = step_to_exercise(step_messages, metadata_as_json)
        _root = ET.fromstring(ret)  # Make sure it renders properly as XML
        exercises_str += ret
    exercises_str += "</exercises>\n"
    with open(xml_path, "w") as f:
        f.write(exercises_str)


def save_exercises(exercises: list[AgentExercise], xml_path: Path):
    exercises_str = f'{HEADER}\n\n'
    exercises_str += "<exercises>\n\n"
    exercises_str += "\n\n".join(
        [ET.tostring(ex.exercise_element, encoding="unicode") for ex in exercises]
    )
    exercises_str += "</exercises>\n"
    _root = ET.fromstring(exercises_str)  # Make sure it renders properly as XML
    with open(xml_path, "w") as f:
        f.write(exercises_str)


def remove_run_from_agent_data(run_path: Path, verbose: bool = False):
    xml_path = run_path.parent.parent.parent / "xml" / f"{run_path.parent.name}_{run_path.name}.xml"
    if xml_path.exists():
        if verbose:
            print(f"Removing {xml_path}")
        xml_path.unlink()
    if run_path.exists():
        if verbose:
            print(f"Removing {run_path}")
        shutil.rmtree(run_path)


def combine_exercises(source_xml_paths: list[Path], target_xml_path: Path, verbose: bool = False):
    exercises_str = f'{HEADER}\n\n'
    exercises_str += "<exercises>\n\n"
    for xml_path in source_xml_paths:
        xml_content = xml_path.read_text()

        # Extract text within <exercises> tag
        start_idx = xml_content.find("<exercises>") + len("<exercises>")
        end_idx = xml_content.find("</exercises>")
        xml_content = xml_content[start_idx:end_idx]

        exercises_str += xml_content

    exercises_str += "</exercises>\n"
    target_xml_path.write_text(exercises_str)

    if verbose:
        n_exercises = exercises_str.count("<exercise>")
        print(f"{n_exercises} exercises combined to {target_xml_path}")
