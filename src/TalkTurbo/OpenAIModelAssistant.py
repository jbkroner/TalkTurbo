import os
from typing import List, Dict, Tuple
from .ChatContext import ChatContext

# Set up logging
import logging
import requests
import time
import base64

logger = logging.getLogger("OpenAIModelAssistant")
logger.setLevel(logging.INFO)


class OpenAIModelAssistant:
    DALLE_RESOLUTION = {
        "small": "256x256",
        "medium": "512x512",
        "large": "1024x1024",
    }

    def __init__(
        self,
        temperature: float = 0.7,
        min_dalle_timeout_in_seconds: float = 10.0,
    ) -> None:
        if temperature > 2.0 or temperature < 0:
            print(
                f"invalid temperature ({temperature}, must be in [0, 2.0]). Setting to default (0.7)"
            )
            temperature = 0.7
        self.temperature = temperature
        self.min_dalle_timeout_in_seconds = min_dalle_timeout_in_seconds
        self._last_dalle_gen_time = time.time()

    def query_model(
        self,
        context: ChatContext,
        prompt: str,
        max_tokens: int = 100,
        temperature: float = 0.7,
        stop: List[str] = None,
        hashed_user_identifier: str = None,
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
            "n": 1,  # number of completions to generatei
        }
        if hashed_user_identifier:
            payload["user"] = hashed_user_identifier

        response = requests.post(
            url="https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
        )

        # print(f"response = {response.json()}")

        return response.json()

    def query_dalle(
        self,
        query: str,
        path: str = f"./dalle_tmp/",
        resolution: str = "large",
        hashed_user_identifier: str = None,
        openai_secret_key: str = "",
    ) -> str:
        headers = {"authorization": f"Bearer {openai_secret_key}"}
        url = "https://api.openai.com/v1/images/generations"
        payload = {
            "prompt": query,
            "size": OpenAIModelAssistant.DALLE_RESOLUTION[resolution],
        }

        if hashed_user_identifier:
            payload["user"] = hashed_user_identifier

        response = requests.post(url=url, json=payload, headers=headers)
        image_url = response.json()["data"][0]["url"]
        image_data = requests.get(image_url)

        # update the path
        path = (
            path
            + str(time.time())
            + "---"
            + self._safe_encode(string_to_encode=query.replace(" ", ""))
            + ".png"
        )

        # Ensure the directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "wb") as f:
            f.write(image_data.content)
            f.close()

        # hit the clock
        self._last_dalle_gen_time = time.time()

        return path

    def _build_prompt(self, context: ChatContext) -> str:
        messages = []
        messages.append({"role": "system", "content": context.secret_prompt})
        for message in context.messages:
            messages.append({"role": message["role"], "content": message["content"]})
        print(f"formatted messages: {messages}")
        return messages

    def _safe_encode(self, string_to_encode: str) -> str:
        input_bytes = string_to_encode.encode("utf-8")
        encoded_bytes = base64.urlsafe_b64encode(input_bytes)
        encoded_string = encoded_bytes.decode("utf-8")
        return encoded_string

    def dalle_timeout_passed(self) -> bool:
        return (
            True
            if self.dalle_timeout_remaining() > self.min_dalle_timeout_in_seconds
            else False
        )

    def dalle_timeout_remaining(self) -> float:
        return max(time.time() - self._last_dalle_gen_time, 0.0)

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
