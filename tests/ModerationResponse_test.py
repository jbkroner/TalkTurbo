import unittest
import json
from TalkTurbo.ModelResponses.Moderations.ModerationResponse import ModerationResponse
from TalkTurbo.ModelResponses.Moderations.ModerationResults import ModerationResults
from TalkTurbo.ModelResponses.Moderations.ModerationCategories import (
    ModerationCategories,
)


class TestModerationResults(unittest.TestCase):
    def test_from_json(self):
        moderation_response_data = {
            "id": "modr-5MWoLO",
            "model": "text-moderation-001",
            "results": [
                {
                    "category_scores": {
                        "hate": 0.22714105248451233,
                        "hate/threatening": 0.4132447838783264,
                        "self-harm": 0.005232391878962517,
                        "sexual": 0.01407341007143259,
                        "sexual/minors": 0.0038522258400917053,
                        "violence": 0.9223177433013916,
                        "violence/graphic": 0.036865197122097015,
                    },
                    "flagged": True,
                }
            ],
        }

        moderation_results = ModerationResults.from_json(moderation_response_data)
        expected_category_scores = {
            ModerationCategories.HATE: 0.22714105248451233,
            ModerationCategories.HATE_THREATENING: 0.4132447838783264,
            ModerationCategories.SELF_HARM: 0.005232391878962517,
            ModerationCategories.SEXUAL: 0.01407341007143259,
            ModerationCategories.SEXUAL_MINORS: 0.0038522258400917053,
            ModerationCategories.VIOLENCE: 0.9223177433013916,
            ModerationCategories.VIOLENCE_GRAPHIC: 0.036865197122097015,
        }

        self.assertEqual(moderation_results.flagged, True)
        self.assertEqual(moderation_results.category_scores, expected_category_scores)


if __name__ == "__main__":
    unittest.main()
