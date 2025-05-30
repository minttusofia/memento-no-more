# %%
from dotenv import load_dotenv
import nest_asyncio

from agent import AGENT_RUN_PATH
from agent.agent import Agent
from agent.clients import OpenAIClient
from agent.configs import AgentConfig, PromptConfig, AgentEngineConfig
from agent.tips import GUIDELINES
import agent.tools_python as tools

nest_asyncio.apply()

load_dotenv()

# %%
client = OpenAIClient(
    #model="gpt-3.5-turbo"
    model="gpt-4o-mini"
    # model="gpt-4-1106-preview"
    # model="gpt-4-0125-preview"
)

prompt_config = PromptConfig(
    guidelines=[GUIDELINES["response_format"]],
    tool_docs="long",
)
engine_config = AgentEngineConfig(
    tools={"complete_task": tools.complete_task},
)

config = AgentConfig(
    log_stats=False,
    stream=True,
    prompt_config=prompt_config,
    engine_config=engine_config,
)

agent = Agent(
    task="Compute '2 + 3' using Python and report the result.",
    run_path=AGENT_RUN_PATH / "test",
    config=config,
    return_cls_name="int",
)

success = await agent.run(client=client, max_llm_calls=10)
print(agent.return_value)

# %%
