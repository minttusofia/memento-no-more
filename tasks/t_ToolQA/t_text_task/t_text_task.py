from tasks.base import BaseTask
from agent.agent import Agent
from dataclasses import asdict
from .utils import normalize_answer
from .format_tips import FORMAT_TIPS

def modify_agent_agenda(agent: Agent):
    complete_task_method = agent.config.engine_config.tools["complete_task"]
    complete_task_method.__doc__ = complete_task_method.__doc__.replace("tools.", "")

    agent.workspace.add_variables({"complete_task" : agent.core_tools.complete_task})
    agent.workspace.add_variables({"retrieve_agenda" : agent.core_tools.retrieve_agenda})

task_descriptions = """You are tasked with answering a question about an agenda by querying a database containing over 9,000 documents. To efficiently find the answer, you can use the provided tool to retrieve a subset of relevant documents for analysis, avoiding the need to manually search the entire database. Use the retrieved documents to determine the final answer.

Here is the question:
""" 
   
step_by_step_tips = """Steps to Answer the Question:

1. Read the question carefully.
2. Use the tool to query the database. Review the tool's documentation to ensure proper usage.
3. When using the tool, write an appropriate query to retrieve relevant documents, and specify the number of documents to retrieve based on the complexity of the question.
4. Analyze the retrieved documents to find the information needed to answer the question.
5. If the answer is not found, you can refine your query or retrieve more documents.
6. Your final answer should be a string only containing the answers to the question without explanatory text or context.
"""

num_docs_tips = """Number of Documents to Retrieve: 
For questions about a specific time, place, event, or person, start with a smaller number of documents. If the answer is not found in the initial set, you can increase the number of documents retrieved.
""" 

long_context_tips = """When a large number of documents are retrieved, it may not be feasible to display all of them at once, as the output could be truncated.
"""
# question-specific hints
#--------
hint_atendee = """Hint on solution:
Question: Who attended the exhibition?
Retrieved document: "The exhibition was planned by Paul, and he will host the event. He will present some art work then."
Solution:
Start by retrieving, e.g., 10 documents. 
You only need to return one attendee's name. 
In this case, Paul is the host of the exhibition, which qualifies him as an attendee. Therefore, the answer is 'Paul'.

Roles such as host, participant, presenter, or any similar designation are all considered as 'attendee.'. It is sufficient to provide the name of one attendee. 
"""

hint_query = """Hint on solution:
Question: What did Paul do on 2022/04/05 from 10:00 AM to 12:00 AM?
Hint: Start by retrieving, e.g., 10 documents. If you don't find the answer in the retrieved documents, try modifying your query by replacing keywords or rephrasing it., e.g., "Paul 2022/04/05 10:00 AM 12:00 AM"; "Paul' activities on 2022/04/05 from 10:00 AM to 12:00 AM"; "Paul's agenda on 2022/04/05 from 10:00 AM to 12:00 AM", etc.
You can also simplify your query by reducing the number of keywords, which helps retrieve more results.
"""

hint_event_name = """Hint: When answering questions about the name of an event, provide the exact name of the event as stated in the document. For example, if the document indicates that the event is named 'park picnic', the answer should be 'park picnic' but not 'picnic'.
"""

hint_venue_name = """Hint: When answering questions about the location of an event, provide the exact name of the place as stated in the document, without any context. For example, if the document indicates that the event took place at 'the garden of The Central Park', the answer should be 'the garden of The Central Park' but not 'Central Park'.
"""

hint_schedule = """To answer this question, you must follow the example solution below:
Question: When should I schedule a meeting with Paul from 9:00 AM to 6:00 PM on 2023/01/01?
Solution:
1. Start by retrieving 1000 documents related to Paul: `retrieved_docs = retrieve_agenda('Paul', 1000)`.  
2. Do not print all retrieved documents. Instead, filter again to make sure these documents are related to Paul: `docs_with_paul = [doc for doc in retrieved_docs if 'Paul' in doc]`. Always remember to do this step.
3. Refine the results by filtering documents that mention the date: `docs = [doc for doc in docs_with_paul if 'January 1' in doc]`. Dates must strictly follow the format: "Month in word + day in number", e.g., "January 1".
4. Review the remaining documents: `print(docs)`.
5. Read the retrieved documents and think in your monologue to determine the best time for scheduling the meeting. Avoid using programmatic solutions to extract the answer.
6. Before ending the task, ensure that you focus on finding an available time slot within the window of 9:00 AM to 6:00 PM.
Note that if there is not events scheduled within 9:00 AM to 6:00 PM, then the meeting can be scheduled at any time within that window. Thus, the answer would be 9:00 AM-6:00 PM.
"""

