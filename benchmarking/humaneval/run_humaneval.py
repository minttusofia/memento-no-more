# %%
from benchmarking.humaneval.humaneval_utils import humaneval, save_results
from agent.clients import get_client
from core.messages import Message, Role
from core.utils import get_model_name

from collections import defaultdict
from pprint import pprint
import nest_asyncio
nest_asyncio.apply()

# %%
client_model = "vm-agent-llama3.1-70b/1007_pureed-tint-2"
model_name, base_model_name = get_model_name(client_model)
client = get_client(model=client_model)

async def propose_solution(task_prompt):
    "This method uses the client to generate a solution given a task prompt."

    messages = [
        Message(Role.USER, f"Your task is to implement full code that starts with the following:\n```{task_prompt}```\nStrictly follow the XML-like format below:\n<python>\n# copy of the provided code snippet followed by your completion and nothing else\n</python>"),
    ]
    completion = await client.call(messages, stream=False)
    completion = completion.removeprefix("<python>").removesuffix("</python>") 
    return(completion)

# %%

# Perform the benchmark
passed, results, solutions, errors = await humaneval( # type: ignore
    propose_solution=propose_solution,
    k=5,
    verbose=True
)

# Print results
adapter_column_width = len(model_name)
header = f"| {'Adapter'.ljust(adapter_column_width)} || {' | '.join([f'pass@{k+1}' for k in range(len(passed))])} |"
result = f"| {model_name.ljust(adapter_column_width)} || {' | '.join([f'{passed_at_k:.3f}' for passed_at_k in passed])} |"

print(header)
print(result)

# %%
# Save results to evaluation records

save_results(
    model_name,
    passed,
    results,
    solutions,
    errors,
    base_model_name=base_model_name
)

# %%
#  ANALYSIS OF THE RESULTS

## Print error counts
error_counts = {}
error_tasks = defaultdict(list)
for id, error_list in errors.items():
    for trial, error in enumerate(error_list):
        exception_type = str(type(error))
        if exception_type != "<class 'NoneType'>":
            error_counts[exception_type] = error_counts.get(exception_type, 0) + 1
            error_tasks[exception_type].append((id, trial))

print("Error counts:")
pprint(error_counts)

error_type = "<class 'SyntaxError'>"
print(f"\nTasks and trials with {error_type}")
pprint(error_tasks[error_type])

# Note: if you see NameErrors, it is likely that the LLM omitted the import statements when generating the solution. This can introduce an unwanted signal into the metrics. We would recommend investigating further.

# %%
## Investigation of individual failed tasks

failed_tasks = [id for id, res in results.items() if not any(res)]
print(f"Total number of failed tasks: {len(failed_tasks)}\n")

i = 0
# id = failed_tasks[i]
id = 'HumanEval-15'
print(f"Investigating task {id}:\n")
print("ERRORS:\n^^^^^^^")
for er in errors[id]:
    print(er)

print("\nSOLUTIONS:\n^^^^^^^^^^")
for sol in solutions[id]:
    print(sol, "\n----------\n")

# %%
