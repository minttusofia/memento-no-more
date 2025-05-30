import copy
from dataclasses import dataclass
from prettyprinter import pformat
import random
import re
from typing import Literal, Optional, get_args

import xml.etree.ElementTree as ET

from .utils import Colors
from .tags import Tag
from core.utils import xml_decoder, xml_encoder, MyEnum


class Role(MyEnum):
    SYSTEM = "system"
    AI = "assistant"
    USER = "user"

class Message:
    color: str = Colors.DEFAULT
    content: str
    role: str
    tags: set
    short_content: Optional[str]

    def __init__(self, role: str, content: str, tags: set = None, short_content: str | None = None, color: str = None): # python 3.10
    # def __init__(self, role: str, content: str, tags: Optional[set] = None, short_content: Optional[str] = None, color: Optional[str] = None): # python 3.9
        self.role = role
        self.content = content
        self.tags = set(tags or {})
        self.short_content = short_content or ""
        # If role is system, use blue color
        self.color = color or (Colors.BLUE if role == Role.AI else Colors.DEFAULT)

    def copy(self):
        return Message(self.role, self.content, self.tags, self.short_content, self.color)

    def short_version(self):
        return Message(self.role, self.short_content, self.tags, self.short_content, self.color)

    @classmethod
    def from_xml_element(cls, element):
        role = Role.from_value(element.get("role"))
        content = xml_decoder(element.text)
        tags = []
        short_content = ""
        for sub_element in element:
            if sub_element.tag == "tag":
                tags.append(xml_decoder(sub_element.text))
            if sub_element.tag == "short_content" and sub_element.text:
                short_content = xml_decoder(sub_element.text)
        tags = set([Tag(tag_str) for tag_str in tags])
        color = xml_decoder(element.get("color"))
        return Message(role, content, tags=tags, short_content=short_content, color=color)

    def _header(self):
        name = self.__class__.__name__
        return f"{name.upper()} with tags ({', '.join(self.tags)}):\n"

    def __str__(self):
        role = self.role
        tags = "{" + ", ".join(str(t) for t in self.tags) + "}"
        return f"{self.color}Message({role=}, tags={tags})\n------------\n{self.content}{Colors.DEFAULT}"

    def __repr__(self):
        return self.__str__()

    def dump(self):
        return {
            "role": self.role.value,
            "content": self.content or "",
        }

    def to_xml(self, parent: ET.Element = None):
        if parent is None:
            msg_element = ET.Element("message")
        else:
            msg_element = ET.SubElement(parent, "message")
        msg_element.set("role", self.role.value)
        msg_element.set("color", xml_encoder(self.color))
        tags = [xml_encoder(tag.value) for tag in self.tags]
        for tag in sorted(tags):
            ET.SubElement(msg_element, "tag").text = tag
        if self.short_content:
            ET.SubElement(msg_element, "short_content").text = xml_encoder(self.short_content)
        msg_element.text = xml_encoder(self.content)

        return msg_element

    def __eq__(self, other):
        return self.to_dict() == other.to_dict()

    def to_dict(self):
        return {
            "role": self.role.value,
            "content": self.content or "",
            "tags": sorted([tag.value for tag in self.tags]),
            "short_content": self.short_content,
            "color": self.color,
        }


def render_for_message(object):
    try:
        return object.render(place="message")
    except (AttributeError, ValueError):
        return str(object)


def merge_messages(messages: list[Message]):
    """Merge consecutive messages of the same role into one message"""
    merged_messages = []
    new_message = None
    for message in messages:
        if new_message is None:
            new_message = message.copy()
        else:
            if message.role == new_message.role:
                new_message.content += "\n\n" + message.content
            else:
                merged_messages.append(new_message)
                new_message = message.copy()
    if new_message:
        merged_messages.append(new_message)

    return merged_messages


Recipient = Literal["teacher", "student", "student_dropout"]

@dataclass
class Section:
    content: str
    recipient: Recipient

    # Make sure the recipient is valid
    def __post_init__(self):
        assert self.recipient in get_args(Recipient), f"Invalid recipient: {self.recipient}"

    def to_xml(self, parent: ET.Element):
        element = ET.SubElement(parent, self.recipient)
        element.text = xml_encoder(self.content)
        return element


