import nltk
from typing import List
from ChatContext import ChatContext

# Set up logging
import logging
import requests

logger = logging.getLogger("OpenAIModelAssistant")
logger.setLevel(logging.INFO)


class OpenAIModelAssistant:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def query_model(
        self,
        context: ChatContext,
        prompt: str,
        max_tokens: int = 100,
        n: int = 1,
        stop: List[str] = None,
        openai_secret_key="",
    ) -> List[str]:
        if stop is None:
            stop = ["\n"]

        messages = self._build_prompt(context=context)
        headers = {"authorization": f"Bearer {openai_secret_key}"}
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 512,
        }

        response = requests.post(
            url="https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
        )

        # print(f"response = {response.json()}")

        return response.json()

    def _build_prompt(self, context: ChatContext) -> str:
        messages = []
        messages.append({"role": "assistant", "content": context.secret_prompt})
        for message in context.messages:
            messages.append({"role": message["role"], "content": message["content"]})
        # print(f"formatted messages: {messages}")
        return messages
