from core.utils import MyEnum


class TCStatus(MyEnum):
    REGULAR_CALL = "regular_call"
    ERROR = "error"
    COMPLETE_TASK = "complete_task"

    def __eq__(self, other):
        return hasattr(other, "value") and self.value == other.value
