import os
from typing import Union, Iterable
from xml.etree import ElementTree as ET

from core.messages import Message
from core.steps import StepMessages
from core.tags import Tag

class History:
    """History holds and manages the agent messages which are needed for running a single step."""
    def __init__(self):
        self.messages: list[Message] = []

    def __str__(self):
        s = ""
        for i, msg in enumerate(self.messages):
            s += f"MESSAGE {i}\n"
            s += str(msg)
        return s

    def __repr__(self):
        return self.__str__()

    def __len__(self) -> int:
        return len(self.messages)

    def get_messages(self) -> list[Message]:
        messages: list[Message] = []
        for msg in self.messages:
            if msg is None:
                continue
            if Tag.OUTDATED in msg.tags:
                short_msg = msg.short_version()
                if short_msg.content:
                    messages.append(short_msg)
            else:
                messages.append(msg)
        return messages

    def get_step_messages(self) -> StepMessages:
        return StepMessages(self.get_messages())

    def add_message(self, msg: Message | None, verbose=False):
        if msg is None:
            return
        self.messages.append(msg)
        if verbose:
            print(msg)

    def copy(self):
        new_history = History()
        new_history.messages = self.messages.copy()
        return new_history

    def mark_messages_outdated(self, tags: Union[Tag, Iterable[Tag]]):
        tags = {tags} if isinstance(tags, Tag) else set(tags)
        for msg in self.messages:
            if tags.intersection(msg.tags):
                msg.tags.add(Tag.OUTDATED)

    def save(self, path: os.PathLike):
        step_xml = ET.Element("step")
        for msg in self.get_messages():
            step_xml.append(msg.to_xml())
        tree = ET.ElementTree(step_xml)
        ET.indent(tree, space="", level=0)
        tree.write(path, encoding="unicode", xml_declaration=True)

    @classmethod
    def from_xml_path(cls, path):
        with open(path, 'r') as f:
            data = f.read()
        data_tree = ET.fromstring(data)
        history = cls()
        for msg in data_tree.findall("message"):
            history.add_message(Message.from_xml_element(msg))
        return history
