"""Utilities for reprompting a client with existing step data."""
# %%
import asyncio
from typing import Callable, Iterable
from tqdm import tqdm

from agent.agent import MessageBuilder
from agent.clients import BaseClient, ResponseFormat
from core.steps import StepMessages
from core.tags import Tag
from core.messages import Message, Role

from .xml_trajectory import monologue_prompt_from_step


async def parallel_map_with_limit(func: Callable, iterable: Iterable, max_concurrent: int):
    semaphore = asyncio.Semaphore(max_concurrent)

    async def sem_task(item):
        async with semaphore:
            return await func(item)

    tasks = [asyncio.create_task(sem_task(item)) for item in iterable]
    return await asyncio.gather(*tasks)


async def call_client_on_monologue_and_ipython_steps(
    steps: list[StepMessages],
    client: BaseClient,
    max_concurrent: int = 48,
) -> list[StepMessages]:
    new_steps = [monologue_prompt_from_step(step_messages) for step_messages in steps]
    
    async def call(new_steps):
        return await client.call(new_steps, response_format=ResponseFormat.MONOLOGUE)
    
    if max_concurrent and max_concurrent > 1:
        responses = await parallel_map_with_limit(call, new_steps, max_concurrent)
    else:
        responses = [await call(step_messages) for step_messages in tqdm(new_steps)]
    
    for i, response in enumerate(responses):
        new_steps[i].append(Message(content=response, role=Role.AI, tags={Tag.MONOLOGUE}))

        message_builder = MessageBuilder(steps[i].metadata["agent_config"])
        message = message_builder.tool_call_instruction_message()
        new_steps[i].append(message)

    async def call(new_steps):
        return await client.call(new_steps, response_format=ResponseFormat.IPYTHON)
    if max_concurrent and max_concurrent > 1:
        responses = await parallel_map_with_limit(call, new_steps, max_concurrent)
    else:
        responses = [await call(step_messages) for step_messages in tqdm(new_steps)]

    for i, response in enumerate(responses):
        new_steps[i].append(Message(content=response, role=Role.AI, tags={Tag.TOOL_CALL}))
    return new_steps


