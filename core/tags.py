from core.utils import MyEnum

class Tag(MyEnum):
    BRIEFING = "briefing"
    GUIDELINES = "guidelines"
    TOOL_DOCS = "tool_docs"
    INIT_SCRIPT = "init_script"
    MONOLOGUE_INSTRUCTION = "monologue_instruction"
    TOOL_CALL_INSTRUCTION = "tool_call_instruction"
    STATUS = "status"

    # These tags are used when messages are rendered in the history
    # Note: step files contain only messages that are rendered in the history
    OUTDATED = "outdated"  # rendered as a short version

    MONOLOGUE = "monologue"
    TOOL_CALL = "tc"
    TOOL_OUTPUT = "tool_output"
    FEEDBACK = "feedback"

    # These tags are used when messages are rendered in the exercise format
    ESCAPED = "escaped"  # message is escaped and contains xml tags
    STUDENT_DROPOUT = "student_dropout"  # recipient will be set to student_dropout
    TEACHER = "teacher"  # recipient will be set to teacher
    STUDENT = "student"  # recipient will be set to student
    TARGET = "target"  # assistant_target message
