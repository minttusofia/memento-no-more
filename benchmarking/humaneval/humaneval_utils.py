from core.utils import stream_jsonl
from agent import AGENT_DATASET_PATH
from benchmarking.humaneval import HUMANEVAL_PATH

from typing import Callable, Awaitable, Tuple
import sys
import os
import time
from datetime import datetime
import json
import ast
import asyncio
import contextlib
import signal

def augment_asserts(code_str):
    """
    This method takes a string containing Python code and improves assets statements found within.
    Assert statements are augmented by adding the assert condition as the failure message, if no custom message is already provided.
    """
    class AssertAugmenter(ast.NodeTransformer):
        def __init__(self, source):
            self.source = source

        def visit_Assert(self, node):
            if node.msg is None:
                condition_source = ast.get_source_segment(self.source, node.test)
                if condition_source is None:
                    # Fallback in case source segment is not available
                    condition_source = ast.unparse(node.test)
                node.msg = ast.Constant(condition_source)
            return node

    tree = ast.parse(code_str)
    augmenter = AssertAugmenter(code_str)
    augmenter.visit(tree)
    ast.fix_missing_locations(tree) # fix locations and line numbers
    modified_code = ast.unparse(tree)
    return modified_code

# Borrowed from HumanEval github
@contextlib.contextmanager
def time_limit(seconds: float):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")
    signal.setitimer(signal.ITIMER_REAL, seconds)
    signal.signal(signal.SIGALRM, signal_handler)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)

class TimeoutException(Exception):
    pass

def evaluate_solution(
        task: dict,
        solution_candidate:str,
        augment_test_code: bool=True,
        timeout: int = 30,
    ) -> Tuple[bool, Exception | None]:
    "Evaluates a proposed solution candidate on provided tests. Returns whether the candidate passed the tests along with an exception if one was encountered."
    original_stdout = sys.stdout
    try:
        sys.stdout = open(os.devnull, 'w')
        temp_namespace = {}
        with time_limit(timeout):
            test = task['test']
            if augment_test_code:
                test = augment_asserts(test)
            exec(solution_candidate, temp_namespace)
            exec(test, temp_namespace)
            exec(f"check({task['entry_point']})", temp_namespace)
        return True, None
    except Exception as e:
        return False, e
    finally:
        sys.stdout = original_stdout

async def process_task(
        propose_solution: Callable[[str], str],
        task: dict,
        semaphore: asyncio.Semaphore,
        k: int,
        continuation_only: bool = False,
        verbose: bool = False,
        augment_test_code: bool = True,
        timeout: float = 30,
    ):
    "Handles generating and evaluating solutions for one task over k trials."
    try:
        async with semaphore:
            task_prompt = task['prompt']
            task_results = [None] * k
            task_solutions = [None] * k
            task_errors = [None] * k
            for trial in range(k):
                trial_solution = await propose_solution(task_prompt)
                if continuation_only:
                    trial_solution = task_prompt + trial_solution
                trial_result, trial_error = evaluate_solution(
                    task, trial_solution,
                    augment_test_code,
                    timeout=timeout,
                )
                task_results[trial] = trial_result
                task_solutions[trial] = trial_solution
                task_errors[trial] = trial_error

            if verbose:
                print(f"Task {task['task_id'].ljust(12)}:", " NOT " if not any(task_results) else "", "completed")

            return task_results, task_solutions, task_errors
    except asyncio.CancelledError:
        if verbose:
            print(f"Task {task['task_id']} cancelled.")
        return None, None, None
    
def pass_at_k_estimates(outcomes: list[bool]) -> list[float]:
    """
    Compute estimates of pass@k probabilities based on experimental results.
    
    Args:
    - outcomes (list[bool]): independent binary outcomes of an experiment
    
    Return:
    - list[float]: list of probabilities of finding at least one success when picking k elements from the list of outcomes."""

    n_trials = len(outcomes)
    success_rate = sum(outcomes) / n_trials
    pass_at_k = [(1 - (1-success_rate)**(k+1)) for k in range(n_trials)]
    return pass_at_k

