import nltk
from typing import List, Dict, Tuple
from .ChatContext import ChatContext

# Set up logging
import logging
import requests

logger = logging.getLogger("OpenAIModelAssistant")
logger.setLevel(logging.INFO)


class OpenAIModelAssistant:
    def __init__(
        self, temperature: float = 0.7, max_response_length: int = 100
    ) -> None:
        if temperature > 2.0 or temperature < 0:
            print(
                f"invalid temperature ({temperature}, must be in [0, 2.0]). Setting to default (0.7)"
            )
            temperature = 0.7
        self.temperature = temperature

    def query_model(
        self,
        context: ChatContext,
        prompt: str,
        max_tokens: int = 100,
        temperature: float = 0.7,
        stop: List[str] = None,
        openai_secret_key: str = "",
    ) -> List[str]:
        if stop is None:
            stop = ["\n"]

        messages = self._build_prompt(context=context)
        headers = {"authorization": f"Bearer {openai_secret_key}"}
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "n": 1,  # number of completions to generate
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
        messages.append({"role": "system", "content": context.secret_prompt})
        for message in context.messages:
            messages.append({"role": message["role"], "content": message["content"]})
        print(f"formatted messages: {messages}")
        return messages

    @staticmethod
    def get_moderation_score(message: str, openai_secret_key: str) -> Tuple[str, float]:
        url = "https://api.openai.com/v1/moderations"
        headers = {"authorization": f"Bearer {openai_secret_key}"}
        payload = {"input": message}
        response = requests.post(url=url, json=payload, headers=headers)

        return OpenAIModelAssistant._category_score(response.json())

    @staticmethod
    def _category_score(moderation_response: Dict[str, any]) -> Tuple[str, float]:
        """
        parse the results of a response from the moderation endpoint
        https://platform.openai.com/docs/api-reference/moderations

        returns the name of the max category and the max score
        """
        categories = moderation_response["results"][0]["categories"]
        category_scores = moderation_response["results"][0]["category_scores"]

        for category, is_harmful in categories.items():
            if is_harmful:
                return (category, category_scores[category])

        return None, 0.0
