# %%
import os
import nest_asyncio

print(os.getpid())
nest_asyncio.apply()

# %%
from agent.clients import LLMClient  # noqa
from core.messages import Message, Role  # noqa

from core.llm import LLM  # noqa

llm = LLM.from_adapter("adapters/llama3-agent/friendly-box")  # Adapt this to your needs
# llm = LLM("models/llama3-8b-instruct")
client = LLMClient(llm)

# %%
prompt = "Who are you?"
messages = [
    Message(Role.SYSTEM, prompt)
]

content, info = client.llm.call(messages, stream=True, max_new_tokens=100)
print(content)

# %%
from agent.agent import Agent
from agent.configs import AgentConfig
import nest_asyncio
from agent import AGENT_RUN_PATH

nest_asyncio.apply()

run_name = "test_run"
run_path = AGENT_RUN_PATH / f"{run_name}"

config = AgentConfig(
    log_stats=False,
    stream=True,
)

task = "Add 2 and 3 and report the result."

# task = "Create a list with random strings, sort it, and print the result."
# task = """\
# Execute the followings steps:
# 1. Create a list with random names like "John", "Alice", "Bob", etc.
# 2. Create a dictionary with the names as keys and random numbers as values.
# 3. Return the name with the highest value.
# """
# task = "Create a list with random numbers between 1 and 100 and return all numbers smaller than 50."

agent = Agent(
  task=task,
  run_path=run_path,
  config=config,
  return_cls=int,
)

await agent.run(
  client=client,
  max_llm_calls=6
)

# %%