async def humaneval(
        propose_solution: Callable[[str], Awaitable[str]],
        k: int = 1,
        continuation_only=False,
        max_concurrent_tasks: int = 20,
        timeout: float = 30,
        augment_test_code=True,
        verbose=False, 
    ) -> Tuple[list, dict, dict, dict]:
    """
    Performs the HumanEval benchmark using the Python version of the dataset.

    Args:
        propose_solution (Callable[[str], Awaitable[str]]): an async method for generating a complete method implementation.
        k (int): if k > 1, for each task, k independent trials are run. If one is successful, the task is considered solved.
        continuation_only (bool): if False, the proposed solution string is presumed to contain the full implementation, including the task prompt. Otherwise, it is presumed to be the continuation of the task prompt.
        max_concurrent_tasks (int): max number of tasks evaluated at the same time.
        timeout (float): how long to wait before giving up on evaluating a trial.
        augment_test_code (bool): if True, the automated test will be augmented with assert messages, making it easier to see how the solutions failed
        verbose (bool): if True, test results of each task will be printed to stdout.

    Returns:
        list[float]: List of length k containing pass@k metric values. Each value corresponds to the estimated proportion of tasks that were solved in at least one of k trials.
        dict[str, list[bool]]: A dict that uses task IDs as keys and contains a list of binary outcomes for each trial of corresponding task.
        dict[str, list[str]]: A dict that uses task IDs as keys and contains a list of solution candidates generated for each trial of corresponding task.
        dict[str, list[Exception | None]]: A dict that uses task IDs as keys and contains a list of exceptions occurred during each trial of corresponding task.
    """

    if k < 1:
        raise ValueError("k cannot be less than 1")

    # Load dataset
    dataset_path = str(HUMANEVAL_PATH)
    tasks = list(stream_jsonl(dataset_path))

    # Remove slashes from task IDs
    for task in tasks:
        task['task_id'] = task["task_id"].replace("/", "-")

    # Start jobs for handling tasks
    semaphore = asyncio.Semaphore(max_concurrent_tasks)
    start = time.time()
    jobs = [process_task(
        propose_solution=propose_solution,
        task=task,
        semaphore=semaphore,
        k=k,
        continuation_only=continuation_only,
        verbose=verbose,
        augment_test_code=augment_test_code,
        timeout=timeout,
    ) for task in tasks]

    # Await completion of all jobs
    job_results = await asyncio.gather(*jobs, return_exceptions=True)
    # print(job_results)
    if verbose:
        total_time = time.time() - start
        print(f"Benchmarking took {total_time:.2f} seconds.")

    # Write results to output dicts
    results: dict[str, list[bool]] = {}
    solutions: dict[str, list[str]] = {}
    errors: dict[str, list[str]] = {}
    for task, job_result in zip(tasks, job_results, strict=True):
        task_id = task['task_id']
        results[task_id], solutions[task_id], errors[task_id] = job_result

    # Calculate pass@k metrics
    pass_at_k = []
    pass_at_k_tasks = [pass_at_k_estimates(results_task) for results_task in results.values()]
    for i in range(k):
        pass_at_k.append(sum([estimates[i] for estimates in pass_at_k_tasks]) / len(tasks))

    return pass_at_k, results, solutions, errors

def save_results(model_name, pass_at_k, results, solutions, errors, base_model_name=None):
    """
    Saves the benchmarking results in the following format:

    <model_name>/<date>_<time>_human_eval/
    ├── scores_humaneval.json               # pass@k metrics
    └── task_outputs/                       # results, solutions, errors for each task
        ├── HumanEval-0.json
        ├── HumanEval-1.json
        └── ...
    """

    current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
    folder_name = f"{current_time}_human_eval"
    output_folder = AGENT_DATASET_PATH / model_name / folder_name
    task_outputs_folder = output_folder / "task_outputs"
    os.makedirs(task_outputs_folder, exist_ok=True)

    task_ids = results.keys()
    for task_id in task_ids:
        task_data = {
            "results": results[task_id],
            "solutions": solutions[task_id],
            "errors": [e.__repr__() for e in errors[task_id]]
        }
        file_path = task_outputs_folder / f"{task_id}.json"
        with open(file_path, 'w') as json_file:
            json.dump(task_data, json_file, indent=4)

    score_data = {'model_name' : model_name}
    score_data['base_model_name'] = base_model_name
    score_data['scores'] = {f"pass@{i+1}": value for i, value in enumerate(pass_at_k)}
    passed_file_path = output_folder / "scores_humaneval.json"
    with open(passed_file_path, 'w') as json_file:
        json.dump(score_data, json_file, indent=4)

    print(f"Data saved in: {output_folder}")
