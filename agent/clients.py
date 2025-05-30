import os
import sys
import time
from transformers import AutoTokenizer, TextStreamer
from typing import Tuple
from warnings import warn

from .async_retry_caller import AsyncRetryCaller
from .stats import Stats

from core import MODEL_PATH
from core.count_tokens import num_tokens_openai
from core.llm import ResponseFormat, START_SEQUENCES, STOP_SEQUENCES, LLM, MODEL_FULL_NAME, MyStoppingCriteria
from core.messages import Message, merge_messages
from core.usage import Usage
from core.utils import Colors

def print_response(text: str, color: str = Colors.BLUE):
    print(color + text, end="", flush=True, file=sys.__stdout__)

def default_color():
    print(Colors.DEFAULT, end="", flush=True, file=sys.__stdout__)

class BaseClient:
    def __init__(self, merge_messages_by_role: bool = False):
        self.merge_messages_by_role = merge_messages_by_role

    def call(
        self,
        messages: list,
        *,
        stats: Stats = None,
        verbose: bool = False,
        request_json: bool = False,
        **kwargs
    ) -> str:
        raise NotImplementedError

    def count_tokens(self, messages: list[Message]) -> int:
        # If token counting is not implemented, return a rough estimate
        n_chars = sum((len(msg.content)+4) for msg in messages)
        return n_chars // 3

    def format_messages(
        self,
        messages: list[Message],
    ) -> list[dict]:
        if self.merge_messages_by_role:
            messages = merge_messages(messages)
        return [message_to_dict(msg) for msg in messages]


def get_tokenizer_name(model_name: str) -> str:
    if model_name.startswith("llama3-"):
        return "llama3-8b"
    elif model_name.startswith("llama3.1-"):
        return "llama3.1-8b"
    else:
        raise ValueError(f"Not sure which tokenizer to use for model {model_name}")

def get_client(model: str, base_url: str = "http://localhost:8000/v1") -> BaseClient:
    if model.startswith("claude"):
        return ClaudeClient(model=model)
    elif model.startswith("deepseek"):
        return DeepSeekClient(model=model)  # 'deepseek-chat'
    elif model.startswith("gpt") or model.startswith("o1"):
        return OpenAIClient(model=model)
    elif model == "mixtral":
        llm = LLM("mixtral-instruct")
        return LLMClient(llm, merge_messages_by_role=True)
    elif model == "llama3-8b":
        llm = LLM("llama3-8b-instruct")
        return LLMClient(llm, merge_messages_by_role=False)
    elif model == "llama3-70b":
        llm = LLM("llama3-70b-instruct")
        return LLMClient(llm, merge_messages_by_role=False)
    elif model.startswith("v-"):
        # Example: "v-llama3-8b"
        model_name = model[2:]
        return vLLMClient(model[2:], tokenizer=get_tokenizer_name(model_name), base_url=base_url)
    elif model.startswith("vm-"):
        # vLLM serving a model with a merged adapter
        # Example: vm-llama3-agent/glossy-fork
        model_path = str(MODEL_PATH / model[3:])
        return vLLMClient(model_path, tokenizer="llama3-8b", base_url=base_url)
    elif model.startswith("di-"):
        return DeepInfraClient(model[3:])
    else:
        raise ValueError(f"Unknown model: {model}")


