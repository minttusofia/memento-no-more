from contextlib import nullcontext
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM
from typing import Literal

from training import IGNORE_INDEX


def compute_logit_loss(
    batch,
    student: AutoModelForCausalLM,
    teacher_type: Literal["student", "student_base", "model"],
    temperature,
    reduction: Literal["batch", "sample"] = "sample",  # "batch" is not currently used anywhere
    teacher: AutoModelForCausalLM = None,
    verbose: bool = True,
    compute_token_loss: bool = False,
):
    assert reduction in ["batch", "sample"]
    assert teacher_type in ["student", "student_base", "model"]
    if teacher_type == "model":
        assert isinstance(teacher, AutoModelForCausalLM), "teacher must be an instance of AutoModelForCausalLM"

    student_inputs = batch['student_seqs'][..., :-1]  # (batch_size, seq_length)
    student_masks = batch['student_masks'][..., 1:]  # (batch_size, seq_length)

    batch_size, seq_length = student_inputs.shape

    teacher_context = student.disable_adapter() if teacher_type == "student_base" else nullcontext()
    if teacher_type != "model":
        teacher = student

    with torch.no_grad(), teacher_context:
        teacher.eval()
        teacher_inputs = batch['teacher_seqs'][..., :-1]
        # The mask determines which outputs should be used for loss calculation
        teacher_masks = batch['teacher_masks'][..., 1:]
        teacher_output = teacher.forward(teacher_inputs)
        teacher_logits = teacher_output.logits[teacher_masks].clone()
        del teacher_output
        torch.cuda.empty_cache()

    student.train()  # This is important! If we use "student_base" as a teacher, doing teacher.eval() seems
                     # to break things. For example, gradient checkpointing did not work without this line.
    student_output = student.forward(student_inputs)
    student_logits = student_output.logits[student_masks]

    if compute_token_loss:
        student_labels = batch["student_seqs"][batch["student_masks"]]
        token_loss = F.cross_entropy(
            student_logits,
            student_labels,
            ignore_index=IGNORE_INDEX,
            reduction="mean" if reduction == "batch" else "none"
        )  # for "sample" reduction: (n_tokens,)
    else:
        token_loss = None

    s_logits = student_logits / temperature  # (n_tokens, vocab_size)
    t_logits = teacher_logits / temperature  # (n_tokens, vocab_size)

    s_log_probs = F.log_softmax(s_logits, dim=-1)
    t_log_probs = F.log_softmax(t_logits, dim=-1)
    logit_loss = F.kl_div(
        s_log_probs, t_log_probs, log_target=True,
        reduction="batchmean" if reduction == "batch" else "none"
    )  # for "sample" reduction: (n_tokens, vocab_size)

    if reduction == "sample":
        logit_loss_t = logit_loss.sum(-1)  # (n_tokens,)

        logit_loss_mx = torch.zeros(batch_size, seq_length, device=student_inputs.device)
        logit_loss_mx[student_masks] = logit_loss_t
        logit_loss = logit_loss_mx.sum(-1) / student_masks.sum(-1)  # (batch_size,)

        if compute_token_loss:
            token_loss_mx = torch.zeros(batch_size, seq_length, device=student_inputs.device)
            token_loss_mx[student_masks] = token_loss
            token_loss = token_loss_mx.sum(-1) / student_masks.sum(-1)  # (batch_size,)

    return logit_loss, token_loss


def compute_token_loss(
    batch,
    student: AutoModelForCausalLM,
    reduction: Literal["batch", "sample"] = "sample",  # "batch" is not currently used anywhere
    verbose: bool = True,
):
    student_inputs = batch['student_seqs'][..., :-1]  # (batch_size, seq_length)
    student_masks = batch['student_masks'][..., 1:]  # (batch_size, seq_length)

    batch_size, seq_length = student_inputs.shape

    student.train()
    student_output = student.forward(student_inputs)
    student_logits = student_output.logits[student_masks]

    student_labels = batch["student_seqs"][batch["student_masks"]]

    token_loss = F.cross_entropy(
        student_logits,
        student_labels,
        ignore_index=IGNORE_INDEX,
        reduction="mean" if reduction == "batch" else "none"
    )  # for "sample" reduction: (n_tokens,)

    if reduction == "sample":
        token_loss_mx = torch.zeros(batch_size, seq_length, device=student_inputs.device)
        token_loss_mx[student_masks] = token_loss
        token_loss = token_loss_mx.sum(-1) / student_masks.sum(-1)  # (batch_size,)

    return token_loss
