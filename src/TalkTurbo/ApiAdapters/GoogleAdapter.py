import google.generativeai as genai

from TalkTurbo.ApiAdapters.ApiAdapter import ApiAdapter
from TalkTurbo.ChatContext import ChatContext
from TalkTurbo.Messages import AssistantMessage, ContentMessage, MessageRole


class GoogleAdapter(ApiAdapter):
    """Adapter for Google's API."""

    def __init__(self, api_token: str):
        self.model_name = "gemini-pro"

        super().__init__(
            api_token=api_token, model_name=self.model_name, max_tokens=1024
        )

        genai.configure(api_key=self.api_token)
        self._google_client = genai.GenerativeModel(model_name=self.model_name)

    def get_chat_completion(self, context: ChatContext) -> ContentMessage:
        google_context = self.convert_context_to_api_format(context)
        response = self._google_client.generate_content(google_context)

        return AssistantMessage(content=response.text)

    def convert_context_to_api_format(self, context: ChatContext):
        return [
            {"role": message.role.value, "parts": [message.content]}
            for message in context.messages
            if message.role in [MessageRole.USER, MessageRole.ASSISTANT]
        ]
