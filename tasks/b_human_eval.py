from benchmarking.humaneval import HUMANEVAL_PATH
from agent.agent import Agent
from tasks.base import BaseTask
from core.utils import stream_jsonl

def load_human_eval_data(test=False):
    dataset_path = HUMANEVAL_PATH
    if test:
        return [{
            "task_id": "test/0",
            "prompt": "def return1():\n",
            "canonical_solution": "    return 1",
            "test": "def check(candidate):\n    assert candidate() == 1\n\n",
            "entry_point": "return1"
        }]
    return list(stream_jsonl(str(dataset_path)))

BENCHMARK_TASKS_PYTHON: list[dict] = load_human_eval_data()

class HumanEvalTask(BaseTask):
    data_variants = BENCHMARK_TASKS_PYTHON
    n_variants = len(BENCHMARK_TASKS_PYTHON)
    budget = 30

    def __init__(self, variant: int = 0):
        super().__init__(variant)
        self.task_data = self.data_variants[variant]

        # Handle import if there are any 
        imports = self.task_data["prompt"].split("def")[0]
        if imports:
            self.init_script = imports

        self.task = "Below is an incomplete python method. Finish defining the method in your workspace.\n\n"
        self.task += self.task_data["prompt"]
        self.method_name = self.task_data["entry_point"]

    @property
    def _custom_name(self):
        task_id = self.task_data["task_id"]
        task_id = task_id.replace("/", "-") # remove slashes from task name
        return f"b_human_eval_{task_id}"
    
    def evaluate(self, agent: Agent, verbose: bool = True) -> tuple[float, str]:
        score = 1
        report = ""

        # Check if a function with correct name has been implemented
        defined = agent.workspace.eval_expr(f"'{self.method_name}' in globals()")
        if not defined:
            report += "Requested method not implemented."
            score = 0
            return score, report 
        
        if verbose:
            # Print agent's implementation
            agent.workspace.execute_expr("import inspect")
            inspect_expr = f"inspect.getsource({self.method_name})"
            source = agent.workspace.eval_expr(inspect_expr)
            report += f"Agent's implementation:\n\n{source}\n"

            # Print tests
            check_start_index = self.task_data['test'].find("def")
            checks = self.task_data['test'][check_start_index:]
            report += f"Running following tests:\n\n{checks}"

        # Run tests
        agent.workspace.execute_expr(self.task_data["test"])
        test_outcome = agent.workspace.execute_expr(f"check({self.method_name})")
        if test_outcome[1]:
            report += "Tests not passed:\n" + test_outcome[1]
            score = 0
        else:
            report += "Tests passed successfully!"

        return score, report
