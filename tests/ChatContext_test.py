import unittest

from TalkTurbo.ChatContext import ChatContext
from TalkTurbo.Messages import AssistantMessage, SystemMessage, UserMessage


class TestChatContext(unittest.TestCase):
    def test_init_defaults(self):
        c = ChatContext()
        self.assertEqual(c.messages, [])
        self.assertEqual(c.system_prompt.content, "")
        self.assertEqual(c.pre_load_data, [])
        self.assertEqual(c.max_tokens, 4096)

    def test_init_non_default(self):
        messages = [UserMessage("Hello")]
        system_prompt = SystemMessage("Prompt")
        pre_load_data = [AssistantMessage("Data")]
        max_tokens = 1000
        c = ChatContext(messages, system_prompt, pre_load_data, max_tokens)
        self.assertEqual(c.messages, messages)
        self.assertEqual(c.system_prompt, system_prompt)
        self.assertEqual(c.pre_load_data, pre_load_data)
        self.assertEqual(c.max_tokens, max_tokens)

    def test_context_length_in_tokens(self):
        c = ChatContext()
        c.pre_load_data = [UserMessage("Hello", None)]
        c.messages = [UserMessage("World", None)]
        self.assertEqual(
            c.context_length_in_tokens(), 2 + c.system_prompt.encoding_length_in_tokens
        )

    def test_add_message(self):
        c = ChatContext()
        c.messages = [UserMessage("Hello", None)]
        c.add_message(UserMessage("World", None))
        self.assertEqual(len(c.messages), 2)
        self.assertEqual(c.messages[-1].content, "World")

    def test_add_message_str(self):
        c = ChatContext()
        c.messages = [UserMessage("Hello", None)]
        c.add_message("World")
        self.assertEqual(len(c.messages), 2)
        self.assertEqual(c.messages[-1].content, "World")

    def test_add_pre_load_data(self):
        c = ChatContext()
        c.add_pre_load_data(UserMessage("Hello", None))
        self.assertEqual(len(c.pre_load_data), 1)
        self.assertEqual(c.pre_load_data[-1].content, "Hello")

    def test_add_pre_load_data_not_content_message(self):
        c = ChatContext()
        with self.assertRaises(ValueError):
            c.add_pre_load_data("Hello")

    def test_add_pre_load_system_prompt(self):
        c = ChatContext()
        c.add_pre_load_system_prompt(SystemMessage("Hello"))
        self.assertEqual(c.system_prompt.content, "Hello")

    def test_add_pre_load_system_prompt_not_content_message(self):
        c = ChatContext()
        with self.assertRaises(ValueError):
            c.add_pre_load_system_prompt("Hello")

    def test_get_latest_message(self):
        c = ChatContext()
        c.messages = [UserMessage("Hello", None), UserMessage("World", None)]
        self.assertEqual(c.get_latest_message().content, "World")

    def test_reduce_context(self):
        c = ChatContext(max_tokens=10)
        c.messages = [
            UserMessage("hey there!", None),
            AssistantMessage("I'm here to help."),
            UserMessage("really long question?", None),
        ]
        c._reduce_context()
        self.assertEqual(len(c.messages), 1)

    def test_get_messages_as_list(self):
        c = ChatContext()
        c.messages = [UserMessage("Hello", None), UserMessage("World", None)]

        expected = [
            {"content": "", "role": "system"},
            {"content": "Hello", "role": "user"},
            {"content": "World", "role": "user"},
        ]

        self.assertEqual(c.get_messages_as_list(), expected)


if __name__ == "__main__":
    unittest.main()
