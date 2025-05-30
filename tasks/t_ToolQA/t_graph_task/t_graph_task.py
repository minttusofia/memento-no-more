from tasks.base import BaseTask
from dataclasses import asdict
from .utils import normalize_answer
from agent.agent import Agent

def modify_agent(agent: Agent):
    complete_task_method = agent.config.engine_config.tools["complete_task"]
    complete_task_method.__doc__ = complete_task_method.__doc__.replace("tools.", "")

    agent.workspace.add_variables({"complete_task" : agent.core_tools.complete_task})
    agent.workspace.add_variables({"load_graph" : agent.core_tools.load_graph})
    agent.workspace.add_variables({"check_neighbours" : agent.core_tools.check_neighbours})
    agent.workspace.add_variables({"check_nodes" : agent.core_tools.check_nodes})
    agent.workspace.add_variables({"check_edges" : agent.core_tools.check_edges})

task_descriptions = """In this task, you are asked to answer a question by analyzing graph data. You can use provided tools to assist in exploring the graph. You should return a string as the final answer.

Here is the question:
"""

step_by_step_tips = """Steps to Answer the Question:

1. Read the question carefully.
2. Choose appropriate tools. Read the documentation of the chosen tools to understand the functions of them.
3. Load the graph data.
4. Retrieve the information that is asked in the question by using the provided tools rather than writing code by yourself.
5. Your final answer should be a string only containing the answers to the question without explanatory text.
"""

action_tips = """The answers to the questions have been ensured to be accessible via the provided tools. Do not attempt to use custom programmatic solutions to extract information from the graph.
"""

reasoning_tips = """At each step, use only one tool, and carefully observe the output of each step to better understand how the tool functions.
"""
# question-specific hints
#--------
hint_paper = """Hint on solution: 
Question: What papers did Laddha write?
Hint:
1: Identify the co-author(s) of Laddha.
2: For each co-author, get their joint paper by checking the edge attributes.
3: Combine papers. Remember to remove duplicates.
"""

hint_citation = """Hint on solution:
Question: How many papers cited "A survey on Machine Learning"?
Hint: Focus only on the node attribute 'number of citations for this paper'. There is no need to know the title of papers that cited "A survey on Machine Learning".
"""

hint_most_cited = """Hint on solution:
Question: Which is/are the most cited paper(s) written by Laddha? 
Hint: 
First find out what papers Laddha wrote. Then check the citations of them.
If all papers by Laddha have zero citations, consider all of them as the most cited papers. 
Return only the title(s), without the number of citations.
"""

hint_collaborations = """Hint on solution:
Question: How many papers did Laddha and Baran write together? / How many accumulated citations do papers collaborated by Laddha and Baran?
Hint: Check the edge attributes to find the papers jointly authored by Laddha and Baran. Remember to remove duplicates.
"""

hint_all_collaborations = """Hint on solution:
Question: What is the total number of papers authored by Laddha and collaborators plus those written by collaborators and other people?
Hint:
1. Identify the co-author(s) of Laddha. (Answer: Baran).
2. For Laddha and Baran, get their joint paper by checking the edge attributes.
3. Find out additional co-authors of Baran.
4. Retrieve the papers jointly authored by Baran and each of Baran's additional co-authors.
5. Combine papers. Always remember to remove duplicates to determine the total count.
"""

hint_institution = """Hint on solution:
Question: What institutions participated in the study of 'A survey on Machine Learning'?
Hint: Focus only on the node attribute of the paper 'A survey on Machine Learning'.
If there are multiple institutions, separate them with semicolon and space '; '.
If there is only one institution, provide only the name of the institution without semicolon added at the end.
"""

hint_accumulation_citations = """For this question, strictly follow the steps below:
Question: How many accumulated citations do papers collaborated by Laddha and Baran have?
Solution: 
1. Check the edge attributes to find the papers jointly authored by Laddha and Baran. 
2. strictly follow the code:
``` 
    papers = list(set(papers))
    number_of_citations = 0
    for paper in papers:
        answer += check_nodes(GRAPH_DATA, "PaperNet", paper)["number of citations for this paper"]
```

"""

hint_graph_duplicate_citations = """Now that you got a list of co-authors, you should perform the following operations in the next step:
```
max_citations = 0
answer = []
for co_author in co_authors:
    papers = [paper for paper in check_edges(GRAPH_DATA, "AuthorNet", author, co_author)["papers"]] # find papers co-authored by the author and co-author
    papers = list(set(papers)) # always remember to remove duplicates
    for paper in papers:
        citation += check_nodes(GRAPH_DATA, "PaperNet", paper)["number of citations for this paper"]
    if citation > max_citation:
        max_citation = citation
        answer = [co_author]
    elif citation == max_citation: # multiple collaborators with the same citations
        answer.append(co_author)
answer = "; ".join(answer) # If there are multiple collaborators with the same citations, separate them with semicolon and space '; '
```
Do not print the answer since the output is too long and will be truncated.
Directly return the answer string as the final output.
"""
hint_duplicate_citations = """Hint: When counting the citations of papers by someone (and their collaborators), ensure that duplicate papers are removed first. After identifying the unique papers, proceed to count their citations.
""" 
#--------

answer_tips = """Note: Provide only the value of the answer as the final output, without any additional text or full sentences.
"""
finalization_tips = """Before completing the task, view the final answer to check for potential issues, such as duplicate papers or formatting inconsistencies.
"""
init_script = """from dataclasses import dataclass
from typing import Literal

@dataclass
class TaskAnswer:
    answer: str
"""

class GraphTask(BaseTask):

    def __init__(self, question_answer, question_variant = 0, level = 'easy'):
        self.task_question = question_answer[0][question_variant]
        self.task_answer = question_answer[1][question_variant]
        if len(question_answer) == 3:
            self.task_question_type = question_answer[2][question_variant]
        self.question_variant = question_variant
        self.return_cls_name = "str"
        #self.return_cls_name = "TaskAnswer"
        self.level = level
        self.task = task_descriptions + self.task_question 
        # self.init_script = init_script
        self.budget = 20
    
    def evaluate(self, agent, verbose = False):
        "Produce the score and report, as well as fill out analytics"
        score, report = (1.0, "")
        self.analytics = {
            "log_path" : agent.run_path / "output.ans",
            "data_variant" : self.question_variant,
        }
        issue = ''
        #agent_answer = asdict(agent.return_value).get('answer', None)
        agent_answer = agent.return_value
        true_answer = self.task_answer
        if not isinstance(true_answer, str):
            true_answer = str(true_answer)

        if not normalize_answer(agent_answer, true_answer):
            issue += f'Incorrect Answer: {agent_answer}; Expected: {true_answer}'
            score = 0.0
        else:
            issue += 'Correct Answer'

        self.analytics["score"] = score

        report += f"score: {score:.2f}\n\n" + f"Issues:{issue}"

        return score, report

    @classmethod
    def generate_variants(cls, question_answer: tuple, level: str = 'easy', question_index: int = 0, number_of_questions: int = 100):
        return [
            cls(question_answer, question_variant, level)
            for question_variant in range(question_index, question_index + number_of_questions)
        ]
    
    @property
    def default_name(self):
        name = f"t_graph_task_{self.level}_v{self.question_variant}"
        return name