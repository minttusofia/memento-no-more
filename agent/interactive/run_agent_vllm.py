# %%
from dotenv import load_dotenv
import nest_asyncio

from agent import AGENT_RUN_PATH
from agent.agent import Agent
from agent.clients import vLLMClient
from agent.configs import AgentConfig
from core.messages import Message, Role

nest_asyncio.apply()

load_dotenv()

# %%
model = "llama3.1-70b"
#client = vLLMClient(model=model, chat=False)
#model = "llama3-70b"
client = vLLMClient(model=model, tokenizer="llama3.1-8b")

# %%
from agent.agent import Agent
import nest_asyncio

nest_asyncio.apply()

run_name = "test"
run_path = AGENT_RUN_PATH / run_name

config = AgentConfig(
    log_stats=False,
    stream=True,
)

agent = Agent(task="Compute '2 + 3' using Python and report the result.", run_path=run_path, config=config)

await agent.run(client=client, max_llm_calls=10)

# %%
