"""Adapter for Google's API."""

import google.generativeai as genai

from TalkTurbo.ApiAdapters.ApiAdapter import ApiAdapter
from TalkTurbo.ChatContext import ChatContext
from TalkTurbo.Messages import AssistantMessage, ContentMessage, MessageRole


class GoogleAdapter(ApiAdapter):
    """Adapter for Google's API."""

    AVAILABLE_MODELS = ["gemini-pro"]

    def __init__(self, api_token: str, model_name: str = "gemini-pro", max_tokens=4096):
        super().__init__(api_token=api_token, model_name=model_name, max_tokens=1024)

        genai.configure(api_key=self.api_token)
        self._google_client = genai.GenerativeModel(model_name=self.model_name)

    def get_chat_completion(self, context: ChatContext) -> ContentMessage:
        google_context = self.convert_context_to_api_format(context)
        response = self._google_client.generate_content(google_context)

        return AssistantMessage(content=response.text)

    def convert_context_to_api_format(self, context: ChatContext):
        # multi-turn expects a user and asst messages alternating
        # to fit the system prompt in we have to make up the first few
        # messages here
        messages = [
            context.system_prompt,
            AssistantMessage("Sounds great ;)"),
        ] + context.messages

        # convert to google format
        cc_list = [{"role": message.role.value, "parts": [message.content]} for message in messages]

        # update the roles
        for message in cc_list:
            # system messages become user messages
            if message["role"] == MessageRole.SYSTEM.value:
                message["role"] = MessageRole.USER.value

            # assistant messages become "model" messages
            if message["role"] in {MessageRole.ASSISTANT.value}:
                message["role"] = "model"

        return cc_list
