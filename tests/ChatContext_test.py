import unittest
from unittest.mock import patch
from datetime import datetime, timedelta
from TalkTurbo.ChatContext import ChatContext
from TalkTurbo.Messages import SystemMessage, AssistantMessage, UserMessage


class TestChatContext(unittest.TestCase):
    def test_init(self):
        chat_context = ChatContext()
        self.assertEqual(chat_context.messages, [])
        self.assertEqual(chat_context.system_prompt.content, "")
        self.assertEqual(chat_context.max_tokens, 1024)

    def test_context_length_in_tokens(self):

        messages = [
            UserMessage("a"),
            AssistantMessage("a")
        ]

        system_prompt = SystemMessage("a")


        chat_context = ChatContext(messages=messages, system_prompt=system_prompt)
        self.assertEqual(chat_context.context_length_in_tokens(), 3)

    def test_add_message(self):
        chat_context = ChatContext()
        message = UserMessage("Hello")
        chat_context.add_message(UserMessage("Hello"))
        self.assertEqual(len(chat_context.messages), 1)
        self.assertEqual(chat_context.messages[0].content, message.content)

    def test_reduce_context_single_message_less_than_max(self):
        chat_context = ChatContext(max_tokens=3)
        chat_context.add_message(UserMessage("testing _reduce_context!"))
        chat_context._reduce_context()
        self.assertEqual(len(chat_context.messages), 0)


    def test_reduce_context_single_message_greater_than_max(self):
        chat_context = ChatContext(max_tokens=3)
        chat_context.add_message(UserMessage("Testing reduce_context with a longer message"))
        chat_context._reduce_context()
        self.assertEqual(len(chat_context.messages), 0)

    def test_reduce_context_multiple_messages(self):
        chat_context = ChatContext(max_tokens=6)
        chat_context.add_message(UserMessage("Hello there cats and dogs"))
        chat_context.add_message(UserMessage("Hi"))
        chat_context.add_message(UserMessage("Hey"))
        chat_context._reduce_context()
        self.assertEqual(len(chat_context.messages), 2)
        self.assertEqual(chat_context.messages[0].content, "Hi")
        self.assertEqual(chat_context.messages[1].content, "Hey")

    def test_reduce_context_no_removal(self):
        chat_context = ChatContext(max_tokens=5)
        chat_context.add_message(UserMessage("Hello"))
        chat_context.add_message(UserMessage("Hi"))
        chat_context._reduce_context()
        self.assertEqual(len(chat_context.messages), 2)
        self.assertEqual(chat_context.messages[0].content, "Hello")
        self.assertEqual(chat_context.messages[1].content, "Hi")

    def test_remove_stale_messages(self):
        # Mock datetime to control the current time
        with patch('TalkTurbo.ChatContext.datetime') as mock_datetime:
            # Set the current time to a specific point
            now = datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.utcnow.return_value = now

            # Create a ChatContext with a TTL of 1 hour
            chat_context = ChatContext(ttl_hours=1)
            
            # Add a message that is just within the TTL
            fresh_message = UserMessage("Fresh message")
            fresh_message.created_on_utc = now - timedelta(minutes=59)
            chat_context.add_message(fresh_message)

            # Add a message that is outside the TTL
            stale_message = UserMessage("Stale message")
            stale_message.created_on_utc = now - timedelta(hours=1, minutes=1)
            chat_context.add_message(stale_message)

            # Check if stale messages are removed correctly
            self.assertEqual(len(chat_context.messages), 1)
            self.assertEqual(chat_context.messages[0].content, fresh_message.content)

    def test_to_dict(self):
        chat_context = ChatContext()
        chat_context.add_message(UserMessage("Hello"))
        chat_context.add_message(UserMessage("Hello2"))
        context_list = chat_context.get_messages_as_list()
        self.assertEqual(context_list[0]["content"], "") # system prompt
        self.assertEqual(context_list[1]["content"], "Hello")
        self.assertEqual(context_list[2]["content"], "Hello2")


if __name__ == "__main__":
    unittest.main()
