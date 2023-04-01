import unittest
import nltk
from TalkTurbo.ChatContext import ChatContext


class TestChatContext(unittest.TestCase):
    def test_init(self):
        chat_context = ChatContext()
        self.assertEqual(chat_context.messages, [])
        self.assertEqual(chat_context.secret_prompt, "")
        self.assertEqual(chat_context.max_tokens, 1024)

    def test_context_length_in_tokens(self):
        messages = [{"content": "Hello", "num_tokens": 2}]
        chat_context = ChatContext(messages=messages, secret_prompt="Test prompt")
        self.assertEqual(chat_context.context_length_in_tokens(), 4)

    def test_add_message(self):
        chat_context = ChatContext()
        chat_context.add_message("Hello", "user")
        self.assertEqual(len(chat_context.messages), 1)
        self.assertEqual(chat_context.messages[0]["content"], "Hello")

    def test_reduce_context_single_message_less_than_max(self):
        chat_context = ChatContext(max_tokens=3)
        chat_context.add_message("Testing reduce_context", "user")
        chat_context._reduce_context()
        self.assertEqual(len(chat_context.messages), 1)

    def test_reduce_context_single_message_greater_than_max(self):
        chat_context = ChatContext(max_tokens=3)
        chat_context.add_message("Testing reduce_context with a longer message", "user")
        chat_context._reduce_context()
        self.assertEqual(len(chat_context.messages), 0)

    def test_reduce_context_multiple_messages(self):
        chat_context = ChatContext(max_tokens=6)
        chat_context.add_message("Hello there cats and dogs", "user")
        chat_context.add_message("Hi", "user")
        chat_context.add_message("Hey", "user")
        chat_context._reduce_context()
        self.assertEqual(len(chat_context.messages), 2)
        self.assertEqual(chat_context.messages[0]["content"], "Hi")
        self.assertEqual(chat_context.messages[1]["content"], "Hey")

    def test_reduce_context_no_removal(self):
        chat_context = ChatContext(max_tokens=5)
        chat_context.add_message("Hello", "user")
        chat_context.add_message("Hi", "user")
        chat_context._reduce_context()
        self.assertEqual(len(chat_context.messages), 2)
        self.assertEqual(chat_context.messages[0]["content"], "Hello")
        self.assertEqual(chat_context.messages[1]["content"], "Hi")

    def test_length_in_tokens(self):
        chat_context = ChatContext()
        tokens = chat_context.length_in_tokens("This is a test.")
        self.assertEqual(tokens, 5)

    def test_to_dict(self):
        chat_context = ChatContext()
        chat_context.add_message("Hello", "user")
        context_dict = chat_context.to_dict()
        self.assertEqual(context_dict["secret_prompt"], "")
        self.assertEqual(context_dict["max_tokens"], 1024)
        self.assertEqual(len(context_dict["messages"]), 1)

    def test_from_dict(self):
        data = {
            "messages": [{"role": "user", "content": "Hello", "num_tokens": 1}],
            "secret_prompt": "",
            "max_tokens": 1024,
        }
        chat_context = ChatContext.from_dict(data)
        self.assertEqual(chat_context.secret_prompt, "")
        self.assertEqual(chat_context.max_tokens, 1024)
        self.assertEqual(len(chat_context.messages), 1)

    def test_serialize(self):
        chat_context = ChatContext()
        chat_context.add_message("Hello", "user")
        serialized_context = chat_context.serialize()
        self.assertIsInstance(serialized_context, str)

    def test_deserialize(self):
        chat_context = ChatContext()
        chat_context.add_message("Hello", "user")
        serialized_context = chat_context.serialize()
        deserialized_context = ChatContext.deserialize(serialized_context)
        self.assertIsInstance(deserialized_context, ChatContext)
        self.assertEqual(deserialized_context.secret_prompt, "")
        self.assertEqual(deserialized_context.max_tokens, 1024)
        self.assertEqual(len(deserialized_context.messages), 1)


if __name__ == "__main__":
    unittest.main()
