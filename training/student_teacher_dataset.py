# %%
import copy
from dataclasses import dataclass
from pathlib import Path
from platform import system
import xml.etree.ElementTree as ET
from typing import Literal, Union

import random
import torch
from torch.nn.utils.rnn import pad_sequence

from core.chat_templates import SYSTEM_MESSAGES
from core.llm import Tokenizer
from core.messages import Message
from core.utils import xml_decoder


class STMessage:
    """A message to carry the information needed for creating token sequences and their masks.

    Only assistant messages have the start sequence and can be targets.
    Only the message content and stop sequence belong to the target."""
    def __init__(
            self,
            content: str | None,  # Does not include the possible start and stop sequences
            role: Literal["system", "user", "assistant"],
            start_seq: str = "",
            is_target: bool = False,
    ):
        self.content = content or ""
        self.role = role
        if role in ["system", "user"] and (start_seq or is_target):
            raise ValueError(f"When role is system or user, no start sequence ({start_seq=}) or target allowed ({is_target=})")
        self.start_seq = start_seq
        self.is_target = is_target

    @classmethod
    def from_message(cls, msg: Message) -> "STMessage":
        return cls(msg.content, msg.role.value)

    def __iadd__(self, txt):
        if txt:
            self.content += txt
        return self

    def __str__(self):
        return str(self.content)

    def __repr__(self):
        return f"STMessage({repr(self.content)}, {repr(self.role)}, {repr(self.start_seq)}, {self.is_target})"

    @classmethod
    def from_system_or_user_element(cls, msg: ET.Element, role: Literal["teacher", "student"]) -> "STMessage":
        result = cls(msg.text, msg.tag)
        for child in msg:
            if child.tag in [role, "both"]:
                result += child.text
            result += child.tail
        return result


def validate_exercise(exercise: ET.Element):
    if exercise.text.strip():
        raise RuntimeError(f"No text allowed before messages\n{exercise}")
    for msg in exercise:
        if msg.tail and msg.tail.strip():
            raise RuntimeError(f"No text allowed after or between messages\n{exercise}")
        if msg.tag not in ["user", "assistant", "system", "assistant_target", "metadata"]:
            raise RuntimeError(f"Unknown message tag {msg.tag}")
        if len(msg.attrib) > 1:
            raise RuntimeError("Only one attribute allowed in '{msg.tag}'")
        if msg.tag == "user" or msg.tag == "system":
            for child in msg:
                if len(child):
                    raise RuntimeError(f"Nested tags detected inside {child.tag} of {msg.tag}")
                if child.tag not in ["teacher", "student", "both", "student_dropout"]:
                    raise RuntimeError(f"Unknown tag {child.tag} inside <user>")
            if msg.attrib:
                if "recipient" not in msg.attrib:
                    raise RuntimeError(f"Unknown attribute {msg.attrib} in 'user'")
                if (recipient := msg.attrib["recipient"]) not in ["teacher", "student", "both", "student_dropout"]:
                    raise RuntimeError(f"Unknown recipient attribute {recipient} in <user>")
        elif msg.tag != "metadata":
            if len(msg):
                raise RuntimeError(f"No tags allowed inside {msg.tag}")
            if msg.attrib:
                if "response_format" not in msg.attrib:
                    raise RuntimeError(f"Unknown attribute {msg.attrib} in '{msg.tag}'")
    if len(exercise) == 0 or msg.tag != "assistant_target":
        raise RuntimeError("The last message should be 'assistant_target'")

def exercise_to_messages(exercise: ET.Element) -> tuple[list[STMessage], list[STMessage]]:
    "Convert an exercise to student and teacher messages."
    student_msgs = []
    teacher_msgs = []
    for msg_element in exercise:
        if msg_element.tag == "user" or msg_element.tag == "system":
            recipient = msg_element.attrib.get("recipient", "both")
            if recipient in ["student", "both"]:
                student_msgs.append(STMessage.from_system_or_user_element(msg_element, "student"))
            if recipient in ["teacher", "both"]:
                teacher_msgs.append(STMessage.from_system_or_user_element(msg_element, "teacher"))
        elif msg_element.tag != "metadata":
            msg = STMessage(
                content=msg_element.text,
                role="assistant",
                start_seq=msg_element.attrib.get("response_format", ""),
                is_target=msg_element.tag == "assistant_target",
            )
            student_msgs.append(msg)
            teacher_msgs.append(msg)
    return student_msgs, teacher_msgs


