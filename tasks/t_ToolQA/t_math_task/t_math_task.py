
from tasks.base import BaseTask
from agent.agent import Agent
from .utils import remove_punc

def modify_agent(agent: Agent):
    # Modifying the docs of the complete_task method
    complete_task_method = agent.config.engine_config.tools["complete_task"]
    complete_task_method.__doc__ = complete_task_method.__doc__.replace("tools.", "")
    agent.workspace.add_variables({"complete_task" : agent.core_tools.complete_task})

class MathTask(BaseTask):

    def __init__(self, question_answer, question_variant = 0):
        self.question_variant = question_variant
        self.task_question = question_answer[0][question_variant]
        self.task_answer = question_answer[1][question_variant]
        self.return_cls_name = "int"
        self.task = self.task_question 

        self.budget = 20


    def evaluate(self, agent, verbose = False):
        "Produce the score and report, as well as fill out analytics"
        score, report = (1.0, "")
        self.analytics = {
            "log_path" : agent.run_path / "output.ans",
            "data_variant" : self.question_variant,
        }
        issue = ''
        agent_answer = agent.return_value
        true_answer = self.task_answer # str
        true_answer = int(remove_punc(true_answer))
        if agent_answer != true_answer:
            issue += f'Incorrect Answer: {agent_answer}; Expected: {true_answer}'
            score = 0.0
        else:
            issue += 'Correct Answer'

        self.analytics["score"] = score

        report += f"score: {score:.2f}\n\n" + f"Issues:{issue}"

        return score, report

    @classmethod
    def generate_variants(cls, question_answer: tuple, question_index: int = 0, number_of_questions: int = 100):
        return [
            cls(question_answer, question_variant)
            for question_variant in range(question_index, question_index + number_of_questions)
        ]

    @property
    def default_name(self):
        name = f"t_math_task_test_v{self.question_variant}"
        return name
