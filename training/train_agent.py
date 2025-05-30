# %%
from functools import partial
from pathlib import Path
from peft import LoraConfig, get_peft_model

import randomname
import time
import torch
from torch.utils.data.dataloader import DataLoader

from agent import AGENT_DATASET_PATH
from core import BASE_PATH
from core.llm import LLM, Tokenizer, load_lora
from core.utils import num_parameters, MMDD
from training.losses import compute_logit_loss, compute_token_loss
from training.metrics import Aggregator
from training.train_utils import Run, RunConfig, Hyperparameters, iter_or_None
from training.student_teacher_dataset import StudentTeacherDataset, RandomStudentTeacherDataset
from training.train_utils import InfiniteSampler

def train(
    run_cfg: RunConfig,
    hp: Hyperparameters,
) -> None:
    assert run_cfg.val_interval % run_cfg.log_interval == 0, "eval_interval must be divisible by log_interval"

    run = Run(run_cfg, hp)
    accelerator = run.setup()
    verbose = accelerator.is_main_process

    # tokenizer = get_tokenizer(run_cfg)
    # if False:
    #     logit_train_dataloader, len_logit_trainset, logit_val_dataloader = get_data_test(run.devices)
    # else:
    #     logit_train_dataloader, len_logit_trainset, logit_val_dataloader = get_data(tokenizer, hp, run)

    if run_cfg.student is None:
        student, base_llm = create_student(hp, run)
    else:
        student, base_llm = load_student(run)
    tokenizer = Tokenizer(base_llm.tokenizer_id)

    teacher_type = run_cfg.teacher_type

    optimizer = torch.optim.AdamW(student.parameters(), lr=hp.max_lr, weight_decay=hp.weight_decay)

    if run_cfg.checkpoint_interval:
        accelerator.register_for_checkpointing(student)

    #student, optimizer = accelerator.prepare(student, optimizer)
    student = accelerator.prepare(student)
    optimizer = accelerator.prepare(optimizer)
    accelerator.wait_for_everyone()

    if False:
        logit_train_dataloader, len_logit_trainset, logit_val_dataloader = get_data_test(run.devices)
    else:
        logit_train_dataloader, len_logit_trainset, logit_val_dataloader = get_data(tokenizer, hp, run)
    logit_train_dataloader, logit_val_dataloader = accelerator.prepare(logit_train_dataloader, logit_val_dataloader)
    run.print(student)

    hp.set_max_steps(len_logit_trainset, run.devices, verbose)
    hp.set_warmup_steps(verbose)

    iter_logit_train_dataloader = iter_or_None(logit_train_dataloader)

    for step in range(hp.max_steps):
        run.reset_step(step, hp.max_steps)

        # Validation
        if step % run_cfg.val_interval == 0:
            validate(student, teacher_type, logit_val_dataloader, accelerator, run)

        run.reset_step_time()
        lr = hp.adjust_learning_rate(optimizer, step)
        run.add_to_metrics("lr", lr)

        #gc.collect()
        student.train()
        for _ in range(hp.n_logit_micro_batches_per_batch):
            batch = next(iter_logit_train_dataloader)
            run.print_gpu_utilization()

            if run_cfg.loss_type == "xent":
                loss = compute_token_loss(batch, student, verbose=run.is_main_process)
            else:
                loss, _ = compute_logit_loss(batch, student, teacher_type, temperature=hp.temperature, verbose=run.is_main_process, compute_token_loss=False)
            loss = loss.mean()
            #loss = hp.logit_loss_weight * logit_loss / n_logit_micro_batches_per_batch
            accelerator.backward(loss)

        if run_cfg.loss_type == "xent":
            run.add_to_metrics("token_loss", loss)
        else:
            run.add_to_metrics("logit_loss", loss)

        # Process other losses here

        if hp.max_grad_norm:
            accelerator.clip_grad_norm_(student.parameters(), hp.max_grad_norm)
        optimizer.step()
        optimizer.zero_grad()
        run.log_step()

        if run.is_checkpoint_step():
            #accelerator.save_state()
            # For now do not save the optimizer state
            run.save(student, accelerator, base_llm)

    # End of the training loop

    run.save(student, accelerator, base_llm)
    run.print("Done")

