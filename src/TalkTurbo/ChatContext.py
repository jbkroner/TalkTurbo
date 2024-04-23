"""Represents the context of a conversation with a chatbot."""

from datetime import datetime, timedelta
from typing import List

import tiktoken

from TalkTurbo.Messages import ContentMessage, SystemMessage, UserMessage


class ChatContext:
    """
    Represents the context of a conversation with a chatbot.
    """

    _tokenizer_downloaded = False

    def __init__(
        self,
        messages: List[ContentMessage] = None,
        system_prompt: SystemMessage = SystemMessage(""),
        max_tokens: int = 1024,
        ttl_hours: int = 24,
    ) -> None:
        if not messages:
            messages = []
        self.messages = messages
        self.system_prompt = system_prompt
        self.max_tokens = max_tokens
        self.ttl = timedelta(hours=ttl_hours)  # time-to-live for messages
        self._encoding = tiktoken.get_encoding("cl100k_base")

        # add the system prompt to the context
        self.add_message(system_prompt)

    def __str__(self) -> str:
        return f"ChatContext(messages={self.messages}, secret_prompt='{self.system_prompt}', max_tokens={self.max_tokens})"

    def context_length_in_tokens(self) -> int:
        """Return the total length of the context in tokens."""
        total_tokens = self.system_prompt.encoding_length_in_tokens

        for message in self.messages:
            total_tokens += message.encoding_length_in_tokens

        return total_tokens

    def add_message(self, message: ContentMessage | str):
        """Add a message to the context and trim old messages that don't fit within max_tokens."""
        if isinstance(message, str):
            message = UserMessage(message, self._encoding)

        self.messages.append(message)

        # shorten the context to max_tokens if needed
        self._reduce_context()

        # remove stale messages
        self._remove_stale_messages()

    def get_latest_message(self) -> ContentMessage:
        """Return the latest message in the context."""
        return self.messages[-1]

    def _reduce_context(self):
        """
        Reduce the context to max_tokens if needed.

        Side-effect: modifies self.messages
        """
        while self.context_length_in_tokens() > self.max_tokens:
            del self.messages[1]  # the 0th message is the system prompt

    def _remove_stale_messages(self):
        """Remove messages that are older than the TTL"""
        current_time = datetime.utcnow()
        self.messages = [
            m
            for m in self.messages
            if (current_time - m.created_on_utc < self.ttl)
            and not isinstance(m, SystemMessage)
        ]

    def get_messages_as_list(self) -> List[dict]:
        """Convert the context messages to a list of message dicts"""
        return [self.system_prompt.to_completion_dict()] + [
            message.to_completion_dict() for message in self.messages
        ]
