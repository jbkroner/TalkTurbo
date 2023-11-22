from enum import Enum
from datetime import datetime

import tiktoken
# api ref: https://platform.openai.com/docs/api-reference/chat/create

ENCODER = tiktoken.get_encoding("cl100k_base")

class MessageRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    FUNCTION = "function"

class Message:
    def __init__(self, role: MessageRole):
        self.role = role
        self.created_on_utc = datetime.utcnow()

    def __str__(self):
        return str(vars(self))

class ContentMessage:
    def __init__(self, content: str, name: str=None) -> None:
        self.content = content
        self.name = name
        self.encoding = ENCODER.encode(self.content)
        self.encoding_length_in_token = len(self.encoding)

class SystemMessage(ContentMessage):
    def __init__(self, content: str, name: str=None):
        """
        args:
            content: The contents of the system message
            name: An optional name for the participant.
                  Provides the model information to differentiate 
                  between participants of the same role.
        """
        super().__init__(role=MessageRole.SYSTEM, content=content, name=name)

class UserMessage(ContentMessage):
    def __init__(self, content: str, name: str = None):
        """
        args:
            content: The contents of the user message
            name: An optional name for the participant.
                  Provides the model information to differentiate 
                  between participants of the same role.
        """
        super().__init__(role=MessageRole.USER, content=content, name=name)

class AssistantMessage(ContentMessage):
    def __init__(self, content: str, name: str = None):
        """
        args:
            content: The contents of the assistant message
            name: An optional name for the participant.
                  Provides the model information to differentiate 
                  between participants of the same role.
        """
        super().__init__(role=MessageRole.ASSISTANTm, content=content, name=name)

class FunctionMessage(Message):
    def __init__(self, role: MessageRole):
        raise NotImplementedError()

class ToolMessage(Message):
    def __init__(self, role: MessageRole):
        raise NotImplementedError()