hint_schedule_generalization = """Question: When should I schedule a meeting with Paul from 9:00 AM to 6:00 PM on 2023/01/01?
This question is a more general one, which requires you to find out all events within a time window. For these types of question, you must follow the example solution below:
Solution:
1. Start by retrieving 1000 documents related to Paul: `retrieved_docs = retrieve_agenda('Paul', 1000)`.  
2. Do not print all retrieved documents. Instead, filter again to make sure these documents are related to Paul: `docs_with_paul = [doc for doc in retrieved_docs if 'Paul' in doc]`. Always remember to do this step.
3. Refine the results by filtering documents that mention the date: `docs = [doc for doc in docs_with_paul if 'January 1' in doc]`. Dates must strictly follow the format: "Month in word + day in number", e.g., "January 1".
4. Review the remaining documents: `print(docs)`.
5. Read the retrieved documents and think in your monologue to determine the best time for scheduling the meeting. Avoid using programmatic solutions to extract the answer.
6. Before ending the task, ensure that you focus on finding an available time slot within the window of 9:00 AM to 6:00 PM.
Note that if there is not events scheduled within 9:00 AM to 6:00 PM, then the meeting can be scheduled at any time within that window. Thus, the answer would be 9:00 AM-6:00 PM.
"""

hint_all_events = """To answer this question, you must follow the example solution below:
Question: What events does Paul have on 2023/01/01?
Solution:
1. Start by retrieving 1000 documents related to Paul: `retrieved_docs = retrieve_agenda('Paul', 1000)`. 
2. Do not print all retrieved documents. Instead, filter again to make sure these documents are related to Paul: `docs_with_paul = [doc for doc in retrieved_docs if 'Paul' in doc]`. Always remember to do this step.
3. Refine the results by filtering documents that mention the date: `docs = [doc for doc in docs_with_paul if 'January 1' in doc]`. Dates must strictly follow the format: "Month in word + day in number", e.g., "January 1".
4. Review the remaining documents: `print(docs)`.
5. Read the retrieved documents to find out all events Paul has on this day. Avoid using programmatic solutions to extract the answer.
"""

hint_time_window = """
To determine available time windows from 9:00 AM to 6:00 PM for a meeting:
1. Read the retrieved document carefully to identify event(s) between 9:00 AM and 6:00 PM. Focus on identifying any time slots where events conflict with the potential meeting time.
2. Use reasoning in your monologue to determine available time windows. The answer should be all time slots within 9:00 AM to 6:00 PM where no event is scheduled. 
    Note: Do not use programmatic solutions to calculate or extract the answer. Consider only available time windows within 9:00 AM to 6:00 PM. 
    Example:
    If an event is from 9:30 AM to 1:00 PM, the answer would be: 9:00 AM-9:30 AM, 1:00 PM-6:00 PM.
    If an event is from 4:00 PM to 6:00 PM, the answer would be: 9:00 AM-4:00 PM.
    If an event is from 7:00 AM to 10:00 AM, the answer would be: 10:00 AM-6:00 PM.
    If an event is from 6:00 PM to 7:00 PM, the answer would be: 9:00 AM-6:00 PM. (Events beyond the range of 9:00 AM to 6:00 PM should not affect the answer.)
3. Check your answer. If you are sure that your answer is correct in both value and format, you can call `complete_task(final_report: str, return_value)` to finish the task.
"""
#--------

hint_date = """Dates in the documents are written in words. For example, '04/05' appear as 'April 5'.
"""

answer_tips = """Note: Provide only the value of the answer as the final output, without any additional text or full sentences.
"""

init_script = """from dataclasses import dataclass
from typing import Literal

@dataclass
class TaskAnswer:
    answer: str
"""

class TextTask(BaseTask):

    def __init__(self, question_answer, question_variant = 0, level = 'easy'):
        self.task_question = question_answer[0][question_variant]
        self.task_answer = question_answer[1][question_variant]
        self.task_question_type = question_answer[2][question_variant]
        self.question_variant = question_variant
        # self.return_cls_name = "TaskAnswer"
        self.return_cls_name = "str"
        self.level = level
        task_descriptions + self.task_question + "\n\nFormat tip: " + FORMAT_TIPS[self.task_question_type] 
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
        # agent_answer = asdict(agent.return_value).get('answer', None)
        agent_answer = agent.return_value
        true_answer = self.task_answer

        if not normalize_answer(agent_answer, true_answer, self.task_question_type):
            issue += f'Incorrect Answer: {agent_answer}; Expected: {true_answer}'
            score = 0.0
        else:
            issue += 'Correct Answer'
        
        if agent_answer == 'Not Found':
            issue += '\nAnswer Not Found'

        self.analytics["score"] = score

        report += f"score: {score:.2f}\n\n" + f"Issues:{issue}"

        return score, report

    @classmethod
    def generate_variants(cls, question_answer: tuple, level: str = 'easy',  question_index: int = 0, number_of_questions: int = 100):
        return [
            cls(question_answer, question_variant, level)
            for question_variant in range(question_index, question_index + number_of_questions)
        ]
    
    @property
    def default_name(self):
        name = f"t_text_task_agenda_{self.level}_v{self.question_variant}"
        return name