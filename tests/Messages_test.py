import unittest
from unittest.mock import patch
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
        with patch('requests.post', return_value=unittest.mock.Mock(json=lambda: mock_moderation_response)) as mock_post:
            msg = ContentMessage(MessageRole.USER, "Some potentially sensitive content")
            msg.moderate()

            self.assertTrue(mock_post.called)
            self.assertTrue(msg._flagged)
            self.assertIsInstance(msg._category_flags, CategoryFlags)
            self.assertIsInstance(msg._category_scores, CategoryScores)

    def test_moderate_method(self):
        with patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = mock_moderation_response
            msg = ContentMessage(MessageRole.USER, "Some content")
            msg.moderate()

            self.assertTrue(msg._moderated)
            self.assertTrue(msg._flagged)
            self.assertIsInstance(msg._category_flags, CategoryFlags)
            self.assertIsInstance(msg._category_scores, CategoryScores)

    def test_flagged_method(self):
        with patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = mock_moderation_response
            msg = ContentMessage(MessageRole.USER, "Some content")
            
            result = msg.flagged()
            
            self.assertTrue(mock_post.called) # Check if moderate() was called
            self.assertTrue(result)

    def test_get_category_flags_method(self):
        with patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = mock_moderation_response
            msg = ContentMessage(MessageRole.USER, "Some content")
            
            result = msg.get_category_flags()
            
            self.assertTrue(mock_post.called) # Check if moderate() was called
            self.assertIsInstance(result, CategoryFlags)

    def test_get_category_scores_method(self):
        with patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = mock_moderation_response
            msg = ContentMessage(MessageRole.USER, "Some content")
            
            result = msg.get_category_scores()
            
            self.assertTrue(mock_post.called) # Check if moderate() was called
            self.assertIsInstance(result, CategoryScores)

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
