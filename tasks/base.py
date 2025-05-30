import os
import re
from pathlib import Path
import traceback
from typing import Any, Type

from agent.agent import Agent

class BaseTask:
    input_variables: dict[str, Any] = None
    env: dict = None  # Environment variables
    task: str = None
    budget: int = 10
    n_variants: int = 1  # Number of task variants
    return_cls_name: str = None
    init_script: str = None
    _custom_name: str = None

    def __init__(self, variant: int = 0):
        assert 0 <= variant < self.n_variants, f"Unknown variant: {variant}"
        self.variant = variant

    def __enter__(self):
        self.dir_before = Path.cwd()
        os.chdir(AGENT_HOME)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            traceback.print_tb(exc_tb)
        os.chdir(self.dir_before)

    def get_prompt_config(self):
        """Return a prompt configuration for the agent."""
        raise NotImplementedError("get_prompt_config method must be implemented in derived classes")

    def evaluate(self, agent: Agent, verbose: bool = False) -> tuple[float, str]:
        # Return a score and a report
        raise NotImplementedError("evaluate method must be implemented in derived classes")

    @classmethod
    def generate_variants(cls, **kwargs):
        return [cls(variant, **kwargs) for variant in range(cls.n_variants)]

    @property
    def default_name(self):
        name = camel_to_snake(self.__class__.__name__)
        if not name.startswith("t_"):
            name = "t_" + name

        if name.endswith("_task"):
            name = name[:-5]

        name += f"_{self.variant}"
        return name

    @property
    def name(self):
        return self._custom_name or self.default_name

    @name.setter
    def name(self, value):
        self._custom_name = value


AGENT_HOME = Path(__file__).parent / "home"


def camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower()