def get_data_test(devices: int):
    seq_len = 11000
    logit_train_dataset = RandomStudentTeacherDataset(seq_len=seq_len, batch_size=1, devices=devices)
    infinite_sampler = InfiniteSampler(len(logit_train_dataset))
    logit_train_dataloader = DataLoader(
        logit_train_dataset,
        batch_size=1,
        collate_fn=partial(logit_train_dataset.collate_fn, padding_value=0),
        #shuffle=False,
        sampler=infinite_sampler,
    )
    print(f"Using random data with {len(logit_train_dataset)} samples and seq_len {seq_len}")
    return logit_train_dataloader, len(logit_train_dataset), None


def get_data(llm: LLM, hp: Hyperparameters, run: Run):
    logit_train_dataset = StudentTeacherDataset(
        llm, hp.training_data,
        verbose=run.is_main_process,
        student_dropout_rate=hp.student_dropout_rate,
        max_teacher_seq_len=4096,
    )
    if len(logit_train_dataset) == 0:
        raise ValueError("No logit training data available.")
    run.print("Number of logit training samples:", len(logit_train_dataset))

    infinite_sampler = InfiniteSampler(len(logit_train_dataset))
    logit_train_dataloader = DataLoader(
        logit_train_dataset,
        batch_size=hp.logit_loss_micro_batch_size,
        collate_fn=partial(logit_train_dataset.collate_fn, padding_value=0), # padding_value=2),
        shuffle=False,
        sampler=infinite_sampler,
    )

    logit_valid_dataset = StudentTeacherDataset(
        llm, hp.validation_data, verbose=run.is_main_process,
    )

    logit_val_dataloader = DataLoader(
        logit_valid_dataset,
        batch_size=hp.logit_loss_micro_batch_size,
        collate_fn=partial(logit_valid_dataset.collate_fn, padding_value=0), # padding_value=2),
        shuffle=False,
    )
    if len(logit_valid_dataset) == 0:
        raise ValueError("No logit validation data available.")
    run.print("Number of logit validation samples:", len(logit_valid_dataset))

    return logit_train_dataloader, len(logit_train_dataset), logit_val_dataloader


def create_student(hp: Hyperparameters, run: Run):
    base_llm: LLM = run.run_cfg.base_model

    if hp.lora_target_modules == "full":
        target_modules = [
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
            "lm_head",
        ]
    elif hp.lora_target_modules == "qk":
        target_modules=["q_proj", "k_proj"]
    elif hp.lora_target_modules == "qv":
        target_modules = ["q_proj", "v_proj"]
    else:
        raise ValueError(f"Invalid lora_target_modules: {hp.lora_target_modules}")
    peft_config = LoraConfig(
        r=hp.lora_r,
        lora_alpha=hp.lora_r*2,
        target_modules=target_modules,
        lora_dropout=0.05,
    )
    run.print_gpu_utilization()
    model = base_llm.load_model(training=True)
    run.print(f"Number of trainable parameters: {num_parameters(model, requires_grad=True):,}")
    run.print(f"Number of fixed parameters: {num_parameters(model, requires_grad=False):,}")
    run.print_gpu_utilization()

    if run.run_cfg.gradient_checkpointing:
        model.gradient_checkpointing_enable()

    lora_model = get_peft_model(model, peft_config, autocast_adapter_dtype=False)

    run.print(lora_model)
    run.print(f"Number of trainable parameters: {num_parameters(lora_model, requires_grad=True):,}")
    run.print(f"Number of fixed parameters: {num_parameters(lora_model, requires_grad=False):,}")
    run.print_gpu_utilization()

    return lora_model, base_llm


