# %%
from agent.agent import Agent
import nest_asyncio
from agent.clients import MockClient
from agent import AGENT_RUN_PATH
from agent.configs import AgentConfig

nest_asyncio.apply()

# %%
# Test init_script and return_cls_name
from dataclasses import dataclass  # noqa

run_name = "test_run"
run_path = AGENT_RUN_PATH / run_name

config = AgentConfig(log_stats=False)

init_script = """\
from dataclasses import dataclass

@dataclass
class ReturnValue:
    result: int

print("Initialization complete")
12**3 + 1**3, 10**3 + 9**3  # Testing cell output
"""

agent = Agent(
    task="Add 2 and 3 and return the result with return_cls.",
    run_path=run_path,
    config=config,
    init_script=init_script,
    return_cls_name="ReturnValue",
)

responses = [
"I will add 2 and 3.",
#
"""<run_ipython>
result = 2 + 3
result  # Testing cell output
</run_ipython>""",
###
"I will raise an exception.",
#
"""<run_ipython>
raise Exception("This is an exception")
</run_ipython>""",
###
"Let's return the result as instructed.",
#
"""<run_ipython>
tools.complete_task("The result of adding 2 and 3 is 5.", ReturnValue(result=result))
</run_ipython>""",
]
client = MockClient(responses)

await agent.run(
  client=client,
  max_llm_calls=10
)

# %%
run_name = "test_run"
run_path = AGENT_RUN_PATH / run_name

config = AgentConfig(log_stats=False)

agent = Agent(
  task="Test complete_task.",
  run_path=run_path,
  config=config,
)
print(agent)

responses = [
"I will try to complete the task and detect if it succeeded.",
#
"""<run_ipython>
interrupted = True
tools.complete_task("PERFECT")
interrupted = False
</run_ipython>""",
###
"I really shouldn't be here...",
#
"""<run_ipython>
tools.complete_task("process_tool_call did not properly react to tools.complete_task")
</run_ipython>""",
]
client = MockClient(responses)

await agent.run(
    client=client,
    max_llm_calls=10
)

if not agent.workspace.get_variable("interrupted"):
    print("ERROR: it looks like complete_task did not interrupt the execution of run_ipython")
elif agent.final_report != "PERFECT":
    print("ERROR: It looks like complete_task failed.")
    print(agent.final_report)

# %%
agent = Agent(
  task="Test detection of input function.",
  run_path=AGENT_RUN_PATH / "test_run",
  config=AgentConfig(log_stats=False),
  return_cls_name=None,
)

responses = [
"Let's use input.",
#
"""<run_ipython>
input("Please enter something: ")
</run_ipython>""",
###
"Next, let's hide it in a function.",
#
"""<run_ipython>
def get_user_input():
    return input("Please enter something: ")

get_user_input()
</run_ipython>""",
###
"Next, let's hide it a bit more.",
#
"""<run_ipython>
ask_user = input

ask_user("Please enter something: ")
</run_ipython>""",
###
"Let's make a syntax error.",
#
"""<run_ipython>
input("Please enter something: ")
</run_ipython>""",
###
"Let's finish this",
#
"""<run_ipython>
tools.complete_task("Returning.", None)
</run_ipython>"""
]
client = MockClient(responses)

await agent.run(
  client=client,
  max_llm_calls=10
)

# %%
run_name = "test_run"
run_path = AGENT_RUN_PATH / run_name

config = AgentConfig(log_stats=True)

agent = Agent(
  task="Test IPython outputs",
  run_path=run_path,
  config=config,
  return_cls_name=None,
)

responses = [
"Let's print and try to output directly something",
#
"""<run_ipython>
print("Hello world!")
[3, 1, 4]  # This is the output
</run_ipython>""",
###
"Next, let's see how the stderr looks like",
#
"""<run_ipython>
import sys
print("This goes to stdout")
print("This goes to stderr", file=sys.stderr)
raise Exception("This goes to exception")
</run_ipython>""",
#
"Let's finish this",
#
"""<run_ipython>
tools.complete_task("Yes, it worked.", None)
</run_ipython>"""
]
client = MockClient(responses)

await agent.run(
  client=client,
  max_llm_calls=10
)

# %%
