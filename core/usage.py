from dataclasses import dataclass

@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0

    def __str__(self):
        return f"Usage(input_tokens={self.input_tokens}, output_tokens: {self.output_tokens})"

    def add(self, usage: "Usage"):
        self.input_tokens += usage.input_tokens
        self.output_tokens += usage.output_tokens

    def __add__(self, other):
        return Usage(
            self.input_tokens + other.input_tokens,
            self.output_tokens + other.output_tokens
        )

    def to_dict(self):
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
        }

    def to_cost(self, model: str) -> float | None:
        if model in pricing:
            return (
                pricing[model].input_per_1k * self.input_tokens / 1000 +
                pricing[model].output_per_1k * self.output_tokens / 1000
            )

        return None

    @classmethod
    def from_anthropic(cls, usage):
        return cls(input_tokens=usage.input_tokens, output_tokens=usage.output_tokens)

    @classmethod
    def from_openai(cls, usage):
        return cls(
            input_tokens=usage.prompt_tokens,
            output_tokens=usage.completion_tokens,
        )

@dataclass
class Price:
    input_per_1k: float
    output_per_1k: float

pricing = {
    "gpt-4o": Price(2.5/1000, 10./1000),
    "gpt-4o-mini": Price(0.150/1000, 0.600/1000),
    "gpt-4-turbo": Price(0.01, 0.03),
    "gpt-3.5-turbo": Price(3/1000, 5/1000),
    "claude-3-5-sonnet-20240620": Price(3/1000, 15/1000),
    "claude-3-opus-20240229": Price(15/1000, 75/1000),
    "claude-3-sonnet-20240229": Price(3/1000, 15/1000),
    "claude-3-haiku-20240307": Price(0.25/1000, 1.25/1000),
    "deepseek-chat": Price(0.14/1000, 0.28/1000),  # Served by DeepSeek
    "deepseek-ai/DeepSeek-V3": Price(0.85/1000, 0.9/1000),  # Served by DeepInfra
}

