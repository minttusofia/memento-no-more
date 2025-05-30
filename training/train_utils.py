from accelerate import Accelerator
from accelerate.utils import ProjectConfiguration
from dataclasses import dataclass
import copy
import json
import math
import os
from pathlib import Path
import pprint
import sys
import time
import torch
from torch.utils.data import Sampler
from typing import Literal
import wandb

from agent import AGENT_DATASET_PATH
from core.llm import LLM
from core.putils import print_gpu_utilization, print_gpu_utilization_cuda
from core.utils import DualOutput


@dataclass
class Hyperparameters:
    training_data: list[Path]  # Paths to xml files
    validation_data: list[Path]  # Paths to xml files

    max_lr: float
    logit_loss_micro_batch_size: int
    n_logit_micro_batches_per_batch: int
    weight_decay: float
    temperature: float
    n_epochs: int = 1
    max_grad_norm: float = 1.0  # This seems to produce better results
    max_steps: int = None  # None means derived from n_epochs
    lr_decay: bool = False
    warmup_steps: int = 0  # None means using warmup_ratio
    warmup_ratio: float = None

    lora_target_modules: Literal["full", "qk", "qv"] = "full"
    lora_r: int = 512

    student_dropout_rate: float = 0.5

    run_cfg: dict = None  # This is used for logging run_cfg in wandb

    def set_max_steps(self, len_dataset, devices, verbose):
        if self.max_steps is not None:
            if self.n_epochs is not None and verbose:
                print("Warning: n_epochs is ignored when max_steps is set")
            return

        n_batches = math.ceil(
            len_dataset / self.n_logit_micro_batches_per_batch
            / self.logit_loss_micro_batch_size / devices
        )
        self.max_steps = self.n_epochs * n_batches
        if verbose:
            print(f"Training for {self.n_epochs} epochs, {self.max_steps} steps", flush=True)

    def set_warmup_steps(self, verbose):
        if self.warmup_steps is None and self.warmup_ratio:
            self.warmup_steps = int(self.warmup_ratio * self.max_steps)
        if verbose:
            print(f"Learning rate warmup: {self.warmup_steps} steps", flush=True)

    def adjust_learning_rate(self, optimizer, step: int):
        max_steps = self.max_steps
        warmup_steps = self.warmup_steps

        lr = self.max_lr
        if step <= warmup_steps and warmup_steps:
            # linear warmup
            lr = self.max_lr * step / warmup_steps
        else:
            if self.lr_decay:
                multiplier = max(0.0, float(max_steps - step) / float(max(1, max_steps - warmup_steps)))
                lr = self.max_lr * multiplier

        for param_group in optimizer.param_groups:
            param_group["lr"] = lr

        return lr

@dataclass
class RunConfig:
    project_name: str
    run_name: str
    project_path: Path
    group_name: str

    base_model: LLM
    student: LLM = None  # Specify an existing adapter's name to continue training
    teacher_type: Literal["student_base", "student"] = "student_base"
    loss_type: Literal["kl", "xent"] = "kl"

    gradient_checkpointing: bool = False
    fsdp: bool = True
    mixed_precision: str = "bf16"

    val_interval: int = 0  # zero means no validation
    log_interval: int = 1
    generation_interval: int = 0
    checkpoint_interval: int = 0  # zero means no checkpointing
    use_wandb: bool = False
    notes: str = None  # Notes to be added on wandb

    @property
    def run_path(self):
        return self.project_path / self.run_name

    def to_dict(self):
        d = self.__dict__.copy()
        d["project_path"] = str(d["project_path"])
        d["run_path"] = str(self.run_path)
        return d

def iter_or_None(dataloader):
    return None if dataloader is None else iter(dataloader)

@dataclass
class Config:
    hp: Hyperparameters
    run_cfg: RunConfig

