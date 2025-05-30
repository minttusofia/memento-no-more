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
from tasks.batch_eval import save_results, Manager, create_batch_run_path  # noqa
import tasks.t_OfficeBench.data_collection_config as dcf  # noqa

# baseline / teacher / trained model to evaluate or collect data with
model = "v-llama3.1-70b"  # v-llama3.1-70b | deepseek-chat | gpt-4o | vm-<PROJECT_NAME>/<RUN_NAME>
client = get_client(model=model)

# the model for which combined hints were optimized (if use_combined_guidelines=True)
hints_model = model[2:] if model.startswith("v-") else model  # llama3.1-70b | deepseek-chat | gpt-4o

# n_trials = 4 when collecting training data with task-specific teacher; n_trials = 3 when performing evaluation
n_trials = 4

# Optionally run a subset of tasks by setting num_apps_only or task_index in dcf.officebench
# e.g. `num_apps_only=1` or `task_index=[('1-1', '0'), ('1-1', '1'), ('1-1', '2')]`

# Option I. Collect training data with task-specific teacher
taskset = dcf.officebench(
    level='train',
    n_trials=n_trials,
    guidance='full',
    toolset='relevant',
)

# Option II. Evaluate task-specific teacher on test tasks (hints optimized on test tasks)
# taskset = dcf.officebench(
#     level='test',
#     n_trials=n_trials,
#     guidance='full',
#     toolset='relevant',
# )

# Option IIIa. Evaluate without any guidance - train tasks
# taskset = dcf.officebench(
#     level='train',
#     n_trials=n_trials,
#     guidance='none',
# )

# Option IIIb. Evaluate without any guidance - test tasks
# taskset = dcf.officebench(
#     level='test',
#     n_trials=n_trials,
#     guidance='none',
# )

# Option IV. Evaluate with combined hints
# taskset = dcf.officebench(
#     level='test',
#     n_trials=n_trials,
#     use_combined_hints=True,
#     combined_hints_model=hints_model,
# )

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

# %%

start_t = time()
batch_run_path = create_batch_run_path(model, taskset.name)
run_paths = [batch_run_path] * len(taskset)

for i, task in enumerate(taskset.tasks):
    run_path = run_paths[i] / task.name
    task.input_variables["data_path"] = str(run_path) + "/testbed/data"


agent_configs = taskset.get_agent_configs()

manager = Manager(
    taskset.tasks,
    agent_configs,
    batch_run_paths=run_paths,
    max_concurrent_tasks=8,
)


run_task = asyncio.create_task(manager.run(client, debug=False))


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
