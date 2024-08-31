from abc import ABC


class ModelDescription(ABC):
    """Generic interface for describing a language model's properties"""

    def __init__(self, model_name: str, max_input_tokens: int, max_output_tokens: int) -> None:
        super().__init__()
        self.model_name = model_name
        self.max_input_tokens = max_input_tokens
        self.max_output_tokens = max_output_tokens

    def __str__(self) -> str:
        return (
            f"{self.model_name} (input: {self.max_input_tokens}, output: {self.max_output_tokens})"
        )

    def to_dict(self) -> dict:
        return {
            "model_name": self.model_name,
            "max_input_tokens": self.max_input_tokens,
            "max_output_tokens": self.max_output_tokens,
        }
