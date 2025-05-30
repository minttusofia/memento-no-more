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
import data_collection_config_ToolQA_generalization as dcf_g  # noqa

# baseline / teacher / trained model to evaluate or collect data with
model = "v-llama3.1-70b"  # v-llama3.1-70b | deepseek-chat | gpt-4o | vm-<PROJECT_NAME>/<RUN_NAME>
client = get_client(model=model)

# the model for which combined hints were optimized (if use_combined_guidelines=True)
hints_model = model[2:] if model.startswith("v-") else model  # llama3.1-70b | deepseek-chat | gpt-4o

n_trials = 3


# Option I. Collect training data with task-specific teacher
taskset = dcf.table_task(db_variant='airbnb', level='train', all_tools=False, number_of_questions=100, format_tips=True, basic_normalization=True, use_generic_task_description=True, n_trials=n_trials)
# taskset = dcf.table_task(db_variant='coffee', level='train', all_tools=False, number_of_questions=139, format_tips=True, basic_normalization=True, use_generic_task_description=True, n_trials=n_trials)
# taskset = dcf.table_task(db_variant='flights', level='train', all_tools=False, number_of_questions=120, format_tips=True, basic_normalization=True, use_generic_task_description=True, n_trials=n_trials)
# taskset = dcf.table_task(db_variant='yelp', level='train', all_tools=False, number_of_questions=101, format_tips=True, basic_normalization=True, use_generic_task_description=True, n_trials=n_trials)
# taskset = dcf.graph_task(level='train', all_tools=False, number_of_questions=104, use_generic_task_description=True, n_trials=n_trials)
# taskset = dcf.text_task(level='train', all_tools=False, number_of_questions=91, use_generic_task_description=True, n_trials=n_trials)

# Option II. Evaluate task-specific teacher on test tasks (hints optimized on test tasks)
# taskset = dcf.table_task(db_variant='airbnb', level='test', all_tools=False, number_of_questions=51, format_tips=True, basic_normalization=True, use_generic_task_description=True, n_trials=n_trials)
# taskset = dcf.table_task(db_variant='coffee', level='test', all_tools=False, number_of_questions=71, format_tips=True, basic_normalization=True, use_generic_task_description=True, n_trials=n_trials)
# taskset = dcf.table_task(db_variant='flights', level='test', all_tools=False, number_of_questions=60, format_tips=True, basic_normalization=True, use_generic_task_description=True, n_trials=n_trials)
# taskset = dcf.table_task(db_variant='yelp', level='test', all_tools=False, number_of_questions=59, format_tips=True, basic_normalization=True, use_generic_task_description=True, n_trials=n_trials)
# taskset = dcf.graph_task(level='test', all_tools=False, number_of_questions=59, use_generic_task_description=True, n_trials=n_trials)
# taskset = dcf.text_task(level='test', all_tools=False, number_of_questions=42, use_generic_task_description=True, n_trials=n_trials)

# Option IIIa. Evaluate without any guidance - train tasks
# taskset = dcf.table_task_test(db_variant='airbnb', level='train', number_of_questions=100, tools='none', use_combined_guidelines=False, n_trials=n_trials)
# taskset = dcf.table_task_test(db_variant='coffee', level='train', number_of_questions=139, tools='none', use_combined_guidelines=False, n_trials=n_trials)
# taskset = dcf.table_task_test(db_variant='flights', level='train', number_of_questions=120, tools='none', use_combined_guidelines=False, n_trials=n_trials)
# taskset = dcf.table_task_test(db_variant='yelp', level='train', number_of_questions=101, tools='none', use_combined_guidelines=False, n_trials=n_trials)
# taskset = dcf.graph_task_test(level='train', number_of_questions=104, tools='none', use_combined_guidelines=False, n_trials=n_trials)
# taskset = dcf.text_task_test(level='train', number_of_questions=91, tools='none', use_combined_guidelines=False, n_trials=n_trials)

# Option IIIb. Evaluate without any guidance - test tasks
# taskset = dcf.table_task_test(db_variant='airbnb', level='test', number_of_questions=51, tools='none', use_combined_guidelines=False, n_trials=n_trials)
# taskset = dcf.table_task_test(db_variant='coffee', level='test', number_of_questions=71, tools='none', use_combined_guidelines=False, n_trials=n_trials)
# taskset = dcf.table_task_test(db_variant='flights', level='test', number_of_questions=60, tools='none', use_combined_guidelines=False, n_trials=n_trials)
# taskset = dcf.table_task_test(db_variant='yelp', level='test', number_of_questions=59, tools='none', use_combined_guidelines=False, n_trials=n_trials)
# taskset = dcf.graph_task_test(level='test', number_of_questions=59, tools='none', use_combined_guidelines=False, n_trials=n_trials)
# taskset = dcf.text_task_test(level='test', number_of_questions=42, tools='none', use_combined_guidelines=False, n_trials=n_trials)

# Option IV. Evaluate with combined hints
# taskset = dcf.table_task_test(db_variant='airbnb', level='test', number_of_questions=51, tools='all-long', use_combined_guidelines=True, combined_hints_model=hints_model, n_trials=n_trials)
# taskset = dcf.table_task_test(db_variant='coffee', level='test', number_of_questions=71, tools='all-long', use_combined_guidelines=True, combined_hints_model=hints_model, n_trials=n_trials)
# taskset = dcf.table_task_test(db_variant='flights', level='test', number_of_questions=60, tools='all-long', use_combined_guidelines=True, combined_hints_model=hints_model, n_trials=n_trials)
# taskset = dcf.table_task_test(db_variant='yelp', level='test', number_of_questions=59, tools='all-long', use_combined_guidelines=True, combined_hints_model=hints_model, n_trials=n_trials)
# taskset = dcf.graph_task_test(level='test', number_of_questions=59, tools='all-long', use_combined_guidelines=True, combined_hints_model=hints_model, n_trials=n_trials)
# taskset = dcf.text_task_test(level='test', number_of_questions=42, tools='all-long', use_combined_guidelines=True, combined_hints_model=hints_model, n_trials=n_trials)