@dataclass
class AgentExercise:
    lesson_name: str  # Name of the lesson
    exercise_element: ET.Element  # XML element of the exercise
    lesson_ix: int = None  # Index of the lesson in the dataset

    def validate(self):
        validate_exercise(self.exercise_element)

    def to_deterministic_exercise(self, dropout_rate: float = 0.5) -> "AgentExercise":
        """Return a copy of the exercise with <student_dropout> randomly replaced by <teacher> or <both>."""

        new_exercise = copy.deepcopy(self)
        for msg_element in new_exercise.exercise_element:
            if msg_element.tag == "user":
                if (recipient := msg_element.attrib.get("recipient", "both")) == "both":
                    for child in msg_element:
                        if child.tag == "student_dropout":
                            child.tag = "both" if random.random() > dropout_rate else "teacher"
                elif recipient == "student_dropout":
                    msg_element.attrib["recipient"] = "both" if random.random() > dropout_rate else "teacher"
        return new_exercise

    def to_sample(self, tokenizer: Tokenizer, dropout_rate: float = 0.5, sysmsg_type: str = "llama") -> dict[str, torch.Tensor]:
        """Convert the exercise to a sample that contains tokens. Random dropout if there are <student_dropout> elements."""

        student_msgs, teacher_msgs = exercise_to_messages(
            self.to_deterministic_exercise(dropout_rate=dropout_rate).exercise_element
        )
        if sysmsg_type is not None:
            sysmsg = STMessage(content=SYSTEM_MESSAGES[sysmsg_type], role="system")
            student_msgs = [sysmsg] + student_msgs
            teacher_msgs = [sysmsg] + teacher_msgs

        student_seq, student_mask = tokenize_messages(student_msgs, tokenizer)
        teacher_seq, teacher_mask = tokenize_messages(teacher_msgs, tokenizer)

        return {
            "student_seq": student_seq,  # (1, student_seq_len)
            "student_mask": student_mask,  # (1, student_seq_len)
            "teacher_seq": teacher_seq,  # (1, teacher_seq_len)
            "teacher_mask": teacher_mask,  # (1, teacher_seq_len)
            "lesson_ix": self.lesson_ix,  # int
        }

    def get_student_seq_len(self, tokenizer: Tokenizer) -> int:
        # This function is meant to be used for deterministic exercises, so dropout_rate is set to 0
        sample = self.to_sample(tokenizer, dropout_rate=0)
        return sample["student_seq"].shape[1]

    def __str__(self):
        return (
            "AgentExercise\n"
            f"lesson_name: {self.lesson_name},\n"
            f"exercise_element:\n{ET.tostring(self.exercise_element, encoding='unicode')}"
        )


# %%
def read_exercises(
    filepath: Path,
    must_exist: bool = False,  # Raise error if file does not exist
    must_parse: bool = False,  # Raise error if parsing fails
    verbose: bool = True,
) -> Union[list[AgentExercise], None]:

    if not (filepath).exists():
        if must_exist:
            raise FileNotFoundError(f"{filepath}: not found")
        if verbose:
            print(f"{filepath}: not found")
        return None

    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except Exception as e:
        if must_parse:
            raise ValueError(f"Processing {filepath} failed: {e}") from e

        if verbose:
            print(f"Processing {filepath} failed: {e}")
        return None

    lesson_name = filepath.stem
    agent_exercises = []
    for elem in root.findall("exercise"):
        ex = AgentExercise(lesson_name, elem)
        try:
            ex.validate()
            agent_exercises.append(ex)
        except Exception as e:
            if must_parse:
                raise ValueError(f"Processing {filepath} failed: {e}") from e
    return agent_exercises


def tokenize_messages(msgs: list[STMessage], tokenizer: Tokenizer) -> tuple[torch.Tensor, torch.Tensor]:
    if tokenizer.model_family != "llama":
        raise NotImplementedError("Only llama tokenisation implemented.")
    token_tuples = [(torch.tensor([[tokenizer.tokenizer.bos_token_id]]), False)]
    for msg in msgs:
        header = f"<|start_header_id|>{msg.role}<|end_header_id|>\n\n"
        token_tuples.append((tokenizer.tokenize(header), False))
        if msg.start_seq:
            token_tuples.append((tokenizer.tokenize("<" + msg.start_seq + ">\n"), False))
        content = msg.content
        if msg.start_seq:
            content += "</" + msg.start_seq + ">"
        if content:
            token_tuples.append((tokenizer.tokenize(xml_decoder(content)), msg.is_target))
        token_tuples.append((torch.tensor([[tokenizer.tokenizer.eos_token_id]]), msg.is_target))
    prompt = []
    mask = []
    for tokens, is_target in token_tuples:
        prompt.append(tokens)
        mask.append(torch.ones_like(tokens, dtype=torch.bool) * is_target)
    return torch.cat(prompt, dim=1), torch.cat(mask, dim=1)


