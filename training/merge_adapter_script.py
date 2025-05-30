# %%
import os

from core.llm import LLM  # noqa

def merge_adapter(
        adapter_path: str,
        save_path: str
    ):
    """
    Merge the adapters in the specified path into the model and save the model.
    """

    llm = LLM.from_adapter(adapter_path)
    llm.load_model()

    llm.model.save_pretrained(save_path)
    llm.tokenizer.save_pretrained(save_path)
    print(f"Model saved to {save_path}.")

def main(
    adapter_id: str="",
    force: bool=False,
    merged_dir_name: str="merged"
):
    merged_dir = adapter_id + "/" + merged_dir_name
    if os.path.isdir(merged_dir) and not force:
        print("Adapter merged already", flush=True)
        return
    os.makedirs(merged_dir, exist_ok=True)

    merge_adapter(
        adapter_path=adapter_id,
        save_path=merged_dir,
    )

# %%
if __name__ == "__main__":
    from jsonargparse import CLI
    CLI(main)
