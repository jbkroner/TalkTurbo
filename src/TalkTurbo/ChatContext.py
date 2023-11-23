from typing import List

import tiktoken
from TalkTurbo.Messages import ContentMessage, UserMessage, SystemMessage, AssistantMessage

class ChatContext:
    _tokenizer_downloaded = False

    def __init__(
        self, messages: List[ContentMessage] = None, system_prompt: SystemMessage = SystemMessage(""), max_tokens: int = 1024
    ) -> None:
        if not messages:  # defaulting to [] was causing problems in the tests
            messages = []
        self.messages = messages
        self.system_prompt = system_prompt
        self.max_tokens = max_tokens
        self._encoding = tiktoken.get_encoding("cl100k_base")

    def __str__(self) -> str:
        return f"ChatContext(messages={self.messages}, secret_prompt='{self.secret_prompt}', max_tokens={self.max_tokens})"

    def context_length_in_tokens(self) -> int:
        """Return the total length of the context in tokens."""
        total_tokens = self.system_prompt.encoding_length_in_tokens

        for message in self.messages:
            total_tokens += message.encoding_length_in_tokens

        return total_tokens


    def add_message(self, message: ContentMessage) -> None:
        """Add a message to the context and trim old messages that don't fit within max_tokens."""
        self.messages.append(message)

        # shorten the context to max_tokens if needed
        self._reduce_context()

    def _reduce_context(self):
        """
        Reduce the context to max_tokens if needed.

        Side-effect: modifies self.messages
        """
        while self.context_length_in_tokens() > self.max_tokens:
            del self.messages[0]

    def length_in_tokens(self, string: str) -> int:
        """Return the number of tokens in a string."""
        return len(self._encoding.encode(string))

    def to_dict(self) -> dict:
        """Convert the context to a dictionary."""
        messages = [message.to_completion_dict() for message in self.messages]
        return {
            "messages": messages,
            "system_prompt": self.system_prompt,
            "max_tokens": self.max_tokens,
        }
