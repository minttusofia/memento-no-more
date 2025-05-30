# %%
from agent.agent import MessageBuilder, ExerciseMessageBuilder
from agent.configs import AgentConfig

agent_config = AgentConfig()

msg_builder = MessageBuilder(agent_config)
msg = msg_builder.guidelines_message()
print(msg)
print(msg.tags)

# %%
exercise_msg_builder = ExerciseMessageBuilder(agent_config)
msg = exercise_msg_builder.guidelines_message()
print(msg)
print(msg.tags)

# %%
msg = msg_builder.tool_docs_message()
print(msg)
print(msg.tags)

# %%
msg = exercise_msg_builder.tool_docs_message()
print(msg)
print(msg.tags)

# %%
msg = msg_builder.monologue_instruction_message()
print(msg)
print(msg.tags)

# %%
msg = exercise_msg_builder.monologue_instruction_message()
print(msg)
print(msg.tags)

# %%
msg = msg_builder.tool_call_instruction_message()
print(msg)
print(msg.tags)

# %%
msg = exercise_msg_builder.tool_call_instruction_message()
print(msg)
print(msg.tags)

