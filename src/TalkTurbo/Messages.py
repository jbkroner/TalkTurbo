from enum import Enum
from datetime import datetime
import os
import requests
import tiktoken
from dotenv import load_dotenv

from TalkTurbo.Moderations import CategoryFlags, CategoryScores
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

class ContentMessage(Message):
    load_dotenv()
    _OPENAI_KEY = os.getenv('OPENAI_SECRET_KEY')

    def __init__(self, role: MessageRole, content: str, name: str = None):
        super().__init__(role)
        self.content = content
        self.name = name
        self.encoding = ENCODER.encode(self.content)
        self.encoding_length_in_tokens = len(self.encoding)
        
        # moderation fields - these may be None if the 
        # message is unmoderated.
        # set with moderate()
        # get with getters.
        self._category_flags = None
        self._category_scores = None
        self._flagged = None


    def to_completion_dict(self) -> dict:
        return {"role": self.role.value, "content": self.content}

    def moderate(self):
        """moderate this message"""
        moderation_response = requests.post(
            url="https://api.openai.com/v1/moderations",
            headers={
                "Content-Type": "application/json",
                "Authorization":  f"Bearer {ContentMessage._OPENAI_KEY}"
            },
            json={
                "input": self.content,
                "model": "text-moderation-stable"
            }
        ) 

        moderation_response.raise_for_status()
        
        moderation_data = moderation_response.json() 

        self._flagged = moderation_data['results'][0]['flagged']
        self._category_flags = CategoryFlags.from_moderation_response(moderation_data)
        self._category_scores = CategoryScores.from_moderation_response(moderation_data)


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
        super().__init__(role=MessageRole.ASSISTANT, content=content, name=name)

class FunctionMessage(Message):
    def __init__(self, role: MessageRole):
        raise NotImplementedError()

class ToolMessage(Message):
    def __init__(self, role: MessageRole):
        raise NotImplementedError()