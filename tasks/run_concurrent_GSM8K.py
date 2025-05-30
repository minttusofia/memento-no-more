# %%
import asyncio
import os
from dotenv import load_dotenv
import nest_asyncio

print(os.getpid())
nest_asyncio.apply()
load_dotenv()

# %%
from time import time  # noqa

from agent.clients import get_client  # noqa
from batch_eval import save_results, Manager, create_batch_run_path  # noqa
import data_collection_config as dcf  # noqa

# model to evaluate
model = "v-llama3.1-70b"
client = get_client(model=model)

taskset = dcf.gsm8k_test(n_trials=3)

# %%
for i, task in enumerate(taskset.tasks):
    print(f"{i}. {task.name}: {task.task}\n")
    print("Guidelines:")
    prompt_config = taskset.prompt_configs[i]
    if prompt_config.guidelines:
        for guideline in prompt_config.guidelines:
            print("-" * 20)
            print(guideline)
    else:
        print("No guidelines")

start_t = time()
batch_run_path = create_batch_run_path(model, taskset.name)
agent_configs = taskset.get_agent_configs()

manager = Manager(
    taskset.tasks,
    agent_configs,
    batch_run_paths=[batch_run_path] * len(taskset),
    max_concurrent_tasks=10,
)


run_task = asyncio.create_task(manager.run(client))


await run_task
await manager.monitor_job


run_names, statuses, scores, agents, tasks = run_task.result()
stats = [agent.stats for agent in agents]
end_t = time()


# Print the time it took to run all tasks
print(f"Time: {int(end_t - start_t)}s")

# Calculate average score
av_score = sum([score or 0.0 for score in scores]) / len(scores)
print(f"Average score: {av_score}")

# Save aggregate results
# Use update=True to add to existing scores and stats
scores, stats_dict = save_results(run_names, scores, stats, batch_run_path, update=True)

# %%
