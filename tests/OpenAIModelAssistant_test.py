import unittest
from unittest.mock import Mock, patch
from TalkTurbo.OpenAIModelAssistant import OpenAIModelAssistant


class TestOpenAIModelAssistant(unittest.TestCase):
    @unittest.skip("broken")
    @patch("TalkTurbo.OpenAIModelAssistant.requests.post")
    def test_get_moderation_score(self, mock_post):
        message = "This is a test message"
        openai_secret_key = "secret"
        expected_result = ("hate", 0.99)
        mock_response = {
            "id": "modr-XXXXX",
            "model": "text-moderation-001",
            "results": [
                {
                    "categories": {
                        "hate": True,
                        "hate/threatening": False,
                        "self-harm": False,
                        "sexual": False,
                        "sexual/minors": False,
                        "violence": False,
                        "violence/graphic": False,
                    },
                    "category_scores": {
                        "hate": 0.99,
                        "hate/threatening": 0.0001250059431185946,
                        "self-harm": 0.0003706029092427343,
                        "sexual": 0.0008735615410842001,
                        "sexual/minors": 0.0007470346172340214,
                        "violence": 0.0041268812492489815,
                        "violence/graphic": 0.00023186142789199948,
                    },
                    "flagged": False,
                }
            ],
        }
        mock_post.return_value.json.return_value = mock_response
        assistant = OpenAIModelAssistant()

        result = assistant.get_moderation_score(message, openai_secret_key)

        self.assertEqual(result, expected_result)
        mock_post.assert_called_once_with(
            url="https://api.openai.com/v1/moderations",
            json={"input": message},
            headers={"authorization": f"Bearer {openai_secret_key}"},
        )

    def test_category_score(self):
        moderation_response = {
            "results": [
                {
                    "categories": {
                        "hate": True,
                        "hate/threatening": False,
                        "self-harm": False,
                        "sexual": False,
                        "sexual/minors": False,
                        "violence": False,
                        "violence/graphic": False,
                    },
                    "category_scores": {
                        "hate": 0.99,
                        "hate/threatening": 0.0001250059431185946,
                        "self-harm": 0.0003706029092427343,
                        "sexual": 0.0008735615410842001,
                        "sexual/minors": 0.0007470346172340214,
                        "violence": 0.0041268812492489815,
                        "violence/graphic": 0.00023186142789199948,
                    },
                    "flagged": False,
                }
            ]
        }
        expected_result = ("hate", 0.99)
        assistant = OpenAIModelAssistant()

        result = assistant._category_score(moderation_response)

        self.assertEqual(result, expected_result)

    def test_category_score_no_harmful_category(self):
        moderation_response = {
            "results": [
                {
                    "categories": {
                        "hate": False,
                        "hate/threatening": False,
                        "self-harm": False,
                        "sexual": False,
                        "sexual/minors": False,
                        "violence": False,
                        "violence/graphic": False,
                    },
                    "category_scores": {
                        "hate": 0.0,
                        "hate/threatening": 0.0,
                        "self-harm": 0.0,
                        "sexual": 0.0,
                        "sexual/minors": 0.0,
                        "violence": 0.0,
                        "violence/graphic": 0.0,
                    },
                    "flagged": False,
                }
            ]
        }
        expected_result = (None, 0.0)
        assistant = OpenAIModelAssistant()

        result = assistant._category_score(moderation_response)

        self.assertEqual(result, expected_result)
