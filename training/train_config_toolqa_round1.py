PROJECT_NAME = "ToolQA"

from agent import AGENT_DATASET_PATH  # noqa
from core import BASE_PATH  # noqa
from core.llm import LLM  # noqa
from training.train_utils import RunConfig, Hyperparameters  # noqa

from train_agent import train  # noqa

def main(run_name: str):
    # These are the most important settings
    group_name = "ToolQA"
    notes = "ToolQA round 1"
    student = None
    base_model = LLM.from_hf("meta-llama/Meta-Llama-3.1-70B-Instruct")
    train_patterns = ["0112_graph_task_train/xml", "0112_table_airbnb_task_train/xml", "0112_table_coffee_task_train/xml", "0112_table_flights_task_train/xml", "0112_table_yelp_task_train/xml", "0112_text_task_train/xml"]
    val_patterns = ["0112_graph_task_test/xml", "0112_table_airbnb_task_test/xml", "0112_table_coffee_task_test/xml", "0112_table_flights_task_test/xml", "0112_table_yelp_task_test/xml", "0112_text_task_test/xml"]
    n_epochs = 2

    use_wandb = True
    run_cfg = RunConfig(
        project_name=PROJECT_NAME,
        run_name=run_name,
        group_name=group_name,
        project_path = BASE_PATH / "checkpoints" / PROJECT_NAME,
        checkpoint_interval=50,
        val_interval=50,
        log_interval=1,
        generation_interval=1000,
        use_wandb=use_wandb,
        notes=notes,
        gradient_checkpointing=True,
        fsdp=True,
        mixed_precision="no",
        student=student,
        base_model=base_model,
        teacher_type="student_base",
    )

    # Training and validation data
    data_path = AGENT_DATASET_PATH / "llama3.1-70b"

    training_data = []
    validation_data = []
    for pattern in train_patterns:
        for dataset_path in list(data_path.glob(pattern)):
            training_data.extend(list(dataset_path.glob('*.xml')))
    for pattern in val_patterns:
        for dataset_path in list(data_path.glob(pattern)):
            validation_data.extend(list(dataset_path.glob('*.xml')))

    hp = Hyperparameters(
        training_data=training_data,
        validation_data=validation_data,
        max_lr=1e-5,
        n_epochs=n_epochs,
        warmup_steps=30,
        logit_loss_micro_batch_size=1,
        n_logit_micro_batches_per_batch=1,
        weight_decay=0.02,
        temperature=2.,
        lr_decay=False,
        lora_target_modules="full",
        lora_r=128,
        student_dropout_rate=0.9,
    )

    train(run_cfg, hp)

if __name__ == "__main__":
    from jsonargparse import CLI
    CLI(main)


# %%