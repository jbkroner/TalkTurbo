from abc import ABC


class Model(ABC):
    def __init__(self, model_name, max_tokens) -> None:
        super().__init__()
        self.max_tokens = max_tokens
        self.model_name = model_name
