import unittest
from TalkTurbo.Messages import MessageRole, SystemMessage, UserMessage, AssistantMessage, FunctionMessage, ToolMessage, ContentMessage
from TalkTurbo.Moderations import CategoryFlags, CategoryScores

# Mock response for moderation
mock_moderation_response = {
    "results": [
        {
            "flagged": True,
            "categories": {
                "sexual": False,
                # ... other categories ...
                "violence": True,
            },
            "category_scores": {
                "sexual": 0.1,
                # ... other categories ...
                "violence": 0.9,
            }
        }
    ]
}

class TestMessageClasses(unittest.TestCase):
    
    def test_content_message_creation(self):
        msg = ContentMessage(MessageRole.USER, "Hello, world!")
        self.assertEqual(msg.role, MessageRole.USER)
        self.assertEqual(msg.content, "Hello, world!")
        self.assertIsNotNone(msg.created_on_utc)
        self.assertIsNotNone(msg.encoding)
        self.assertTrue(isinstance(msg.encoding_length_in_tokens, int))

    def test_moderation(self):
        # Mock the requests.post method
        with unittest.mock.patch('requests.post', return_value=unittest.mock.Mock(json=lambda: mock_moderation_response)) as mock_post:
            msg = ContentMessage(MessageRole.USER, "Some potentially sensitive content")
            msg.moderate()

            self.assertTrue(mock_post.called)
            self.assertTrue(msg._flagged)
            self.assertIsInstance(msg._category_flags, CategoryFlags)
            self.assertIsInstance(msg._category_scores, CategoryScores)

    def test_system_message_creation(self):
        msg = SystemMessage("System message")
        self.assertEqual(msg.role, MessageRole.SYSTEM)
        self.assertEqual(msg.content, "System message")

    def test_user_message_creation(self):
        msg = UserMessage("User message")
        self.assertEqual(msg.role, MessageRole.USER)
        self.assertEqual(msg.content, "User message")

    def test_assistant_message_creation(self):
        msg = AssistantMessage("Assistant message")
        self.assertEqual(msg.role, MessageRole.ASSISTANT)
        self.assertEqual(msg.content, "Assistant message")

    def test_to_completion_dict(self):
        content = "Test content"
        msg = ContentMessage(MessageRole.ASSISTANT, content)
        completion_dict = msg.to_completion_dict()
        self.assertEqual(completion_dict, {"role": MessageRole.ASSISTANT.value, "content": content})

if __name__ == '__main__':
    unittest.main()
