import unittest
from TalkTurbo.ModelResponses.Choice import Choice
from TalkTurbo.ModelResponses.Message import Message


class TestChoice(unittest.TestCase):
    def test_from_dict(self):
        data = {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "\n\nHello there, how may I assist you today?",
            },
            "finish_reason": "stop",
        }
        choice = Choice.from_dict(data)

        self.assertEqual(choice.index, 0)
        self.assertIsInstance(choice.message, Message)
        self.assertEqual(choice.message.role, "assistant")
        self.assertEqual(
            choice.message.content, "\n\nHello there, how may I assist you today?"
        )
        self.assertEqual(choice.finish_reason, "stop")

    def test_choice_attributes(self):
        message = Message(
            role="assistant", content="\n\nHello there, how may I assist you today?"
        )
        choice = Choice(index=0, message=message, finish_reason="stop")

        self.assertEqual(choice.index, 0)
        self.assertIsInstance(choice.message, Message)
        self.assertEqual(choice.message.role, "assistant")
        self.assertEqual(
            choice.message.content, "\n\nHello there, how may I assist you today?"
        )
        self.assertEqual(choice.finish_reason, "stop")


if __name__ == "__main__":
    unittest.main()