class OpenAIClient(BaseClient):
    def __init__(
        self,
        model: str,
        *,
        is_async: bool = True,
        merge_messages_by_role: bool = False,
        api_key: str = None,
        base_url: str = None,
    ):
        from openai import AsyncOpenAI, OpenAI

        self.model = MODEL_FULL_NAME[model] if model in MODEL_FULL_NAME else model
        cls = AsyncOpenAI if is_async else OpenAI
        self.client = cls(api_key=api_key, base_url=base_url)

        self.remove_leading_space = False  # This is to fix the problem that tokenizers always add a space at the beginning
        self.merge_messages_by_role = merge_messages_by_role
        self._response_format_warning_issued = False

    def count_tokens(self, messages: list[Message]) -> int:
        messages = self.format_messages(messages)
        return num_tokens_openai(messages, self.model)

    async def call(
        self,
        messages: list,
        *,
        stats: Stats = None,
        verbose: bool = False,
        max_attempts: int = 3,
        wait_seconds: int = 1,
        single_try_timeout: int = 120,
        response_format: ResponseFormat = None,
        stream: bool = False,
        return_full_response: bool = False,
        **kwargs,
    ) -> str:
        
        if self.model.startswith("gpt") or self.model.startswith("o1"): # set temperature to 0.0 for gpt models
            kwargs['temperature'] = 0.0

        if response_format:
            if not self._response_format_warning_issued:
                self._response_format_warning_issued = True
                warn(f"{response_format} is not supported by {self.__class__.__name__}", stacklevel=2)

            stop_seq = STOP_SEQUENCES[response_format]

        fmt_messages = self.format_messages(messages)
        call_outputs = await self._call(
            fmt_messages,
            stats,
            stream=stream,
            return_full_response=return_full_response,
            **kwargs)
        if return_full_response:
            content, response = call_outputs
        else:
            content = call_outputs

        # This is a hack that we have to use without guidance
        if response_format and response_format != ResponseFormat.JSON:
            content = content.split(stop_seq)[0] + stop_seq

        return content

    async def _call(self,
        messages_or_prompt: list[dict] | str,  # List of messages or a prompt string
        stats: Stats,
        stream=False,
        *,
        return_full_response=False,
        color: str = Colors.BLUE,
        **kwargs
    ) -> str:
        """
        Call the OpenAI API with the given messages or prompt.

        messages_or_prompt is either a list of messages or a prompt string.
        If a list is passed, the chat API is used, otherwise the completion API.
        """
        if stream:
            content, usage = await self.stream_response(messages_or_prompt, color=color, **kwargs)
            call_time, retry_count = 1., 0
            response = None

        else:
            retry_caller = AsyncRetryCaller(max_attempts=3, wait_seconds=1, single_try_timeout=120)
            chat = isinstance(messages_or_prompt, list)
            if chat:
                response = await retry_caller(
                    self.client.chat.completions.create,
                    model=self.model,
                    messages=messages_or_prompt,
                    **kwargs,
                )
            else:
                response = await retry_caller(
                    self.client.completions.create,
                    model=self.model,
                    prompt=messages_or_prompt,
                    **kwargs,
                )

            choice = response.choices[0]
            content = choice.message.content if hasattr(choice, "message") else choice.text
            if self.remove_leading_space and content.startswith(" "):
                content = content[1:]
            usage = Usage(
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
            )
            call_time = retry_caller.success_time
            retry_count = retry_caller.attempt_count - 1

        if stats:
            stats.update(
                usage=usage,
                call_time=call_time,
                retry_count=retry_count,
                model=self.model,
            )
        if return_full_response:
            return content, response
        else:
            return content

    async def stream_response(
        self,
        messages_or_prompt: list[dict] | str,  # List of messages or a prompt string
        *,
        color: str = Colors.BLUE,
        **kwargs,  # Additional arguments to pass to the OpenAI API
    ) -> Tuple[str, Usage]:
        kwargs["stream"] = True
        chat = isinstance(messages_or_prompt, list)
        if chat:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages_or_prompt,
                **kwargs,
            )
        else:
            response = await self.client.completions.create(
                model=self.model,
                prompt=messages_or_prompt,
                **kwargs,
            )

        content = ""
        start = True
        async for chunk in response:
            choice = chunk.choices[0]
            text = choice.delta.content if hasattr(choice, "delta") else choice.text
            if start and text:
                start = False
                if self.remove_leading_space and text.startswith(" "):
                    text = text[1:]
            if text:
                content += text
                print_response(text, color)
        default_color()

        if hasattr(chunk, "usage") and chunk.usage:
            # PerplexityAI returns usage in the chunk
            if isinstance(chunk.usage, dict):
                usage = Usage(
                    input_tokens=chunk.usage["prompt_tokens"],
                    output_tokens=chunk.usage["completion_tokens"]
                )
            elif hasattr(chunk.usage, "prompt_tokens"):
                usage = Usage.from_openai(chunk.usage)
            else:
                usage = Usage()
        else:
            usage = Usage()  # Note: OpenAI does not return usage in the stream

        return content, usage