### Seen-unseen question templates split:

# Option V. Collect training data with task-specific teacher, holding out unseen tasks
# taskset = dcf_g.table_task_generalization(db_variant='airbnb', level='train-seen-questions', all_tools=False, number_of_questions=98, format_tips=True, basic_normalization=True, use_generic_task_description=True, n_trials=n_trials)
# taskset = dcf_g.table_task_generalization(db_variant='coffee', level='train-seen-questions', all_tools=False, number_of_questions=148, format_tips=True, basic_normalization=True, use_generic_task_description=True, n_trials=n_trials)
# taskset = dcf_g.table_task_generalization(db_variant='flights', level='train-seen-questions', all_tools=False, number_of_questions=126, format_tips=True, basic_normalization=True, use_generic_task_description=True, n_trials=n_trials)
# taskset = dcf_g.table_task_generalization(db_variant='yelp', level='train-seen-questions', all_tools=False, number_of_questions=111, format_tips=True, basic_normalization=True, use_generic_task_description=True, n_trials=n_trials)
# taskset = dcf_g.graph_task_generalization(level='train-seen-questions', all_tools=False, number_of_questions=110, format_tips=True, basic_normalization=True, use_generic_task_description=True, n_trials=n_trials)
# taskset = dcf_g.text_task_generalization(level='train-seen-questions', all_tools=False, number_of_questions=72, format_tips=True, basic_normalization=True, use_generic_task_description=True, n_trials=n_trials)

# Option VIa. Evaluate on unseen tasks without any guidance - train tasks
# taskset = dcf_g.table_task_test_generalization(db_variant='airbnb', level='train-seen-questions', number_of_questions=98, tools='none', use_combined_guidelines=False, n_trials=n_trials)
# taskset = dcf_g.table_task_test_generalization(db_variant='coffee', level='train-seen-questions', number_of_questions=148, tools='none', use_combined_guidelines=False, n_trials=n_trials)
# taskset = dcf_g.table_task_test_generalization(db_variant='flights', level='train-seen-questions', number_of_questions=126, tools='none', use_combined_guidelines=False, n_trials=n_trials)
# taskset = dcf_g.table_task_test_generalization(db_variant='yelp', level='train-seen-questions', number_of_questions=111, tools='none', use_combined_guidelines=False, n_trials=n_trials)
# taskset = dcf_g.graph_task_test_generalization(level='train-seen-questions', number_of_questions=110, tools='none', use_combined_guidelines=False, n_trials=n_trials)
# taskset = dcf_g.text_task_test_generalization(level='train-seen-questions', number_of_questions=72, tools='none', use_combined_guidelines=False, n_trials=n_trials)

# Option VIb. Evaluate on unseen tasks without any guidance - test tasks
# taskset = dcf_g.table_task_test_generalization(db_variant='airbnb', level='test-unseen-questions', number_of_questions=59, tools='none', use_combined_guidelines=False, n_trials=n_trials)
# taskset = dcf_g.table_task_test_generalization(db_variant='coffee', level='test-unseen-questions', number_of_questions=68, tools='none', use_combined_guidelines=False, n_trials=n_trials)
# taskset = dcf_g.table_task_test_generalization(db_variant='flights', level='test-unseen-questions', number_of_questions=60, tools='none', use_combined_guidelines=False, n_trials=n_trials)
# taskset = dcf_g.table_task_test_generalization(db_variant='yelp', level='test-unseen-questions', number_of_questions=55, tools='none', use_combined_guidelines=False, n_trials=n_trials)
# taskset = dcf_g.graph_task_test_generalization(level='test-unseen-questions', number_of_questions=58, tools='none', use_combined_guidelines=False, n_trials=n_trials)
# taskset = dcf_g.text_task_test_generalization(level='test-unseen-questions', number_of_questions=64, tools='none', use_combined_guidelines=False, n_trials=n_trials)

# Option VII. Evaluate on unseen tasks with combined hints
# taskset = dcf_g.table_task_test_generalization(db_variant='airbnb', level='test-unseen-questions', number_of_questions=59, tools='all-long', use_combined_guidelines=True, combined_hints_model=hints_model, n_trials=n_trials)
# taskset = dcf_g.table_task_test_generalization(db_variant='coffee', level='test-unseen-questions', number_of_questions=68, tools='all-long', use_combined_guidelines=True, combined_hints_model=hints_model, n_trials=n_trials)
# taskset = dcf_g.table_task_test_generalization(db_variant='flights', level='test-unseen-questions', number_of_questions=60, tools='all-long', use_combined_guidelines=True, combined_hints_model=hints_model, n_trials=n_trials)
# taskset = dcf_g.table_task_test_generalization(db_variant='yelp', level='test-unseen-questions', number_of_questions=55, tools='all-long', use_combined_guidelines=True, combined_hints_model=hints_model, n_trials=n_trials)
# taskset = dcf_g.graph_task_test_generalization(level='test-unseen-questions', tools='all-long', number_of_questions=58, use_combined_guidelines=True, combined_hints_model=hints_model, n_trials=n_trials)
# taskset = dcf_g.text_task_test_generalization(level='test-unseen-questions', tools='all-long', number_of_questions=64, use_combined_guidelines=True, combined_hints_model=hints_model, n_trials=n_trials)


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
    max_concurrent_tasks=8,
)
#%%


run_task = asyncio.create_task(manager.run(client, debug=False))


await run_task
await manager.monitor_job


# %%
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
