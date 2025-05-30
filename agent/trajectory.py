# %%
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
import json
import os
from warnings import warn

from core.utils import random_id

@dataclass
class Trajectory:
    """Trajectory holds information about the run that is needed for a rerun."""
    task: str
    return_cls_name: str = None
    input_variables: list[str] = None
    init_script: str = None
    metadata: dict = None
    half_steps: list[dict] = field(default_factory=list)
    random_suffix: str = field(default_factory=lambda: random_id(4))

    def to_dict(self) -> dict:
        return {
            "task": self.task,
            "return_cls_name": self.return_cls_name,
            "input_variables": self.input_variables,
            "init_script": self.init_script,
            "metadata": self.metadata,
            "half_steps": self.half_steps,
        }

    def next_step(self, status: str = None):
        step = defaultdict(list)
        if status:
            step["status"] = status
        self.half_steps.append(step)

    def set_response(self, txt: str):
        self.half_steps[-1]["response"] = txt

    def add_discarded(self, txt: str):
        self.half_steps[-1]["discarded"].append(txt)

    def add_feedback(self, feedback: str | dict):
        self.half_steps[-1]["feedback"].append(feedback)

    def to_json(self):
        return json.dumps(self, indent=4, default=Trajectory.serializer) + "\n"

    def save(self, basename: str, run_path=None):
        if run_path is None:
            return "Not saved."
            # run_path = AGENT_DATASET_PATH
        if not os.path.exists(run_path):
            os.makedirs(run_path)
        path = run_path / f"{basename}-{self.random_suffix}.json"
        with open(path, "w") as f:
            f.write(self.to_json())
        return path

    @classmethod
    def from_dict(cls, data: dict):
        # Backward compatibility
        if "return_cls" in data:
            data["return_cls_name"] = data.pop("return_cls")
        if "steps" in data:
            data["half_steps"] = data.pop("steps")

        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        return cls.from_dict(data)

    def get_feedbacks(self):
        f = []
        for s in self.half_steps:
            feedback = s.get("feedback", [None])[-1]
            if isinstance(feedback, dict):
                feedback = feedback["feedback"]
            f.append(feedback)
        return f

    def get_responses(self):
        return [s["response"] for s in self.half_steps]

    @staticmethod
    def serializer(x):
        if isinstance(x, Trajectory):
            return x.to_dict()
        else:
            warn(f"Object of type '{type(x)}' is not serializable", stacklevel=2)
            return "Nonserializable object: " + repr(x)

