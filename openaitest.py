import os
import time

from TalkTurbo.ApiAdapters.OpenAIAdapter import OpenAIAdapter
from TalkTurbo.ApiAdapters.AnthropicAdapter import AnthropicAdapter
from TalkTurbo.ChatContext import ChatContext
from TalkTurbo.Messages import UserMessage
from TalkTurbo.ApiAdapters.GoogleAdapter import GoogleAdapter


OPENAI_KEY = os.environ.get("OPENAI_SECRET_KEY", None)
ANT_KEY = os.environ.get("ANTHROPIC_SECRET_KEY", None)

cc = ChatContext()


adapter = OpenAIAdapter(OPENAI_KEY)

cc.add_message(UserMessage("Hi! Tell me about yourself."))

print(cc.get_messages_as_list())

start = time.time()
response = adapter.get_chat_completion(cc)
end = time.time()
print(f"OpenAI GPT 3.5 Turbo -> {end - start:.2f} seconds")
print(response.content)

# print("\ntrying anthropic adapter...")

# ant_adapter = AnthropicAdapter(ANT_KEY)

# start = time.time()
# response = ant_adapter.get_chat_completion(cc)
# end = time.time()

# print(f"Anthropic Claude 3 Opus {end - start:.2f} seconds ->")
# print(response.content)


print("\ntrying google adapter...")
g_adapter = GoogleAdapter(os.environ.get("GOOGLE_SECRET_KEY", None))
start = time.time()
response = g_adapter.get_chat_completion(cc)
end = time.time()
print(f"Google Gemini Pro -> {end - start:.2} seconds")
print(response.content)
