import unittest
from TalkTurbo.ModelResponses.Message import Message


class TestMessage(unittest.TestCase):
    def test_from_dict(self):
        data = {
            "role": "assistant",
            "content": "\n\nHello there, how may I assist you today?",
        }
        message = Message.from_dict(data)

        self.assertEqual(message.role, "assistant")
        self.assertEqual(
            message.content, "\n\nHello there, how may I assist you today?"
        )

    def test_message_attributes(self):
        message = Message(
            role="assistant", content="\n\nHello there, how may I assist you today?"
        )

        self.assertEqual(message.role, "assistant")
        self.assertEqual(
            message.content, "\n\nHello there, how may I assist you today?"
        )


if __name__ == "__main__":
    unittest.main()