def load_student(run: Run):
    student_llm: LLM = run.run_cfg.student

    assert len(student_llm.adapter_ids) == 1, f"Adapter chains are not supported yet (chain {student_llm.adapter_ids})"
    adapter_id = student_llm.adapter_ids[0]
    run.print(f"Base model: {student_llm.model_id}")
    run.print(f"Adapter: {adapter_id}")

    base_llm = LLM(student_llm.model_id, [], student_llm.tokenizer_id)
    model = base_llm.load_model(training=True)
    # In priciple, the model could be loaded by the line below but it has not been tested
    # lora_model = student_llm.load_model(training=True, merge=False)
    run.print_gpu_utilization()

    if run.run_cfg.gradient_checkpointing:
        model.gradient_checkpointing_enable()

    lora_model = load_lora(model, adapter_id)

    run.print(lora_model)
    run.print(f"Number of trainable parameters: {num_parameters(lora_model, requires_grad=True):,}")
    run.print(f"Number of fixed parameters: {num_parameters(lora_model, requires_grad=False):,}")
    run.print_gpu_utilization()

    return lora_model, base_llm

def validate(student, teacher_type, logit_dataloader, accelerator, run):
    if run.is_main_process:
        assert run.is_logging_step, "Validation should only be done at logging steps"

    student.eval()
    metrics = {}
    with torch.no_grad():
        # if token_dataloader is not None:
        #     ...

        t0 = time.perf_counter()
        if logit_dataloader is not None:
            group_names = logit_dataloader.dataset.lesson_names
            aggregator = Aggregator(group_names, accelerator.device)
            for batch in logit_dataloader:
                if run.run_cfg.loss_type == "xent":
                    token_loss = compute_token_loss(batch, student, reduction="sample")
                    batch_metrics = {"val_token_loss": token_loss}
                else:
                    logit_loss, token_loss = compute_logit_loss(batch, student, teacher_type, temperature=1, reduction="sample", compute_token_loss=True)
                    batch_metrics = {
                        "val_logit_loss": logit_loss,
                        "val_token_loss": token_loss,
                    }
                aggregator.add_batch(batch["lesson_ixs"], batch_metrics, accelerator)
            logit_metrics_total, logit_metrics_by_group = aggregator.get_average()
            metrics.update(logit_metrics_total)
            metrics.update(logit_metrics_by_group)

    metrics["val_time"] = time.perf_counter() - t0
    run.add_dict_to_metrics(metrics)
    run.print("Validation results:", metrics)


# Create your own main function, see an example in train_config.py
def main(run_name: str = None):
    # These are the most important settings
    project_name = "agent-llama3.1-70b"
    group_name = "information-extraction"
    notes = "Info extraction, new browsers, fixed data, removed runs with errors"
    # student = None  # Use an adapter name to continue training
    # student = "1007_pureed-tint"
    # student = "1007_distinct-joule-1"
    # student = "1007_pureed-tint-1"
    student = None
    base_model = "meta-llama/Meta-Llama-3.1-70B-Instruct"
    # train_patterns = ["0928_*_train/xml", "0925_browsing*_train/xml"]
    train_patterns = ["1009_*_train/xml", "1009_browsing*_train/xml"]
    val_patterns = ["0926_extraction*_test/xml"]
    n_epochs = 6

    # patterns = ["0802_extraction_train/xml", "0802_browsing_train/xml"]
    # patterns = ["0802_extraction_test/xml"]

    # base_model="0802_happy-crypt-1",  # Use an adapter's short name, e.g. "0802_happy-crypt-1": this hangs for some reason
    # base_model=MODEL_PATH / project_name / "0802_happy-crypt-1",  # Use a merged model

    use_wandb = True
    if run_name is None:
        if use_wandb:
            run_name = MMDD() + "_" + randomname.get_name()
        else:
            run_name = "test"

    run_cfg = RunConfig(
        project_name=project_name,
        run_name=run_name,
        group_name=group_name,
        project_path = BASE_PATH / "checkpoints" / project_name,
        checkpoint_interval=20,
        val_interval=10,
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
    for pattern in train_patterns:
        for dataset_path in list(data_path.glob(pattern)):
            training_data.extend(list(dataset_path.glob('*.xml')))

    validation_data = []
    for pattern in val_patterns:
        for dataset_path in list(data_path.glob(pattern)):
            validation_data.extend(list(dataset_path.glob('*.xml')))

    hp = Hyperparameters(
        training_data=training_data,
        validation_data=validation_data,
        max_lr=1e-5,
        # max_steps=5,
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
    #main()
