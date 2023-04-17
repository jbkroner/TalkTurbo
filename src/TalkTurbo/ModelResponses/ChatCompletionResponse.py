from TalkTurbo.ModelResponses.Choice import Choice
from TalkTurbo.ModelResponses.Usage import Usage

from datetime import datetime
from typing import Dict, List, Any


class ChatCompletionResponse:
    def __init__(
        self,
        id_: str,
        object_: str,
        created: datetime,
        choices: List[Choice],
        usage: Usage,
    ):
        self.id = id_
        self.object = object_
        self.created = created
        self.choices = choices
        self.usage = usage

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatCompletionResponse":
        choices = [Choice.from_dict(c) for c in data["choices"]]
        usage = Usage.from_dict(data["usage"])

        return cls(
            id_=data["id"],
            object_=data["object"],
            created=datetime.fromtimestamp(data["created"]),
            choices=choices,
            usage=usage,
        )
