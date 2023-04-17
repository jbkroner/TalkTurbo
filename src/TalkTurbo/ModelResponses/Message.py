from typing import Dict, Any


class Message:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(role=data["role"], content=data["content"])
