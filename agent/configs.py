import copy
from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Callable, Literal

from .tips import GUIDELINES
from core.utils import CustomEncoder, custom_decoder


@dataclass
class PromptConfig:
    guidelines: list[str] = None  # None means no guidelines
    tool_docs: Literal["none", "short", "long"] = "long"
    tool_docs_list: list[str] = None  # Names of tools to show the documentation for
                                      # If None, show the documentation for all tools
    monologue_format: bool = True  # Remind the monologue format before the monologue
    tool_call_format: bool = True  # Remind the tool call format before the tool call

    @classmethod
    def standard(cls):
        return cls(
            guidelines=list(GUIDELINES.values()),
            tool_docs="long",
            monologue_format=True,
            tool_call_format=True,
        )

    @classmethod
    def empty(cls):
        return cls(
            guidelines=None,
            tool_docs="none",
            monologue_format=False,
            tool_call_format=False,
        )


def get_standard_tools() -> dict[str, Callable]:
    from . import tools_python as tools
    return {
        "complete_task": tools.complete_task,
    }


@dataclass
class AgentEngineConfig:
    # These settings may affect the performance of the agent
    # Tools available to the agent: tool's name -> function
    tools: dict[str, Callable] = None  # If None, use the standard tools
    max_input_tokens: int = 8_192  # Maximum number of tokens in the input
    modify_agent: Callable = None  # Function to modify the agent or its environment

    def get_tools(self) -> dict[str, Callable]:
        return self.tools if self.tools is not None else get_standard_tools()


@dataclass
class AgentConfig:
    log_stats: bool = True
    log_status: bool = True
    prompt_config: PromptConfig = field(default_factory=PromptConfig.standard)
    engine_config: AgentEngineConfig = field(default_factory=AgentEngineConfig)
    stream: bool = True
    verbose: bool = True

    def copy(self):
        return copy.copy(self)

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(asdict(self), cls=CustomEncoder, indent=2)

    @classmethod
    def from_dict(cls, data: dict):
        data["prompt_config"] = PromptConfig(**data["prompt_config"])
        data["engine_config"] = AgentEngineConfig(**data["engine_config"])
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str, object_hook=custom_decoder)
        return cls.from_dict(data)

    @classmethod
    def from_run_path(cls, run_path: Path):
        return cls.from_json((run_path / "config.json").read_text())


class Metadata(dict):
    def to_json(self):
        new_dict = self.copy()
        for k in new_dict:
            if k == "agent_config":
                new_dict[k] = new_dict[k].to_dict()
        return json.dumps(new_dict, indent=2, cls=CustomEncoder)

    @classmethod
    def from_json(cls, s: str):
        dct = json.loads(s)
        for k in dct:
            if k == "agent_config":
                dct[k] = AgentConfig.from_dict(dct[k])
        return cls(dct)
