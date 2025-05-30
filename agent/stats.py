from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import numpy as np
from pprint import pformat
from typing import List, DefaultDict

from core.usage import Usage
from core.utils import elapsed_time_string_short

@dataclass
class Stats:
    start_time: datetime = field(default_factory=datetime.now)
    duration: timedelta = None  # total duration, set at the end of every step
    call_times: List[float] = field(default_factory=list)
    tool_calls: DefaultDict[str, int] = field(default_factory=lambda: defaultdict(int))
    retry_count: int = 0
    usages: List[Usage] = field(default_factory=list)
    costs: List[float] = field(default_factory=list)
    parent_stats: "Stats" = None

    @classmethod
    def from_status(cls, status: dict = None):
        if status and (start_time := status.get("start_time")):
            return cls(start_time=datetime.fromisoformat(start_time))
        else:
            return cls()

    def get_root_stats(self):
        return self.parent_stats.get_root_stats() if self.parent_stats else self

    def add_tool_call(self, tool_name: str):
        self.tool_calls[tool_name] += 1
        if self.parent_stats:
            self.parent_stats.add_tool_call(tool_name)

    def __str__(self):
        if self.call_times:
            min_time = min(self.call_times)
            mean_time = np.mean(self.call_times)
            max_time = max(self.call_times)
        else:
            min_time = mean_time = max_time = np.NaN

        d = self.to_dict()
        d["call times"] = f"{min_time:.1f} <-> {mean_time:.1f} <-> {max_time:.1f}"
        return pformat(d)

    @property
    def n_calls(self):
        return len(self.call_times)

    @property
    def elapsed_time(self):
        return elapsed_time_string_short(self.start_time, datetime.now())

    @property
    def usage(self):
        return sum(self.usages, Usage())

    @property
    def cost(self):
        if any(cost is None for cost in self.costs):
            return None
        else:
            return sum(self.costs)

    def set_duration(self):
        self.duration = datetime.now() - self.start_time

    def update(
        self,
        usage: Usage = None,
        call_time: float = 1.,
        retry_count: int = 0,
        model: str = None,
    ):
        self.call_times.append(call_time)
        self.retry_count += retry_count
        if usage:
            self.usages.append(usage)
        if model is not None:
            cost = usage.to_cost(model)
            self.costs.append(cost)
        if self.parent_stats:
            self.parent_stats.update(usage, call_time, retry_count)

    def to_dict(self):
        return {
            "start_time": self.start_time.isoformat(),
            "duration": int(self.duration.total_seconds()) if self.duration else None,
            "n_calls": self.n_calls,
            "call_times": [round(time, 1) for time in self.call_times],
            "tool_calls": dict(self.tool_calls),
            "retry_count": self.retry_count,
            "usages": [
                (usage.input_tokens, usage.output_tokens)
                for usage in self.usages
            ],
            "total_usage": self.usage.to_dict(),
            "total_cost": round(self.cost, 2) if self.cost is not None else None,
        }
