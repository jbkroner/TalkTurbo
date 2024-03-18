import os

from TalkTurbo.ApiAdapters.OpenAIAdapter import OpenAIAdapter
from TalkTurbo.ApiAdapters.AnthropicAdapter import AnthropicAdapter
from TalkTurbo.ChatContext import ChatContext
from TalkTurbo.Messages import UserMessage
from TalkTurbo.ApiAdapters.GoogleAdapter import GoogleAdapter


OPENAI_KEY = os.environ.get("OPENAI_SECRET_KEY", None)
ANT_KEY = os.environ.get("ANTHROPIC_SECRET_KEY", None)

cc = ChatContext()


adapter = OpenAIAdapter(OPENAI_KEY)

cc.add_message(UserMessage("Hello, how are you?"))

print(cc.get_messages_as_list())

response = adapter.get_chat_completion(cc)
print("OpenAI GPT 3.5 Turbo ->")
print(response.content)

print("trying anthropic adapter...")

ant_adapter = AnthropicAdapter(ANT_KEY)

response = ant_adapter.get_chat_completion(cc)

print("Anthropic Claude 3 Opus ->")
print(response.content)


print("trying google adapter...")
g_adapter = GoogleAdapter(os.environ.get("GOOGLE_SECRET_KEY", None))
print("google auth complete")  # TODO <_ default credentials?
response = g_adapter.get_chat_completion(cc)
print(response)
