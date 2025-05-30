# %%
from agent.configs import AgentEngineConfig, PromptConfig
from tasks.base import BaseTask
from tasks.data_collection_config import TaskSet

taskset = TaskSet(
    name="test",
    tasks=[BaseTask()] * 3,
    prompt_configs=[PromptConfig.standard()] * 3,
    engine_configs=[AgentEngineConfig()] * 3,
)

print(taskset.n_trials)
# %%
