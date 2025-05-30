from core import ADAPTER_PATH, MODEL_PATH
from training.merge_adapter import merge_adapter

def main(adapter_name: str, project_name: str):
    print(f"Merging adapter {adapter_name} in project {project_name}...")
    adapter_path = ADAPTER_PATH / project_name / adapter_name
    save_path = MODEL_PATH / project_name / adapter_name

    merge_adapter(adapter_path, save_path)

if __name__ == "__main__":
    from jsonargparse import CLI
    CLI(main)