class Run:
    def __init__(
        self,
        run_cfg: RunConfig,
        hp: Hyperparameters,
    ):
        self.run_cfg = run_cfg
        self.hp = hp

        # These are set in setup()
        self.is_main_process = None
        self.is_rocm = "rocm" in torch.__version__
        self.devices = None

        self.metrics = {}
        self.step = None
        self.max_steps = None
        self.step_t0 = None

    @property
    def run_path(self):
        return self.run_cfg.project_path / self.run_cfg.run_name

    def setup(self):
        run_cfg = self.run_cfg

        fsdp_plugin = get_fsdp_plugin(activation_checkpointing=run_cfg.gradient_checkpointing) if run_cfg.fsdp else None
        accelerator = Accelerator(
            mixed_precision=run_cfg.mixed_precision,
            project_dir=run_cfg.run_path,
            project_config=ProjectConfiguration(automatic_checkpoint_naming=True),
            fsdp_plugin=fsdp_plugin,
        )

        self.is_main_process = accelerator.is_main_process
        if self.is_main_process:
            self.make_run_dir()

        self.log_to_wandb = self.is_main_process and self.run_cfg.use_wandb

        self.devices = accelerator.state.num_processes if run_cfg.fsdp else 1
        self.setup_print_output(accelerator.process_index)
        self.setup_wandb()
        self.print("run_name:", run_cfg.run_name)
        self.print("Hyperparameters:")
        self.pprint(self.hp)

        return accelerator

    def print(self, *args, **kwargs):
        kwargs["flush"] = True
        if self.is_main_process:
            print(*args, **kwargs)

    def pprint(self, *args, **kwargs):
        if self.is_main_process:
            pprint.pprint(*args, **kwargs)

    def print_gpu_utilization(self):
        if self.is_main_process:
            print_gpu_utilization_cuda() if not self.is_rocm else print_gpu_utilization()

    def make_run_dir(self):
        os.makedirs(self.run_path, exist_ok=True)

    def set_main_process(self, is_main_process):
        self.is_main_process = is_main_process
        self.log_to_wandb = is_main_process and self.run_cfg.use_wandb

    def setup_print_output(self, process_index):
        if self.is_main_process:
            output_log = self.run_path / f"output_{process_index}.log"
            # Set the output to the console and to a file
            sys.stdout = DualOutput(output_log)

    def setup_wandb(self):
        run_cfg = self.run_cfg
        if self.is_main_process and run_cfg.use_wandb:
            wandb_config = copy.copy(self.hp)
            wandb_config.run_cfg = run_cfg.to_dict()
            training_data = get_relative_path(self.hp.training_data)
            wandb_config.training_data = group_files(training_data)

            validation_data = get_relative_path(self.hp.validation_data)
            wandb_config.validation_data = group_files(validation_data)

            wandb.init(
                project=run_cfg.project_path.name,
                name=run_cfg.run_name,
                group=run_cfg.group_name,
                allow_val_change=True,
                config=wandb_config,
                notes=run_cfg.notes,
            )

    def is_checkpoint_step(self):
        return self.run_cfg.checkpoint_interval and ((self.step+1) % self.run_cfg.checkpoint_interval == 0)

    def reset_step(self, step: int, max_steps: int):
        self.step = step
        self.max_steps = max_steps
        self.metrics = {}

    def reset_step_time(self):
        self.step_t0 = time.perf_counter()

    @property
    def is_logging_step(self):
        return self.is_main_process and (self.step % self.run_cfg.log_interval == 0)

    def add_to_metrics(self, key: str, value):
        # Note: If value is a pytorch tensor, pass it instead of value.item()

        # We log only if we are in the logging step
        if not self.is_logging_step:
            return

        if isinstance(value, torch.Tensor):
            value = value.item()  # expensive device-to-host synchronization

        self.metrics[key] = value

    def add_dict_to_metrics(self, d: dict):
        # Note: If value is a pytorch tensor, pass it instead of value.item()
        # We log only if we are in the logging step
        if not self.is_logging_step:
            return

        d = {k: v.item() if isinstance(v, torch.Tensor) else v for k, v in d.items()}
        self.metrics.update(d)

    def log_step(self):
        if not self.is_logging_step:
            return

        # Note: we log the one-batch loss for the main process
        # To gather losses across devices, we should do something like
        # losses = accelerator.gather(loss)
        # loss_item = losses.mean().item()
        t1 = time.perf_counter()
        loss_key = "logit_loss" if "logit_loss" in self.metrics else "token_loss"
        print(
            f"Step {self.step + 1}/{self.max_steps}: "
            f"{loss_key} {self.metrics[loss_key]:.8f}, "
            f"iter time: {(t1 - self.step_t0) * 1000:.2f}ms",
            flush=True
        )
        if self.log_to_wandb:
            self.metrics['step_time'] = (t1 - self.step_t0) * 1000
            wandb.log(self.metrics, self.step)

    def save_base_model_config(self, model, base_llm):
        if self.is_main_process:
            run_path = self.run_path
            with open(run_path / "base_model_config.json", 'w', encoding='utf-8') as f:
                json.dump(base_llm.get_config(), f, ensure_ascii=False, indent=4)
            self.print(f"Saved to {run_path}")

    def _save_fsdp(self, model, accelerator, base_llm, verbose=False):
        accelerator.wait_for_everyone()
        unwrapped_model = accelerator.unwrap_model(model)

        # Not using unwrap=False makes some parameters empty (zero shape)
        state_dict = accelerator.get_state_dict(model, unwrap=False)
        # Parameters that contain "base_layer" in their name do not belong to the adapter
        # There is a bug which adds "base_layer" of "lm_head" to the adapter's parameters
        # This matrix is the largest in the model and it consumes a lot of memory
        # We remove such parameters from the adapter
        state_dict = {k: v for k, v in state_dict.items() if "base_layer" not in k}
        if verbose:
            print("Shapes of state_dict before saving:")
            for name, weight in state_dict.items():
                print(name, weight.shape, weight.requires_grad)
        unwrapped_model.save_pretrained(
            self.run_path,
            is_main_process=accelerator.is_main_process,
            save_function=accelerator.save,
            state_dict=state_dict,
        )

    def save(self, model, accelerator, base_llm, verbose=False):
        if self.run_cfg.fsdp:
            self._save_fsdp(model, accelerator, base_llm, verbose)
        else:
            model.save_pretrained(self.run_path)
        self.save_base_model_config(model, base_llm)

        if accelerator.is_main_process:
            # If the adapter was created not with get_peft_model, the adapter is saved in a subfolder
            # We move it one level up
            adapter_name = model.active_adapters[0]
            move_adapter_to_parent(self.run_path, adapter_name)

