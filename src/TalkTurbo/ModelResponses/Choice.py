from typing import Dict, Any

from TalkTurbo.ModelResponses.Message import Message


class Choice:
    def __init__(self, index: int, message: Message, finish_reason: str):
        self.index = index
        self.message = message
        self.finish_reason = finish_reason

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Choice":
        message = Message.from_dict(data["message"])

        return cls(
            index=data["index"], message=message, finish_reason=data["finish_reason"]
        )