class LLMClient(BaseClient):
    def __init__(
        self,
        llm: LLM,
        tokenizer_id: str = None,
        merge_messages_by_role: bool = False
    ):

        self.llm = llm
        llm.load_model()
        self.merge_messages_by_role = merge_messages_by_role
        tokenizer_id = MODEL_FULL_NAME.get(tokenizer_id, tokenizer_id)
        tokenizer_id = tokenizer_id or llm.model_id
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_id)
        self._terminators = [self.tokenizer.eos_token_id]

    async def call(
        self,
        messages: list,
        *,
        stats: Stats = None,
        verbose: bool = False,
        response_format: ResponseFormat = None,
        **kwargs,
    ) -> str:
        t0 = time.perf_counter()

        content, truncated = self._call(
            messages,
            response_format=response_format,
            merge_messages_by_role=self.merge_messages_by_role,
            **kwargs
        )
        call_time = time.perf_counter() - t0

        if stats:
            stats.update(call_time=call_time)

        return content

    def _call(
        self,
        messages: list[Message] = None,
        temperature: float = None,
        max_new_tokens: int = 2000,
        response_format: ResponseFormat = None,
        stream: bool = False,
        merge_messages_by_role: bool = True,
    ) -> tuple[str, bool]:
        if merge_messages_by_role:
            messages = merge_messages(messages)
        prompt = self.llm.messages_to_prompt(messages)

        streamer = TextStreamer(self.tokenizer, skip_prompt=True) if stream else None

        if response_format:
            start_sequence = START_SEQUENCES[response_format]
            stop_sequence = STOP_SEQUENCES[response_format]
            prompt += start_sequence
            if stream:
                print(start_sequence, end="", flush=True)
        else:
            start_sequence = None
            stop_sequence = None

        inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")
        if stop_sequence:
            prompt_len = inputs['input_ids'].size(1)
            stop_criteria = MyStoppingCriteria(self.tokenizer, prompt_len, stop_sequence)
        else:
            stop_criteria = None

        output_tokens = self.llm.generate(
            **inputs,
            temperature=temperature,
            max_new_tokens=max_new_tokens,
            streamer=streamer,
            stop_criteria=stop_criteria,
        )

        if stop_criteria and stop_criteria(output_tokens, None):
            truncated = True
        else:
            truncated = output_tokens[0, -1] != self.tokenizer.eos_token_id

        response = self.tokenizer.decode(output_tokens[0], skip_special_tokens=True)

        if start_sequence:
            response = start_sequence + response
        return response, truncated


class MockClient(BaseClient):
    """A mock client that returns a sequence of responses, or a default response if the sequence is empty."""
    def __init__(self, responses: list[str]):
        self.responses = responses
        self.stored_messages = []

    async def call(
        self,
        messages: list[Message],
        *,
        stats: Stats = None,
        stream=False,
        **kwargs
    ) -> str:

        if not self.responses:
            raise ValueError("No responses left in the mock client")

        content = self.responses.pop(0)
        if stream:
            print_response(content)

        self.stored_messages.append({"messages": messages, "response": content})

        if stats:
            stats.update()
        return content


class ClaudeClient(BaseClient):
    def __init__(
        self,
        model: str,
        *,
        is_async: bool = True,
    ):
        import anthropic

        if is_async:
            self.client = anthropic.AsyncAnthropic()
        else:
            self.client = anthropic.Anthropic()
        self.model = model
        self.merge_messages_by_role = True  # Claude requires messages to be merged by role

    async def call(
        self,
        messages: list,
        *,
        stats: Stats = None,
        verbose: bool = False,
        max_attempts: int = 3,
        wait_seconds: int = 1,
        single_try_timeout: int = 120,
        response_format: ResponseFormat = None,
        stream: bool = False,
        **kwargs,
    ) -> str:
        fmt_messages = self.format_messages(messages)
        if response_format:
            start_seq = START_SEQUENCES[response_format]
            stop_seq = STOP_SEQUENCES[response_format]
            #  final assistant content cannot end with trailing whitespace
            if start_seq.endswith("\n"):
                start_seq = start_seq[:-1]

            fmt_messages.append(
                {"role": "assistant", "content": start_seq}
            )
            if stream:
                print_response(start_seq)

        for retry_count in range(max_attempts):
            try:
                if not stream:
                    message = await self.client.messages.create(
                        model=self.model,
                        max_tokens=1000,
                        temperature=0.0,
                        messages=fmt_messages,
                    )
                    content = message.content[0].text
                else:
                    async with self.client.messages.stream(
                        max_tokens=1024,
                        messages=fmt_messages,
                        model=self.model,
                    ) as response:
                        content = ""
                        async for text in response.text_stream:
                            content += text
                            print_response(text)
                            if response_format and stop_seq in content:
                                break

                    message = response.current_message_snapshot

                usage = Usage.from_anthropic(message.usage)
                break
            except Exception as e:
                print(f"Attempt {retry_count+1}/{max_attempts} failed: {e}")
                time.sleep(wait_seconds)

        if response_format:
            content = start_seq + content
            # Strip what comes after the stop sequence
            content = content.split(stop_seq)[0] + stop_seq

        if stats:
            stats.update(usage=usage, retry_count=retry_count, model=self.model)

        return content


