import ast
from datetime import datetime
from enum import Enum
import git
import glob
import importlib
import json
import os
from pathlib import Path
import pickle
import random
import re
import string
import sys
import traceback
from types import SimpleNamespace, FunctionType
from typing import Iterable, Dict, Tuple
import warnings
from xml.sax.saxutils import escape as sx_escape
import gzip


import torch

from . import BASE_PATH, ADAPTER_PATH

def pickleable_dict(d: dict, exclude=None, no_warning=None):
    """Return a state that can be pickled."""
    state = {}
    no_warning = no_warning or []
    exclude = exclude or []
    for attr_name, attr_value in d.items():
        if attr_name in exclude:
            continue
        try:
            pickle.dumps(attr_value)
            state[attr_name] = attr_value
        except (pickle.PicklingError, TypeError):
            state[attr_name] = None
            if attr_name not in no_warning:
                warnings.warn(f"Could not pickle attribute {attr_name}", stacklevel=2)
    return state

def shallow_copy(obj):
    cls = obj.__class__
    new_obj = cls.__new__(cls)
    new_obj.__dict__.update(obj.__dict__)
    return new_obj

class Colors:
    DEFAULT = '\033[0m'
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[33m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ITALIC = '\033[3m'


def num_parameters(module: torch.nn.Module, requires_grad: bool = None) -> int:
    total = 0
    for p in module.parameters():
        if requires_grad is None or p.requires_grad == requires_grad:
            total += p.numel()
    return total


class DualOutput:
    def __init__(self, filename, mode='a'):
        self.terminal = sys.stdout
        self.log = open(filename, mode)

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):  # needed for Python 3 compatibility
        # This flush method is needed for the file and terminal to handle the buffer
        self.terminal.flush()
        self.log.flush()


class DualOutputContext:
    "Context and file object that directs stdout and stderr to a given terminal and an optional log file."
    def __init__(self, terminal, filename=None):
        self.terminal = terminal
        self.log = open(filename or os.devnull, "w")

    def __str__(self):
        return f"Terminal: {self.terminal}, Log: {self.log}"

    def write(self, message):
        if self.terminal:
            self.terminal.write(message)
        self.log.write(message)
        self.flush()

    def flush(self):  # needed for Python 3 compatibility
        if self.terminal:
            self.terminal.flush()
        self.log.flush()

    def __enter__(self):
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        sys.stdout = self  # Redirect stdout to this class, which writes to both terminal and file
        sys.stderr = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print(str(exc_type.__name__) + ": " + str(exc_val) + "\n", file=self.log)
            traceback.print_tb(exc_tb, file=self.log)
        sys.stdout = self.original_stdout  # Restore original stdout
        sys.stderr = self.original_stderr


class CoreToolInterruption(Exception):
    pass


def find_runs(path: os.PathLike, pattern: str) -> list[Path]:
    full_pattern = os.path.join(path, f'*/*{pattern}')
    matching_folders = glob.glob(full_pattern, recursive=True)

    return matching_folders


def get_adapter_path(adapter_id: str) -> str:
    if not adapter_id or os.path.exists(adapter_id):
        return adapter_id

    matching_folders = find_runs(BASE_PATH / "checkpoints", adapter_id)
    matching_folders.extend(find_runs(ADAPTER_PATH, adapter_id))

    if len(matching_folders) > 1:
        raise ValueError(f"Multiple adapters found: {matching_folders}")

    elif len(matching_folders) == 0:
        raise ValueError(f"Adapter not found: {adapter_id}")

    else:
        print(f"Adapter found: {matching_folders[0]}")
        return matching_folders[0]


def remove_empty(lst: list) -> list:
    return [item for item in lst if item]


def dict_to_simplenamespace(d: dict) -> SimpleNamespace:
    if isinstance(d, dict):
        for key, value in d.items():
            d[key] = dict_to_simplenamespace(value)
        return SimpleNamespace(**d)
    if isinstance(d, list):
        return [dict_to_simplenamespace(item) for item in d]
    return d


