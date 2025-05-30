from abc import ABC, abstractmethod

from core.steps import StepMessages


class BaseReviewFilter(ABC):
    @abstractmethod
    def check_step(self, step_messages: StepMessages) -> tuple[str, bool]:
        """Return a reason for the filtering decision (can be ""), and the boolean filtering result.

        The filtering result is True if the step passes the filter, and False otherwise.
        """
        pass
