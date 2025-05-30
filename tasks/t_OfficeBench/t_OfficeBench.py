from tasks.base import BaseTask, AGENT_HOME
from pathlib import Path
import shutil
import os
from agent.agent import Agent
from tasks.t_OfficeBench.utils import load_task_info, get_testbed_path
from tasks.t_OfficeBench.OfficeBench import evaluation

task_decpription = """
Today is {date} ({weekday}). The current time is {time}. You are an AI assistant for user {username}. Your role is to help in office-related tasks. 

Your task is:
"""

generic_hints = """
General Guidelines:
1. Solve the task step by step.
2. Use the provided tools as needed, but call only one tool in each step.
3. You are given a string variable `data_path`, which specifies the directory where task files are stored. If the task requires accessing task files, locate them under `data_path`. 
4. To retrieve the names of all task files in the folder, import `os` and use: `os.listdir(data_path)`. When you don't find the file you need, run this step to check the folder contents.

Note: Do not modify `data_path`; it is already set to the task files folder. Strictly forbid reassigning `data_path` (e.g., data_path = ...).
"""

file_operations_hints = """Do not forget to import `os`.
You can import `os` and `shutil` to perform file operations: use `os.rename` to rename a file; use `os.remove` to delete a file; use `shutil.copy` to duplicate a file; use `shutil.move` to move a file.
"""

def modify_agent(agent: Agent):
    # Modifying the docs of the complete_task method
    complete_task_method = agent.config.engine_config.tools["complete_task"]
    complete_task_method.__doc__ = complete_task_method.__doc__.replace("tools.", "")
    agent.workspace.add_variables({"create_event": agent.core_tools.create_event})
    agent.workspace.add_variables({"delete_event": agent.core_tools.delete_event})
    agent.workspace.add_variables({"list_events": agent.core_tools.list_events})
    agent.workspace.add_variables({"list_emails": agent.core_tools.list_emails})
    agent.workspace.add_variables({"read_email": agent.core_tools.read_email})
    agent.workspace.add_variables({"send_email": agent.core_tools.send_email})
    agent.workspace.add_variables({"excel_convert_to_pdf": agent.core_tools.excel_convert_to_pdf})
    agent.workspace.add_variables({"excel_create_new_file": agent.core_tools.excel_create_new_file})
    agent.workspace.add_variables({"excel_delete_cell": agent.core_tools.excel_delete_cell})
    agent.workspace.add_variables({"excel_read_file": agent.core_tools.excel_read_file})
    agent.workspace.add_variables({"excel_set_cell": agent.core_tools.excel_set_cell})
    agent.workspace.add_variables({"ocr_recognize_text": agent.core_tools.ocr_recognize_text})
    agent.workspace.add_variables({"image_convert_to_pdf": agent.core_tools.image_convert_to_pdf})
    agent.workspace.add_variables({"pdf_convert_to_image": agent.core_tools.pdf_convert_to_image})
    agent.workspace.add_variables({"pdf_read_file": agent.core_tools.pdf_read_file})
    agent.workspace.add_variables({"pdf_convert_to_word": agent.core_tools.pdf_convert_to_word})
    agent.workspace.add_variables({"word_convert_to_pdf": agent.core_tools.word_convert_to_pdf})
    agent.workspace.add_variables({"word_create_new_file": agent.core_tools.word_create_new_file})
    agent.workspace.add_variables({"word_read_file": agent.core_tools.word_read_file})
    agent.workspace.add_variables({"word_write_to_file": agent.core_tools.word_write_to_file})

    agent.workspace.add_variables({"complete_task": agent.core_tools.complete_task})


class OfficeBenchBase(BaseTask):

    def __init__(self, level: str='all', task_id: str='1-1', subtask_id: str='0'):
        self.level = level
        self.task_id = task_id
        self.subtask_id = subtask_id
        self.task, self.username, self.date, self.weekday, self.time, self.task_tools = load_task_info(self.task_id, self.subtask_id)
        self.task = task_decpription.format(date=self.date, weekday=self.weekday, time=self.time, username=self.username,) + self.task
        self.source_testbed_path = get_testbed_path(self.task_id) # e.g., /training/tasks/t_OfficeBench/OfficeBench/tasks/1-1/testbed
        self.input_variables = {
            "data_path": None,
        }
        self.budget = 30
        self.agent_home: Path = AGENT_HOME  # default: tasks/home

        self.return_cls_name = None
        self.eval_config = evaluation.load_eval_config(self.task_id, self.subtask_id)
        # If any eval function expects the answer in data/answer.txt, return class should be a str
        for eval_item in self.eval_config:
            if ("args" in eval_item and "file" in eval_item["args"]
                and eval_item["args"]["file"] == "data/answer.txt"):
                self.return_cls_name = "str"
                break


    def __enter__(self):
        self.old_cwd = os.getcwd()
        self.dir_before = self.old_cwd
        self.agent_home.mkdir(exist_ok=True)
        target_testbed_path = self.agent_home / 'testbed' # e.g., /training/agent_batch_runs/v-llama3.1-70b/*_OfficeBench_all_g-full/t_OfficeBench_all_1-1_2_t2/testbed
        self.target_testbed_path = target_testbed_path
        create_tree(self.source_testbed_path, target_testbed_path)
        return self
    
    def evaluate(self, agent: Agent = None, verbose: bool = False):
        # if self.return_cls_name == "str":
        #     # If any eval function expects the answer in data/answer.txt, create it here
        #     os.makedirs(os.path.join(self.target_testbed_path, "data"), exist_ok=True)
        #     with open(os.path.join(self.target_testbed_path, "data/answer.txt"), "w") as f:
        #         f.write(agent.return_value)
        # else:
        result, report = evaluation.evaluate_output(self.task_id, self.subtask_id, self.target_testbed_path, self.source_testbed_path)
        score = int(result)
        return score, report
    
    @classmethod
    def generate_variants(cls, level: str, task_index: list): # task_index = [(task_id, subtask_id), ...]
        return [
            cls(level, task_id, subtask_id) 
            for (task_id, subtask_id) in task_index
        ]

class OfficeBenchTask(OfficeBenchBase):
    @property
    def default_name(self):
        return f"t_OfficeBench_{self.level}_{self.task_id}_{self.subtask_id}"
    

def create_tree(source_testbed_path: Path, target_testbed_path: Path):
    if not source_testbed_path.exists():
        source_testbed_path.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_testbed_path, target_testbed_path)