class StudentTeacherDataset(torch.utils.data.Dataset):
    def __init__(
        self,
        tokenizer: Tokenizer,
        filepaths: list[Path],  # list of paths to xml files,
        verbose: bool = False,
        strict: bool = False,  # Fail with errors
        max_teacher_seq_len: int = 8192,  # Maximum length of teacher sequence
        student_dropout_rate: float = 0.5,
        sysmsg_type: str = "llama",
    ):
        self.tokenizer = tokenizer
        self.student_dropout_rate = student_dropout_rate
        self.verbose = verbose
        self.sysmsg_type = sysmsg_type
        self._print("==== StudentTeacherDataset ====", flush=True)
        self.exercises: list[AgentExercise] = []
        self.lesson_names = []  # Needed to group validation results by lesson
        filepaths = list(filepaths)
        if len(filepaths) == 0:
            self._print("No exercise files found")
            return

        for lesson_ix, filepath in enumerate(filepaths):
            exercises = read_exercises(filepath, must_exist=strict, must_parse=strict, verbose=verbose)
            if not exercises:
                self._print(f"No exercises found in {filepath}")
                continue
            lesson_name = exercises[0].lesson_name
            teacher_seq_lens = [ex.to_sample(tokenizer, sysmsg_type=self.sysmsg_type)["teacher_seq"].size(1) for ex in exercises]
            self._print(f"\n{lesson_name}:")
            self._print(f"  found {len(exercises)} exercises")
            self._print(f"  teacher_seq_lens: {teacher_seq_lens}")
            exercises = [
                ex
                for ex, tsl in zip(exercises, teacher_seq_lens, strict=True)
                if tsl <= max_teacher_seq_len
            ]
            self._print(f"  kept {len(exercises)} exercises with teacher_seq_len <= {max_teacher_seq_len}")
            for ex in exercises:
                ex.lesson_ix = lesson_ix
            self.exercises.extend(exercises)
            self.lesson_names.append(lesson_name)
        self._print("==== /StudentTeacherDataset ====", flush=True)

    def _print(self, *args, **kw):
        if self.verbose:
            print(*args, **kw)

    def __len__(self):
        return len(self.exercises)

    def __getitem__(self, idx) -> AgentExercise:
        return self.exercises[idx]

    def collate_fn(self, exercises: list[AgentExercise], padding_value: int):
        student_seqs = []
        student_masks = []
        teacher_seqs = []
        teacher_masks = []
        lesson_ixs = []

        for exercise in exercises:
            sample = exercise.to_sample(self.tokenizer, dropout_rate=self.student_dropout_rate, sysmsg_type=self.sysmsg_type)
            lesson_ixs.append(sample["lesson_ix"])
            student_seqs.append(sample["student_seq"][0])
            student_masks.append(sample["student_mask"][0])
            teacher_seqs.append(sample["teacher_seq"][0])
            teacher_masks.append(sample["teacher_mask"][0])

        student_seqs = pad_sequence(student_seqs, batch_first=True, padding_value=padding_value)
        student_masks = pad_sequence(student_masks, batch_first=True, padding_value=0).bool()

        teacher_seqs = pad_sequence(teacher_seqs, batch_first=True, padding_value=padding_value)
        teacher_masks = pad_sequence(teacher_masks, batch_first=True, padding_value=0).bool()

        lesson_ixs = torch.tensor(lesson_ixs)

        return {
            'student_seqs': student_seqs,
            'student_masks': student_masks,
            'teacher_seqs': teacher_seqs,
            'teacher_masks': teacher_masks,
            'lesson_ixs': lesson_ixs,
        }


class RandomStudentTeacherDataset(torch.utils.data.Dataset):
    def __init__(self, seq_len: int, batch_size: int, devices: int):
        self.seq_len = seq_len
        self.batch_size = batch_size
        self.devices = devices
        self.teacher_answer_len = 200
        if self.seq_len < self.teacher_answer_len:
            self.teacher_answer_len = self.seq_len
            print("Warning: teacher_answer_len is greater than seq_len")

    def __len__(self):
        return 32

    def __getitem__(self, _idx):
        return None

    def collate_fn(self, _samples, _padding_value):
        student_seqs = torch.randint(0, 100, (self.batch_size, self.seq_len))
        student_masks = torch.zeros_like(student_seqs, dtype=torch.bool)
        student_masks[:, -self.teacher_answer_len:] = 1
        teacher_seqs = torch.randint(0, 100, (self.batch_size, self.seq_len))
        teacher_masks = torch.zeros_like(teacher_seqs, dtype=torch.bool)
        teacher_masks[:, -self.teacher_answer_len:] = 1
        lesson_ixs = torch.zeros(self.batch_size)

        return {
            'student_seqs': student_seqs,
            'student_masks': student_masks,
            'teacher_seqs': teacher_seqs,
            'teacher_masks': teacher_masks,
            'lesson_ixs': lesson_ixs,
        }
