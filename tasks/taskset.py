from copy import deepcopy
from dataclasses import dataclass
import random
from typing import Callable

from agent.configs import AgentConfig, AgentEngineConfig, PromptConfig, get_standard_tools
from tasks.base import BaseTask

@dataclass
class TaskSet:
    name: str
    tasks: list[BaseTask]
    prompt_configs: PromptConfig | list[PromptConfig]  # After initialization, converted to a list
    engine_configs: AgentEngineConfig | list[AgentEngineConfig] = None # After initialization, converted to a list

    def __post_init__(self):
        assert isinstance(self.tasks, list), "tasks must be a list"
        self.prompt_configs = self.to_list(self.prompt_configs)
        self.engine_configs = self.to_list(self.engine_configs or AgentEngineConfig())

    def to_list(self, int_or_list: int | list[int]) -> list[int]:
        if isinstance(int_or_list, list):
            assert len(int_or_list) == len(self.tasks)
            return int_or_list
        else:
            return [int_or_list] * len(self.tasks)

    def __len__(self):
        return len(self.tasks)

    def __getitem__(self, index: int | slice):
        if isinstance(index, slice):
            # This allows taskset = taskset[:2] to get a subset
            # Use taskset[2:3] to get a taskset with one task
            return TaskSet(
                name=self.name,
                tasks=self.tasks[index],
                prompt_configs=self.prompt_configs[index],
                engine_configs=self.engine_configs[index]
            )
        else:
            return (
                self.tasks[index],
                self.prompt_configs[index],
                self.engine_configs[index]
            )

    def repeat(self, n_trials: int = 1):
        if n_trials == 1:
            return self
        new_tasks = []
        new_prompt_configs = []
        new_engine_configs = []
        for i, task in enumerate(self.tasks):
            for trial in range(n_trials):
                new_task = deepcopy(task)
                new_task.name = f"{task.name}_t{trial}"
                new_tasks.append(new_task)
                new_prompt_configs.append(self.prompt_configs[i])
                new_engine_configs.append(self.engine_configs[i])

        return TaskSet(
            name=self.name,
            tasks=new_tasks,
            prompt_configs=new_prompt_configs,
            engine_configs=new_engine_configs,
        )

    def sample(self, n: int):
        assert n <= len(self), f"Cannot sample {n} tasks from a set of {len(self)} tasks"
        indices = random.sample(list(range(len(self))), n)
        return TaskSet(
            name=self.name,
            tasks=[self.tasks[i] for i in indices],
            prompt_configs=[self.prompt_configs[i] for i in indices],
            engine_configs=[self.engine_configs[i] for i in indices],
        )

    def name_startswith(self, prefix: str):
        data = [
            tpe
            for tpe in zip(self.tasks, self.prompt_configs, self.engine_configs, strict=True)
            if tpe[0].name.startswith(prefix)
        ]
        t, p, e = map(list, zip(*data, strict=True))
        return TaskSet(self.name, t, p, e)

    def name_filter(self, filter: Callable):
        data = [
            tpe
            for tpe in zip(self.tasks, self.prompt_configs, self.engine_configs, strict=True)
            if filter(tpe[0].name)
        ]
        t, p, e = map(list, zip(*data, strict=True))
        return TaskSet(self.name, t, p, e)

    def empty_prompt(self):
        return TaskSet(
            name=self.name,
            tasks=self.tasks,
            prompt_configs=[PromptConfig.empty()] * len(self.tasks),
            engine_configs=self.engine_configs
        )

    @classmethod
    def from_tasks(cls, tasks, name="from_tasks"):
        return cls(
            name=name,
            tasks=tasks,
            prompt_configs=[PromptConfig.standard()] * len(tasks),
            engine_configs=[AgentEngineConfig()] * len(tasks)
        )

    def standard_prompt(self):
        return TaskSet(
            name=self.name,
            tasks=self.tasks,
            prompt_configs=[PromptConfig.standard()] * len(self.tasks),
            engine_configs=self.engine_configs
        )

    def standard_engine(self):
        return TaskSet(
            name=self.name,
            tasks=self.tasks,
            prompt_configs=self.prompt_configs,
            engine_configs=[AgentEngineConfig()] * len(self.tasks)
        )

    def standard_tools(self):
        for engine_config in self.engine_configs:
            engine_config.tools = get_standard_tools()

        return TaskSet(
            name=self.name,
            tasks=self.tasks,
            prompt_configs=self.prompt_configs,
            engine_configs=self.engine_configs
        )

    def get_agent_configs(self, **kwargs):
        ac_kwargs = dict(
            log_stats=False,
            log_status=False,
            stream=False,
            verbose=False,
        )
        ac_kwargs.update(kwargs or {})
        return [
            AgentConfig(
                **ac_kwargs,
                prompt_config=prompt_config,
                engine_config=engine_config,
            )
            for prompt_config, engine_config in zip(self.prompt_configs, self.engine_configs, strict=True)
        ]
