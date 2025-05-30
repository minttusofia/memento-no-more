from __future__ import annotations

import os

from . import agent as ag
from core.utils import CoreToolInterruption
from .tool_call_status import TCStatus as TCS


def complete_task_generic(agent: ag.Agent, final_report: str, return_value=None):
    """tools.complete_task(final_report: str, return_value=None)
    Complete the task and report back to the parent project. It is recommended that you do this command as the only command in the cell.
    The return_value needs to be an instance of the class requested in the task description, or an exception signalling that the task has failed.
    Example calls:
        tools.complete_task("Author names extracted successfully", dict(names=["Alice", "Bob"]))
    or
        tools.complete_task("The number of found items is attached.", 2)
    or
        tools.complete_task("The document seems to be encrypted", RuntimeError("Could not parse the document."))"""
    agent.stats.add_tool_call("complete_task")
    if not isinstance(return_value, Exception):  # Exception is always accepted
        # Make sure that the type of return_value matches return_cls_name
        return_cls_name = agent.return_cls_name
        if return_cls_name is not None:
            # Remove any possible type annotations
            return_cls_name_stripped = return_cls_name.split('[')[0]
            if not return_value.__class__.__name__ == return_cls_name_stripped:
                raise TypeError(f"Return value is not an instance of {return_cls_name}")
    agent.final_report = final_report
    agent.return_value = return_value
    raise CoreToolInterruption(TCS.COMPLETE_TASK)

def complete_task(agent: ag.Agent, final_report: str, return_value=None):
    """tools.complete_task(final_report: str, return_value: str)
    Complete the task and report the final answer. It is recommended that you do this command as the only command in the cell.
    The return_value needs to be a string.
    Example calls:
        tools.complete_task("The star rating of Perenn Bakery is", "4.5")
    or
        tools.complete_task("The meeting should be scheduled at", "9:00 AM-6:00 PM")"""
    agent.stats.add_tool_call("complete_task")
    if not isinstance(return_value, Exception):  # Exception is always accepted
        # Make sure that the type of return_value matches return_cls_name
        return_cls_name = agent.return_cls_name
        if return_cls_name is not None:
            # Remove any possible type annotations
            return_cls_name_stripped = return_cls_name.split('[')[0]
            if not return_value.__class__.__name__ == return_cls_name_stripped:
                raise TypeError(f"Return value is not an instance of {return_cls_name}")
    agent.final_report = final_report
    agent.return_value = return_value
    raise CoreToolInterruption(TCS.COMPLETE_TASK)

def officebench_complete_task(agent: ag.Agent, final_report: str, return_value=None):
    """tools.complete_task(final_report: str, return_value=None)
    Complete the task. It is recommended that you do this command as the only command in the cell.
    If the task requires providing a final answer, the return_value needs to be a string.
    Example calls:
        tools.complete_task("The event has been created to the calendar.") # This task does not require providing a final answer.
        tools.complete_task("The email subject is:", "Meeting notes") # This task requires providing a final answer.
    """
    agent.stats.add_tool_call("complete_task")
    if not isinstance(return_value, Exception):  # Exception is always accepted
        # Make sure that the type of return_value matches return_cls_name
        return_cls_name = agent.return_cls_name
        if return_cls_name is not None:
            # Remove any possible type annotations
            return_cls_name_stripped = return_cls_name.split('[')[0]
            if not return_value.__class__.__name__ == return_cls_name_stripped:
                raise TypeError(f"Return value is not an instance of {return_cls_name}")
    agent.final_report = final_report
    agent.return_value = return_value
    if agent.return_value is not None:
        os.makedirs(os.path.join(agent.run_path, "testbed/data"), exist_ok=True)
        with open(os.path.join(agent.run_path, "testbed/data/answer.txt"), "w") as f:
            f.write(str(agent.return_value))
    raise CoreToolInterruption(TCS.COMPLETE_TASK)
