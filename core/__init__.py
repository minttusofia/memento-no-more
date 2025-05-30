from pathlib import Path
from os import environ

BASE_PATH = Path(__file__).parent.parent

ADAPTER_PATH = Path(environ.get("ADAPTER_PATH", BASE_PATH / "adapters"))
MODEL_PATH = Path(environ.get("MODEL_PATH", BASE_PATH / "checkpoints"))

TOOLQA_PATH = Path(environ.get("TOOLQA_PATH", BASE_PATH / "tasks/t_ToolQA/ToolQA"))
