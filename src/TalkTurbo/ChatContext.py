import nltk

# init the tokenizer
nltk.download("punkt")


class ChatContext:
    _tokenizer_downloaded = False

    def __init__(
        self, messages: list = None, secret_prompt: str = "", max_tokens: int = 1024
    ) -> None:
        if not messages:  # defaulting to [] was causing problems in the tests
            messages = []
        self.messages = messages
        self.secret_prompt = secret_prompt
        self.max_tokens = max_tokens

        if not ChatContext._tokenizer_downloaded:
            nltk.download("punkt")
            ChatContext._tokenizer_downloaded = True

    def __str__(self) -> str:
        return f"ChatContext(messages={self.messages}, secret_prompt='{self.secret_prompt}', max_tokens={self.max_tokens})"

    def context_length_in_tokens(self) -> int:
        """Return the total length of the context in tokens."""
        total_tokens = self.length_in_tokens(self.secret_prompt)
        for message in self.messages:
            total_tokens += message["num_tokens"]
        return total_tokens

    def add_message(self, content: str, role: str) -> None:
        """Add a message to the context and trim old messages that don't fit within max_tokens."""
        num_tokens = self.length_in_tokens(content)
        new_message = {"role": role, "content": content, "num_tokens": num_tokens}

        self.messages.append(new_message)

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
        return len(nltk.word_tokenize(string))

    def to_dict(self) -> dict:
        """Convert the context to a dictionary."""
        return {
            "messages": self.messages,
            "secret_prompt": self.secret_prompt,
            "max_tokens": self.max_tokens,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ChatContext":
        """Create a new context from a dictionary."""
        return cls(
            messages=data["messages"],
            secret_prompt=data["secret_prompt"],
            max_tokens=data["max_tokens"],
        )

    def serialize(self) -> str:
        """Serialize the context to a JSON string."""
        import json

        return json.dumps(self.to_dict())

    @classmethod
    def deserialize(cls, serialized_context: str) -> "ChatContext":
        """Deserialize a serialized context from a JSON string."""
        import json

        data = json.loads(serialized_context)
        return cls.from_dict(data)