class SectionedMessage(Message):
    def __init__(
        self,
        role: Role,
        sections: list[Section | str] = None,
        short_content: str | None = None,
        tags: set = None
    ):
        self.role = role
        self.sections = sections or []
        self.short_content = short_content
        self.tags = set(tags or {})
        self.validate_tags()

    def __str__(self):
        role = self.role
        tags = "{" + ", ".join(str(t) for t in self.tags) + "}"
        # Use prettyprinter to format the sections
        return f"SectionedMessage({role=}, tags={tags})\n------------\n{pformat(self.sections)}"

    def copy(self):
        return SectionedMessage(self.role, copy.copy(self.sections), self.tags)

    def to_dict(self):
        return {
            "role": self.role.value,
            "sections": [{"content": section.content, "recipient": section.recipient} for section in self.sections],
            "tags": sorted([tag.value for tag in self.tags]),
        }

    @property
    def content(self):
        print("Warning: Using content property of a SectionedMessage. Use for_recipient() instead.")
        # Use the content for the teacher by default
        return self.for_recipient(recipient="teacher").content

    def append(self, section: Section | str):
        self.sections.append(section)

    def to_xml(self, parent: ET.Element = None):
        "This method is used to save a message in a step XML file."
        if parent is None:
            msg_element = ET.Element("message")
        else:
            msg_element = ET.SubElement(parent, "message")
        last_child = None

        msg_element.set("role", self.role.value)
        msg_element.set("sectioned", "true")
        tag_values = [tag.value for tag in self.tags]

        for tag_value in sorted(tag_values):
            tag_element = ET.SubElement(msg_element, "tag")
            tag_element.text = escape(tag_value)
            last_child = tag_element

        self.insert_sections(msg_element, last_child)

        if self.short_content:
            short_content_element = ET.SubElement(msg_element, "short_content")
            short_content_element.text = xml_encoder(self.short_content)

        return msg_element

    def insert_sections(self, msg_element: ET.Element, last_child: ET.Element = None):
        for section in self.sections:
            if hasattr(section, "to_xml"):
                # Insert a section element
                last_child = section.to_xml(msg_element)
            else:
                # Insert a string section
                if last_child is None:
                    if msg_element.text is None:
                        msg_element.text = escape(section)
                    else:
                        msg_element.text += escape(section)
                else:
                    if last_child.tail is None:
                        last_child.tail = escape(section)
                    else:
                        last_child.tail += escape(section)

    def validate_tags(self):
        for tag in self.tags:
            if tag in (Tag.TEACHER, Tag.STUDENT, Tag.STUDENT_DROPOUT):
                raise ValueError(f"Tag {tag} is not allowed in a SectionedMessage.")

    @classmethod
    def from_xml_element(cls, element):
        assert element.get("sectioned") == "true", f"Element is not sectioned: {element}"

        role = Role.from_value(element.get("role"))
        tags = []

        sections = []
        if element.text:
            sections.append(element.text)
        for sub_element in element:
            if sub_element.tag == "tag":
                tags.append(xml_decoder(sub_element.text))
            elif sub_element.tag == "short_content":
                short_content = xml_decoder(sub_element.text)
            else:
                assert sub_element.tag in get_args(Recipient), f"Unknown section tag: {sub_element.tag}"
                sections.append(Section(xml_decoder(sub_element.text), sub_element.tag))

            if sub_element.tail:
                sections.append(sub_element.tail)

        tags = set([Tag(tag_str) for tag_str in tags])
        return SectionedMessage(role, sections, short_content, tags)

    def for_recipient(self, recipient: Literal["teacher", "student"], dropout_rate: float = 1.0) -> Message:
        assert recipient in ("teacher", "student"), f"Invalid recipient: {recipient}"
        content = ""
        for section in self.sections:
            if hasattr(section, "recipient"):
                # Section object
                if section.recipient == recipient:
                    content += section.content
                elif section.recipient == "student_dropout":
                    if recipient == "teacher" or random.random() > dropout_rate:
                        content += section.content
            else:
                # String section
                content += section

        return Message(self.role, content, self.tags)

    def short_version(self):
        return Message(self.role, self.short_content, self.tags)
