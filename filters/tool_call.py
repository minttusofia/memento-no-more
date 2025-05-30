from abc import abstractmethod
from core.steps import StepMessages
from core.messages import Message, Role

from .base import BaseReviewFilter
from .xml_trajectory import ipython_response_from_step, agent_and_status_messages_from_step, agent_status_task_messages_from_step

helper = {
    "ToolQA": agent_status_task_messages_from_step,
    "OfficeBench": agent_and_status_messages_from_step,
}

class PythonReviewFilter(BaseReviewFilter):
    def __init__(self, allow_syntax_errors: bool = True):
        self.allow_syntax_errors = allow_syntax_errors

    @abstractmethod
    def check_response(self, program: str) -> tuple[str, bool]:
        pass

    def check_step(self, step_messages: StepMessages) -> tuple[str, bool]:
        response = ipython_response_from_step(step_messages)
        if response is None:
            return "Step is not a tool call.", True
        try:
            return self.check_response(self.trim_ipython_tags(response))
        except SyntaxError as e:
            if self.allow_syntax_errors:
                return "The tool call has a syntax error and cannot be parsed.", True
            else:
                raise e

    def trim_ipython_tags(self, program: str) -> str:
        program = program.removeprefix("<run_ipython>\n").removesuffix("\n</run_ipython>")
        program = program.removeprefix("<run_ipython>").removesuffix("</run_ipython>")
        program = program.strip("\n")
        return program

class LLMAgentHistoryFilter(BaseReviewFilter):
    def __init__(self, model=None, instructions=None, function=None, allow_syntax_errors: bool = True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.allow_syntax_errors = allow_syntax_errors
        self.model = model
        self.instructions = instructions
        self.function = function

    async def check_messages(self, programs: list[StepMessages]) -> tuple[str, bool]:
        program_content = ""
        for program in programs:
            program_content += program.content + "\n"

        prompt = f"{self.instructions}\n{program_content}"
        msgs = [Message(Role.USER, prompt)]
        #response = asyncio.run(self.model.call(msgs, stream=True))
        response = await self.model.call(msgs)
        reasoning, answer = self.parse_llm_response(response)

        if self.function == 'notification_sending':
            if answer == 'True':
                accept = True
            elif answer == 'False':
                accept = False
            else:
                raise ValueError(f"Unexpected verification result: {answer}; reasoning: {reasoning}")

        elif self.function == 'review_printed':
            if answer == 'True':
                accept = False
            elif answer == 'False':
                accept = True
            else:
                raise ValueError(f"Unexpected verification result: {answer}; reasoning: {reasoning}")

        return reasoning, accept

    async def check_step(self, step_messages: StepMessages) -> tuple[str, bool]:
        messages = agent_and_status_messages_from_step(step_messages)
        if messages is None:
            return "No messages from the agent", True
        try:
            return await self.check_messages(self.trim_ipython_tags(messages))
        except SyntaxError as e:
            if self.allow_syntax_errors:
                return "syntax error", True
            else:
                raise e

    def trim_ipython_tags(self, programs: list[StepMessages]) -> list:
        for program in programs:
            program.content = program.content.removeprefix("<run_ipython>\n").removesuffix("\n</run_ipython>")
            program.content = program.content.removeprefix("<run_ipython>").removesuffix("</run_ipython>")
            program.content = program.content.strip("\n")
        return programs

    def parse_llm_response(self, response: str) -> tuple[str, bool]:
        if '</reasoning>' in response:
            monologue = response.split('</reasoning>')[0].rstrip('\n')
            if '<answer>' in response:
                answer = response.split('<answer>')[1].lstrip('\n').split('\n')[0]
            else:
                answer = None
        elif '<answer>' in response:
            monologue = response.split('<answer>')[0].rstrip('\n')
            answer = response.split('<answer>')[1].lstrip('\n').split('\n')[0]
        else:
            monologue = response
            answer = None
        if answer is not None:
            answer = answer.strip()
        return monologue, answer

class LLMAgentHistoryFilterForBenchmark(BaseReviewFilter):
    def __init__(self, benchmark = "OfficeBench", model=None, instructions=None, function=None, allow_syntax_errors: bool = True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.allow_syntax_errors = allow_syntax_errors
        self.model = model
        self.instructions = instructions
        self.function = function
        self.benchmark = benchmark

    async def check_messages(self, programs: list[StepMessages]) -> tuple[str, bool]:
        program_content = ""
        for program in programs:
            program_content += program.content + "\n"

        prompt = f"{self.instructions}\n{program_content}"
        msgs = [Message(Role.USER, prompt)]
        response = await self.model.call(msgs)
        reasoning, answer = self.parse_llm_response(response)

        if answer == 'True':
            accept = True
        elif answer == 'False':
            accept = False
        else:
            raise ValueError(f"Unexpected verification result: {answer}; reasoning: {reasoning}")

        return reasoning, accept

    async def check_step(self, step_messages: StepMessages) -> tuple[str, bool]:
        messages = helper[self.benchmark](step_messages)
        if messages is None:
            return "No messages from the agent", True
        try:
            return await self.check_messages(self.trim_ipython_tags(messages))
        except SyntaxError as e:
            if self.allow_syntax_errors:
                return "syntax error", True
            else:
                raise e

    def trim_ipython_tags(self, programs: list[StepMessages]) -> list:
        for program in programs:
            program.content = program.content.removeprefix("<run_ipython>\n").removesuffix("\n</run_ipython>")
            program.content = program.content.removeprefix("<run_ipython>").removesuffix("</run_ipython>")
            program.content = program.content.strip("\n")
        return programs

    def parse_llm_response(self, response: str) -> tuple[str, bool]:
        if '</reasoning>' in response:
            monologue = response.split('</reasoning>')[0].rstrip('\n')
            if '<answer>' in response:
                answer = response.split('<answer>')[1].lstrip('\n').split('\n')[0]
            else:
                answer = None
        elif '<answer>' in response:
            monologue = response.split('<answer>')[0].rstrip('\n')
            answer = response.split('<answer>')[1].lstrip('\n').split('\n')[0]
        else:
            monologue = response
            answer = None
        if answer is not None:
            answer = answer.strip()
        return monologue, answer