def print_batch(batch, process_index, step):
    print(
        f"s{step}-{process_index}: {batch['student_seqs'].shape[1]}, "
        f"{batch['teacher_seqs'].shape[1]}, {batch['teacher_masks'].sum(dim=1)[0]}"
    )

def move_adapter_to_parent(run_path, adapter_name):
    adapter_path = run_path / adapter_name
    if adapter_path.exists():
        # Move all files from adapter_path to run_path
        for f in adapter_path.iterdir():
            f.rename(run_path / f.name)

        # Remove the adapter directory
        adapter_path.rmdir()

def get_relative_path(data: list[Path]):
    # If training data is in AGENT_DATASETPATH, we save paths relative to AGENT_DATASETPATH
    dataset_path = AGENT_DATASET_PATH.resolve()
    relative_paths = []
    for path in data:
        file_path = path.resolve()
        try:
            relative_paths.append(file_path.relative_to(dataset_path))
        except ValueError:
            relative_paths.append(file_path)

    return relative_paths


def group_files(files: list[Path]):
    parent_files = [(str(f.parent), f.name) for f in files]
    grouped_files = {}
    for parent, name in parent_files:
        if parent not in grouped_files:
            grouped_files[parent] = []
        grouped_files[parent].append(name)

    return grouped_files


class InfiniteSampler(Sampler):
    def __init__(self, data_source_length):
        self.data_source_length = data_source_length

    def __iter__(self):
        while True:
            yield from torch.randperm(self.data_source_length)

    def __len__(self):
        return float('inf')


def get_fsdp_plugin(activation_checkpointing: bool = False):
    from torch.distributed.fsdp.fully_sharded_data_parallel import FullOptimStateDictConfig, FullStateDictConfig
    from accelerate import FullyShardedDataParallelPlugin

    fsdp_plugin = FullyShardedDataParallelPlugin(
        state_dict_config=FullStateDictConfig(offload_to_cpu=True, rank0_only=True),
        optim_state_dict_config=FullOptimStateDictConfig(offload_to_cpu=True, rank0_only=True),
        activation_checkpointing=activation_checkpointing,
    )
    return fsdp_plugin


def get_full_run_name(project_dir: Path, short_name: str) -> str:
    full_run_name = next((sub
        for sub in os.listdir(project_dir)
        if os.path.isdir(os.path.join(project_dir, sub)) and short_name in sub
    ), None)
    return full_run_name

