# %%
from dotenv import load_dotenv
import nest_asyncio

from agent import AGENT_RUN_PATH
from agent.agent import Agent
from agent.clients import ClaudeClient
from agent.configs import AgentConfig

nest_asyncio.apply()

load_dotenv()

# %%
model = "claude-3-haiku-20240307"
# model = "claude-3-sonnet-20240229"
# model = "claude-3-opus-20240229"
client = ClaudeClient(model=model)

run_name = "test_run"
run_path = AGENT_RUN_PATH / run_name

config = AgentConfig(
    log_stats=False,
    stream=True,
)

agent = Agent(task="Compute '2 + 3' using Python and report the result.", run_path=run_path, config=config)

success = await agent.run(client=client, max_llm_calls=10)

# %%
