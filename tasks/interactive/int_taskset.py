# %%
from agent.configs import PromptConfig, AgentEngineConfig
from tasks.taskset import TaskSet
from tasks.base import BaseTask

class Task(BaseTask):
    n_variants = 10
    def __init__(self, variant: int = 0):
        super().__init__(variant)
        self._custom_name = f"task_{variant}"

tasks = [Task(i) for i in range(10)]
taskset = TaskSet(
    name="taskset",
    tasks=tasks,
    prompt_configs=PromptConfig(),
    engine_configs=AgentEngineConfig()
).repeat(3)

# %%
subset = taskset.sample(3)

for task, prompt_config, engine_config in subset:
    print(task.name)

# %%
