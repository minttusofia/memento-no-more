# %%
import json
from pathlib import Path

from core import MODEL_PATH, ADAPTER_PATH
from core.llm import LLM

def merge_adapter(
        adapter_path: Path,
        save_path: Path
    ):
    """
    Merge the adapters in the specified path into the model and save the model.
    """
    llm = LLM.from_adapter(adapter_path)
    llm.load_model()

    llm.model.save_pretrained(save_path)
    # llm.tokenizer.save_pretrained(save_path)

    certificate = {
        "model_id": str(llm.model_id),
        "adapter_ids": [str(adapter_id) for adapter_id in llm.adapter_ids],
        "tokenizer_id": llm.tokenizer_id,
    }
    with open(save_path / "creation_certificate.json", 'w', encoding='utf-8') as f:
        json.dump(certificate, f, ensure_ascii=False, indent=4)

    print(f"Model saved to {save_path}.")

# %%
if __name__ == "__main__":
    # %%
    project_name = "ToolQA"
    adapter_name = "0119_overcast-rowhouse"

    adapter_path = ADAPTER_PATH / project_name / adapter_name
    save_path = MODEL_PATH / project_name / adapter_name

    merge_adapter(adapter_path, save_path)

    # %%