class DefaultList(list):
    def __init__(self, default_factory=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_factory = default_factory

    def __getitem__(self, index):
        try:
            return super().__getitem__(index)
        except IndexError:
            # Return a default value if index is out of bounds
            if self.default_factory is not None:
                return self.default_factory()
            else:
                raise

    def __setitem__(self, index, value):
        try:
            super().__setitem__(index, value)
        except IndexError:
            # Add the default value until reaching the desired index
            for _ in range(len(self), index):
                self.append(self.default_factory())
            self.append(value)


async def stream_openai_response(response):
    """Stream the response and print the output.

    """
    tool_call_list = DefaultList(lambda: SimpleNamespace(name="", arguments=""))
    choice = SimpleNamespace(content="", tool_calls=tool_call_list)

    async for chunk in response:
        index = chunk.choices[0].index
        assert index == 0, "Streamed response should have only one choice"

        delta = chunk.choices[0].delta
        if delta.content:
            choice.content += delta.content
            print(delta.content, end="")

        if delta.tool_calls:
            tcix = delta.tool_calls[0].index
            tcf = delta.tool_calls[0].function
            choice.tool_calls[tcix].name += tcf.name
            tool_call = choice.tool_calls[tcix]
            if tcf.name:
                print(f"\nTool call: {tcf.name}" if not tool_call.name else f"{tcf.name}", end="")
                tool_call.name += tcf.name

            if tcf.arguments:
                print(f"\n{tcf.arguments}" if not tool_call.arguments else f"{tcf.arguments}", end="")
                tool_call.arguments += tcf.arguments

    return choice


def elapsed_time_string(start_date: datetime, end_date: datetime) -> str:
    elapsed_time = end_date - start_date
    total_seconds = int(elapsed_time.total_seconds())

    days = elapsed_time.days
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    components = []
    if days > 0:
        components.append(f"{days} day{'s' if days > 1 else ''}")
    if hours > 0:
        components.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if minutes > 0:
        components.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
    if seconds > 0:
        components.append(f"{seconds} second{'s' if seconds > 1 else ''}")

    elapsed_time_str = ", ".join(components)

    return elapsed_time_str


def elapsed_time_string_short(start_date: datetime, end_date: datetime) -> str:
    td = end_date - start_date

    str_td = str(td).split(" days, ")
    if len(str_td) > 1:
        days = str_td[0]
        time = str_td[1]
    else:
        days = "0"
        time = str_td[0]

    time_no_ms = time.split('.')[0]

    if days == "0":  # If there are no days, don't include the days part
        td_no_ms = time_no_ms
    else:
        td_no_ms = f"{days} days, {time_no_ms}"

    return td_no_ms


def random_id(length: int):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def xml_encoder(input_string):
    def replace_control_chars(match):
        char = match.group()
        return f"__{ord(char):02x}__"

    # Control characters pattern: 0-31 and 127
    control_char_pattern = re.compile(r'[\x00-\x09\x0b-\x1F\x7F]')
    # First, escape any __ sequences to avoid conflicts
    escaped_string = input_string.replace("__", "__underscore__")
    # Then replace control characters
    encoded_string = control_char_pattern.sub(replace_control_chars, escaped_string)

    return encoded_string


def xml_decoder(encoded_string):
    def replace_encoded_chars(match):
        code = match.group(1)
        return chr(int(code, 16))

    # Pattern to match __xx__ sequences
    encoded_char_pattern = re.compile(r'__(\w{2})__')
    # Replace encoded control characters with their original characters
    decoded_string = encoded_char_pattern.sub(replace_encoded_chars, encoded_string)
    # Restore any escaped __ sequences
    decoded_string = decoded_string.replace("__underscore__", "__")

    return decoded_string


def escape(txt: str) -> str:
    "Escape strings into XML and handle control characters"
    return sx_escape(xml_encoder(txt))


def git_sha():
    try:
        repo = git.Repo(search_parent_directories=True)
        return repo.head.object.hexsha
    except git.exc.InvalidGitRepositoryError:
        return None


def MMDD():
    return datetime.now().strftime('%m%d')

# Custom encoder to handle function serialization
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, FunctionType):
            # Convert the function to a serializable format using module and qualified name
            return {'__type__': 'function', 'module': obj.__module__, 'qualname': obj.__qualname__}
        return super().default(obj)

# Custom decoder to handle function deserialization
def custom_decoder(dct):
    if '__type__' in dct and dct['__type__'] == 'function':
        # Reconstruct the function from the module and qualified name
        module = importlib.import_module(dct['module'])
        func = module
        for attr in dct['qualname'].split('.'):
            func = getattr(func, attr)
        return func
    return dct

