import unittest
from datetime import datetime

from TalkTurbo.ModelResponses.ChatCompletionResponse import ChatCompletionResponse
from TalkTurbo.ModelResponses.Usage import Usage
from TalkTurbo.ModelResponses.Choice import Choice


class TestChatCompletionResponse(unittest.TestCase):
    def test_from_dict(self):
        data = {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1677652288,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "\n\nHello there, how may I assist you today?",
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 9, "completion_tokens": 12, "total_tokens": 21},
        }
        response = ChatCompletionResponse.from_dict(data)

        self.assertEqual(response.id, "chatcmpl-123")
        self.assertEqual(response.object, "chat.completion")
        self.assertEqual(response.created, datetime.fromtimestamp(1677652288))
        self.assertIsInstance(response.choices[0], Choice)
        self.assertIsInstance(response.usage, Usage)

    def test_chat_completion_response_attributes(self):
        created_datetime = datetime.fromtimestamp(1677652288)
        choice = Choice(
            index=0,
            message={
                "role": "assistant",
                "content": "\n\nHello there, how may I assist you today?",
            },
            finish_reason="stop",
        )
        usage = Usage(prompt_tokens=9, completion_tokens=12, total_tokens=21)
        response = ChatCompletionResponse(
            id_="chatcmpl-123",
            object_="chat.completion",
            created=created_datetime,
            choices=[choice],
            usage=usage,
        )

        self.assertEqual(response.id, "chatcmpl-123")
        self.assertEqual(response.object, "chat.completion")
        self.assertEqual(response.created, created_datetime)
        self.assertIsInstance(response.choices[0], Choice)
        self.assertIsInstance(response.usage, Usage)


if __name__ == "__main__":
    unittest.main()
