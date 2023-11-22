from enum import Enum
from datetime import datetime

# api ref: https://platform.openai.com/docs/api-reference/chat/create

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
class SystemMessage(Message):
    def __init__(self, content: str, name: str=None):
        """
        args:
            content: The contents of the system message
            name: An optional name for the participant.
                  Provides the model information to differentiate 
                  between participants of the same role.
        """
        super().__init__(role=MessageRole.SYSTEM)
        self.content = content
        self.name = name

class UserMessage(Message):
    def __init__(self, content: str, name: str = None):
        """
        args:
            content: The contents of the user message
            name: An optional name for the participant.
                  Provides the model information to differentiate 
                  between participants of the same role.
        """
        super().__init__(role=MessageRole.USER)
        self.content = content
        self.name = name

class AssistantMessage(Message):
    def __init__(self, content: str, name: str = None):
        """
        args:
            content: The contents of the assistant message
            name: An optional name for the participant.
                  Provides the model information to differentiate 
                  between participants of the same role.
        """
        super().__init__(role=MessageRole.ASSISTANT)
        self.content = content
        self.name = name

class FunctionMessage(Message):
    def __init__(self, role: MessageRole):
        raise NotImplementedError()

class ToolMessage(Message):
    def __init__(self, role: MessageRole):
        raise NotImplementedError()