# %%
import nest_asyncio
from agent.clients import OpenAIClient
from core.messages import Message, Role
from agent.stats import Stats

nest_asyncio.apply()

client = OpenAIClient(model="gpt-3.5-turbo")
stats = Stats()
messages = [
    Message(Role.USER, "What are the colours of the rainbow?")
]
response = await client.call(messages, stats=stats, stream=True)

print(stats)
# %%
stats = Stats()
response = await client.call(messages, stats=stats)
print(response)
print(stats)

# %%
import nest_asyncio
from agent.clients import get_client
from core.messages import Message, Role
from agent.stats import Stats

nest_asyncio.apply()

messages = [
    Message(Role.USER, "What are the colours of the rainbow?")
]

client = get_client("vm-llama3-agent/senior-forest")
stats = Stats()
response = await client.call(messages, stats=stats)
print(response)
print(stats)

# %%
stats = Stats()
response = await client.call(messages, stats=stats, stream=True)
print(stats)

# %%
import nest_asyncio
from agent.clients import vLLMClient
from core.messages import Message, Role
from agent.stats import Stats

nest_asyncio.apply()

model = "meta-llama/Meta-Llama-3-8B-Instruct"
#base_url = "http://nid005023:8000/v1"
base_url = "http://localhost:8000/v1"

client = vLLMClient(model, base_url, chat=False)

# %%
messages = [
    Message(Role.USER, "What are the colours of the rainbow?")
]

stats = Stats()
response = await client.call(messages, stats=stats, stream=True)
print(response)
print(stats)

# %%
from core.llm import ResponseFormat  # noqa

messages = [
    Message(Role.USER, """\
What are the colours of the rainbow? Please respond in the following format:
<inner_monologue>
Your thoughts hidden from the user.
</inner_monologue>
Your response visible to the user.
"""
)
]

stats = Stats()
#response = await client.call(messages, stats=stats, stream=True)
response = await client.call(messages, stats=stats, stream=True, response_format=ResponseFormat.MONOLOGUE)
print(response)
print(stats)

# %%
from agent.clients import LLMClient
from core.llm import LLM
from core.messages import Message, Role

llm = LLM("llama3-8b")
client = LLMClient(llm)

messages = [
    Message(Role.USER, "What are the colours of the rainbow?")
]

# %%
response = await client.call(messages, stream=True)

# %%
print(response)

# %%