class vLLMClient(OpenAIClient):
    def __init__(
        self,
        model: str,
        tokenizer: str,
        base_url: str = "http://localhost:8000/v1",
        chat: bool = False,  # Switches between the chat and completion API
        *,
        is_async: bool = True,
        merge_messages_by_role: bool = False,
    ):
        """
        In order to use the vLLM client, you need to have the vLLM server running. The instructions to run the server
        can be found in the README file (file://./../readme.md)

        model should be one of the following:
        - a short name of the model, for example, "llama3-8b" (see MODEL_FULL_NAME)
        - name of the model in the HF model hub
        - path to a merged model, for example, MODEL_PATH / "ToolQA/round1_trained"

        On the server side, the tokenizer is stored in the model directory. We need to pass
        the tokenizer to apply_chat_template and to compute the number of tokens on the client side.
        """
        from openai import AsyncOpenAI, OpenAI

        cls = AsyncOpenAI if is_async else OpenAI
        self.client = cls(
            base_url=base_url,
            api_key=os.environ.get("VLLM_SERVER_KEY"),
        )
        self.model = MODEL_FULL_NAME[model] if model in MODEL_FULL_NAME else model

        tokenizer_name = MODEL_FULL_NAME[tokenizer] if tokenizer in MODEL_FULL_NAME else tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        self.extra_body = {
            #"top_k": 50,
            #
            # Beam search settings:
            #"top_k": -1,
            #"use_beam_search": True,
            #"best_of": 5,
            #"temperature": 0.0,
            #
            "min_p": 0.7,
        }

        self.chat = chat
        self.remove_leading_space = True
        self.merge_messages_by_role = merge_messages_by_role

    def count_tokens(self, messages: list[Message]) -> int:
        fmt_messages = self.format_messages(messages)
        tokenized_messages = self.tokenizer.apply_chat_template(fmt_messages, tokenize=True)
        return len(tokenized_messages)

    async def call(
        self,
        messages: list[Message],
        *,
        stats: Stats = None,
        verbose: bool = False,
        max_attempts: int = 3,
        wait_seconds: int = 1,
        single_try_timeout: int = 120,
        response_format: ResponseFormat = None,
        response_start: str = None,
        stream: bool = False,
        return_full_response: bool = False,
        **kwargs,
    ) -> str:
        extra_body = self.extra_body.copy()
        extra_char = ""

        if (response_format and response_start):
            raise ValueError("response_format and response_start cannot be used together")
        if self.chat and response_start:
            raise ValueError("response_start is not supported in chat mode")
        if response_format:
            start_seq = START_SEQUENCES[response_format]
            stop_seq = STOP_SEQUENCES[response_format]

            if stop_seq[-1] == ">":
                # > doesn't work in stop sequences so we need a workaround
                extra_char = ">"
                stop_seq = stop_seq[:-1]
                if ">" in stop_seq:
                    print("WARNING: there is still > in the stop_sequence")
            extra_body.update({
                "stop": stop_seq,
                "include_stop_str_in_output": True,
            })
            if self.chat:
                extra_body.update({
                    "guided_regex": f"{start_seq}(?s).*",
                })
        else:
            start_seq = response_start or ""

        fmt_messages = self.format_messages(messages)
        extra_body.update(kwargs.get("extra_body", {}))
        kwargs["extra_body"] = extra_body
        kwargs["max_tokens"] = 1000
        if self.chat:
            content = await self._call(
                fmt_messages,
                stats,
                stream=stream,
                return_full_response=return_full_response,
                **kwargs)
            if return_full_response:
                content, response = content
        else:
            content = start_seq
            if stream:
                print_response(start_seq)

            # Start the assistant's answer with start_seq
            fmt_messages.append({"role": "assistant", "content": ""})
            prompt = self.tokenizer.apply_chat_template(fmt_messages, tokenize=False)
            # Remove the last EOS token
            prompt = prompt.rsplit(self.tokenizer.eos_token, 1)[0]
            prompt += start_seq

            completion = await self._call(
                prompt,
                stats,
                stream=stream,
                return_full_response=return_full_response,
                **kwargs)
            if return_full_response:
                completion, response = completion
            content += completion

        if extra_char:
            if stream:
                print_response(extra_char)
                default_color()
            content += extra_char

        if return_full_response:
            return content, response
        else:
            return content


def message_to_dict(msg: Message) -> dict:
    return {
        "role": msg.role.value,
        "content": msg.content,
    }


class DeepSeekClient(OpenAIClient):
    def __init__(
        self,
        model: str,
        *,
        is_async: bool = True,
    ):
        from dotenv import load_dotenv
        load_dotenv()
        from openai import AsyncOpenAI, OpenAI

        self.model = MODEL_FULL_NAME[model] if model in MODEL_FULL_NAME else model

        cls = AsyncOpenAI if is_async else OpenAI
        self.client = cls(api_key=os.environ['DEEPSEEK_API_KEY'], base_url="https://api.deepseek.com")
        self.remove_leading_space = False  # This is to fix the problem that tokenizers always add a space at the beginning
        self.merge_messages_by_role = True
        self._response_format_warning_issued = False


class DeepInfraClient(OpenAIClient):
    def __init__(
        self,
        model: str,
        *,
        is_async: bool = True,
    ):
        from dotenv import load_dotenv
        load_dotenv()
        super().__init__(
            model=model,
            is_async=is_async,
            api_key=os.environ['DEEPINFRA_API_KEY'],
            base_url="https://api.deepinfra.com/v1/openai"
        )