def split_file_into_paragraphs(file_path):
    # Read the contents of the file
    with open(file_path.resolve(), 'r', encoding='utf-8') as file:
        content = file.read()

    # Split the content into paragraphs
    # Assuming paragraphs are separated by two or more newlines
    paragraphs = content.split('\n\n')

    # Remove any leading/trailing whitespace from each paragraph
    paragraphs = [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]

    return paragraphs

class ChangeDirectory:
    def __init__(self, new_dir, debug=False):
        self.new_dir = new_dir
        self.original_dir = None
        self.debug = debug # Set to true to see debug printouts
        self.changed = False  # Flag to track if the directory was changed

    def __enter__(self):
        if os.path.exists(self.new_dir) and os.path.isdir(self.new_dir):
            self.original_dir = os.getcwd()  # Save the current directory
            os.chdir(self.new_dir)  # Change to the new directory
            self.changed = True
            if self.debug:
                print(f"Moving to directory {self.new_dir}")
        else:
            if self.debug:
                print(f"Directory '{self.new_dir}' does not exist. Staying in the current directory.")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.changed:
            os.chdir(self.original_dir)  # Revert to the original directory
            if self.debug:
                print(f"Returning to directory {self.original_dir}")


def check_for_input_function_in_string(code: str) -> bool:
    try:
        # Parse the code string into an AST
        tree = ast.parse(code)
    except SyntaxError:
        # Syntax errors will be caught by the main code
        return False

    for node in ast.walk(tree):
        # Check for function calls
        if isinstance(node, ast.Call):
            # Direct call to 'input'
            if isinstance(node.func, ast.Name) and node.func.id == 'input':
                print(f"Found 'input' function call at line {node.lineno}")
                return True
            # Attribute call (e.g., module.input())
            elif isinstance(node.func, ast.Attribute):
                attr = node.func
                # Drill down to get the base name
                while isinstance(attr, ast.Attribute):
                    attr = attr.value
                if isinstance(attr, ast.Name) and attr.id == 'input':
                    print(f"Found 'input' function call via attribute at line {node.lineno}")
                    return True
        # Check for assignments where 'input' is assigned to a variable
        elif isinstance(node, ast.Assign):
            if isinstance(node.value, ast.Name) and node.value.id == 'input':
                print(f"'input' function assigned to a variable at line {node.lineno}")
                return True
    return False

def stream_jsonl(filename: str) -> Iterable[Dict]:
    """
    Parses each jsonl line and yields it as a dictionary
    """
    if filename.endswith(".gz"):
        with open(filename, "rb") as gzfp:
            with gzip.open(gzfp, 'rt') as fp:
                for line in fp:
                    if any(not x.isspace() for x in line):
                        yield json.loads(line)
    else:
        with open(filename, "r") as fp:
            for line in fp:
                if any(not x.isspace() for x in line):
                    yield json.loads(line)

def get_model_name(client_model: str) -> Tuple[str, str | None]:
    "Returns the shorthand model name and the base model for Llama3[.1] adapters"
    base_model_name = None
    if client_model.startswith("v-"):
        # Example: "v-llama3-8b"
        model_name = client_model[2:]
        base_model_name = model_name
        return client_model[2:], base_model_name
    elif client_model.startswith("vm-"):
        # Example: vm-llama3-agent/glossy-fork
        model_path = client_model[3:]
        model_name = model_path.split("/")[1]
        base_model_path = model_path.split("/")[0]
        if "llama3-70b" in base_model_path:
            base_model_name = "llama3-70b"
        elif "llama3.1-70b" in base_model_path:
            base_model_name = "llama3.1-70b"
        return model_name, base_model_name
    elif client_model.startswith("p-"):
        # Example: "p-llama3-8b"
        model_name = client_model[2:]
        base_model_name = model_name
        return model_name, base_model_name
    else:
        return client_model, base_model_name

class MyEnum(Enum):
    @classmethod
    def from_value(cls, value):
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"{value} is not a valid value in {cls.__name__}")

    def __eq__(self, other):
        return hasattr(other, "value") and self.value == other.value

    def __hash__(self):
        return hash(self.value)
