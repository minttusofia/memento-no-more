from pathlib import Path
from tqdm import tqdm

from core.steps import StepMessages
from .xml_trajectory import trim_tool_output
from .base import BaseReviewFilter


async def filter_steps(steps: list[StepMessages], review_filter: BaseReviewFilter) -> tuple[list[StepMessages], dict[int, str], dict[int, str]]:
    filtered_steps: list[StepMessages] = []
    filtered_reasons: dict[int, str] = {}
    accept_reasons: dict[int, str] = {}
    for i, step_messages in tqdm(enumerate(steps)):
        try:
            reasoning, accept = await review_filter.check_step(step_messages)
            if accept:
                accept_reasons[i] = reasoning
                print(f"Accepting step {i}: {reasoning}")
            else:
                filtered_steps.append(step_messages)
                filtered_reasons[i] = reasoning
                print(f"filtered step {i}: {reasoning}")
                print(f"step_messages: {step_messages}")
        except SyntaxError:
            step_messages = trim_tool_output(step_messages)
            print(f"{step_messages.metadata}\nCould not parse step:\n{step_messages[-1]}\n")
    return filtered_steps, filtered_reasons, accept_reasons


def load_filtered_steps_subset(steps_dir: Path) -> list[StepMessages]:
    steps = []
    for step_file in sorted(steps_dir.glob("*.xml")):
        steps.append(StepMessages.from_xml_path(step_file))
    return steps
