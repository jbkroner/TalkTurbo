import json
from datetime import datetime
from enum import Enum

import tiktoken

from TalkTurbo import OPENAI_CLIENT
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
        self._moderated = False
        self._category_flags = None
        self._category_scores = None
        self._flagged = None

    def to_completion_dict(self) -> dict:
        return {"role": self.role.value, "content": self.content}

    def moderate(self):
        """moderate this message"""
        moderation_response = OPENAI_CLIENT.moderations.create(
            input=self.content, model="text-moderation-latest"
        )

        moderation_data = json.loads(moderation_response.model_dump_json())

        self._flagged = moderation_data["results"][0]["flagged"]
        self._category_flags = CategoryFlags.from_moderation_response(moderation_data)
        self._category_scores = CategoryScores.from_moderation_response(moderation_data)
        self._moderated = True

    def flagged(self) -> bool:
        """
        Returns:
            True if this message has content flags, else False
        """
        if not self._moderated:
            self.moderate()

        return self._flagged

    def get_category_flags(self) -> CategoryFlags:
        """
        Returns:
            A CategoryFlags instance for this message.
        """
        if not self._moderated:
            self.moderate()

        return self._category_flags

    def get_category_scores(self) -> CategoryScores:
        """
        Returns:
            A CategoryScores instance for this message.
        """
        if not self._moderated:
            self.moderate()

        return self._category_scores

    def get_max_category(self) -> str:
        """
        Returns:
            The highest scoring category.
        """
        return max(self.get_category_scores())


class SystemMessage(ContentMessage):
    def __init__(self, content: str, name: str = None):
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


class FlaggedContentError(Exception):
    def __init__(self, content_message: ContentMessage):
        self.content_message = content_message
        super().__init__(f"message f{self.content_message} flagged for content")

    def __str__(self):
        return f"ContentFlaggedError: flagged category: {self.content_message.get_max_category()}, content: {self.content_message.content}"


class MessageFactory:
    """
    Create the appropriate message type based on the role.
    """

    @staticmethod
    def create_message(content: str, role: str, name: str = None) -> ContentMessage:
        role = MessageRole(role)

        if role == MessageRole.SYSTEM:
            return SystemMessage(content=content, name=name)
        elif role == MessageRole.USER:
            return UserMessage(content=content, name=name)
        elif role == MessageRole.ASSISTANT:
            return AssistantMessage(content=content, name=name)
        else:
            raise ValueError(f"Unsupported role: {role}")
