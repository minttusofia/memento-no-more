from __future__ import annotations
import os
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET

from .messages import Message
from agent.configs import Metadata


class StepMessages(list[Message]):
    """StepMessages holds the messages of a single agent step.
    It behaves like list[Message] except it also holds a dictionary of metadata."""
    def __init__(self, iterable: Iterable[Message] = (), metadata: Metadata = None):
        super().__init__(iterable)
        self.metadata = Metadata() if not metadata else Metadata(metadata)

    def __repr__(self):
        return f"{self.__class__.__name__}({super().__repr__()}, metadata={self.metadata})"

    def __add__(self, other: Iterable[Message]) -> StepMessages:
        if hasattr(other, "metadata"):
            raise TypeError("Cannot add Step + Step")
        return StepMessages(list(self) + other, metadata=self.metadata)

    def __iadd__(self, messages: Iterable[Message]) -> StepMessages:
        if hasattr(messages, "metadata"):
            raise TypeError("Cannot add Step + Step")
        for msg in messages:
            self.append(msg)
        return self

    def extend(self, messages: Iterable[Message]):
        self.__iadd__(messages)

    def to_xml_element(self) -> ET.Element:
        element = ET.Element("step_messages")
        for msg in self:
            element.append(msg.to_xml())
        metadata = ET.Element("metadata")
        metadata.text = self.metadata.to_json()
        element.append(metadata)
        return element

    @classmethod
    def from_xml_element(cls, element: ET.Element):
        messages = [Message.from_xml_element(msg) for msg in element.findall("message")]
        metadatas = [Metadata.from_json(meta.text) for meta in element.findall("metadata")]
        if len(metadatas) > 1:
            raise SyntaxError(f"More than one metadata in {element}")
        return cls(messages, metadata=metadatas[0] if metadatas else None)

    @classmethod
    def from_xml_path(cls, path: Path):
        return cls.from_xml_element(ET.parse(path).getroot())

    def to_xml_path(self, path: os.PathLike):
        element = self.to_xml_element()
        tree = ET.ElementTree(element)
        ET.indent(tree, space="", level=0)
        tree.write(path, encoding="unicode", xml_declaration=True)
