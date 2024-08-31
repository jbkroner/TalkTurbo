import unittest

from TalkTurbo.Moderations import CategoryFlags, CategoryScores


class TestCategories(unittest.TestCase):
    def test_category_flags_initialization(self):
        flags = CategoryFlags(
            True, False, True, False, True, False, True, False, True, False, True
        )
        self.assertTrue(flags.sexual)
        self.assertFalse(flags.hate)
        self.assertTrue(flags.harassment)
        self.assertFalse(flags.selfharm)
        self.assertTrue(flags.sexual_minor)
        self.assertFalse(flags.hate_threatening)
        self.assertTrue(flags.violence_graphic)
        self.assertFalse(flags.self_harm_inten)
        self.assertTrue(flags.self_harm_instruction)
        self.assertFalse(flags.harassment_threatening)
        self.assertTrue(flags.violence)

    def test_category_scores_initialization(self):
        scores = CategoryScores(0.5, 0.2, 0.8, 0.1, 0.6, 0.3, 0.9, 0.4, 0.7, 0.5, 0.2)
        self.assertEqual(scores.sexual, 0.5)
        self.assertEqual(scores.hate, 0.2)
        self.assertEqual(scores.harassment, 0.8)
        self.assertEqual(scores.selfharm, 0.1)
        self.assertEqual(scores.sexual_minor, 0.6)
        self.assertEqual(scores.hate_threatening, 0.3)
        self.assertEqual(scores.violence_graphic, 0.9)
        self.assertEqual(scores.self_harm_intent, 0.4)
        self.assertEqual(scores.self_harm_instruction, 0.7)
        self.assertEqual(scores.harassment_threatening, 0.5)
        self.assertEqual(scores.violence, 0.2)

    def test_category_flags_iteration(self):
        flags = CategoryFlags(
            True, False, True, False, True, False, True, False, True, False, True
        )
        expected = [
            ("sexual", True),
            ("hate", False),
            ("harassment", True),
            ("selfharm", False),
            ("sexual_minor", True),
            ("hate_threatening", False),
            ("violence_graphic", True),
            ("self_harm_inten", False),
            ("self_harm_instruction", True),
            ("harassment_threatening", False),
            ("violence", True),
        ]
        for i, (category, status) in enumerate(flags):
            self.assertEqual((category, status), expected[i])

    def test_category_scores_iteration(self):
        scores = CategoryScores(0.5, 0.2, 0.8, 0.1, 0.6, 0.3, 0.9, 0.4, 0.7, 0.5, 0.2)
        expected = [
            ("sexual", 0.5),
            ("hate", 0.2),
            ("harassment", 0.8),
            ("selfharm", 0.1),
            ("sexual_minor", 0.6),
            ("hate_threatening", 0.3),
            ("violence_graphic", 0.9),
            ("self_harm_intent", 0.4),
            ("self_harm_instruction", 0.7),
            ("harassment_threatening", 0.5),
            ("violence", 0.2),
        ]
        for i, (category, score) in enumerate(scores):
            self.assertEqual((category, score), expected[i])

    def test_from_moderation_response_flags(self):
        response = {
            "results": [
                {
                    "categories": {
                        "sexual": True,
                        "hate": False,
                        "harassment": True,
                        "self-harm": False,
                        "sexual/minors": True,
                        "hate/threatening": False,
                        "violence/graphic": True,
                        "self-harm/intent": False,
                        "self-harm/instructions": True,
                        "harassment/threatening": False,
                        "violence": True,
                    }
                }
            ]
        }
        flags = CategoryFlags.from_moderation_response(response)
        self.assertTrue(flags.sexual)
        self.assertFalse(flags.hate)
        self.assertTrue(flags.harassment)
        self.assertFalse(flags.selfharm)
        self.assertTrue(flags.sexual_minor)
        self.assertFalse(flags.hate_threatening)
        self.assertTrue(flags.violence_graphic)
        self.assertFalse(flags.self_harm_inten)
        self.assertTrue(flags.self_harm_instruction)
        self.assertFalse(flags.harassment_threatening)
        self.assertTrue(flags.violence)

    def test_from_moderation_response_scores(self):
        response = {
            "results": [
                {
                    "category_scores": {
                        "sexual": 0.5,
                        "hate": 0.2,
                        "harassment": 0.8,
                        "self-harm": 0.1,
                        "sexual/minors": 0.6,
                        "hate/threatening": 0.3,
                        "violence/graphic": 0.9,
                        "self-harm/intent": 0.4,
                        "self-harm/instructions": 0.7,
                        "harassment/threatening": 0.5,
                        "violence": 0.2,
                    }
                }
            ]
        }
        scores = CategoryScores.from_moderation_response(response)
        self.assertEqual(scores.sexual, 0.5)
        self.assertEqual(scores.hate, 0.2)
        self.assertEqual(scores.harassment, 0.8)
        self.assertEqual(scores.selfharm, 0.1)
        self.assertEqual(scores.sexual_minor, 0.6)
        self.assertEqual(scores.hate_threatening, 0.3)
        self.assertEqual(scores.violence_graphic, 0.9)
        self.assertEqual(scores.self_harm_intent, 0.4)
        self.assertEqual(scores.self_harm_instruction, 0.7)
        self.assertEqual(scores.harassment_threatening, 0.5)
        self.assertEqual(scores.violence, 0.2)


if __name__ == "__main__":
    unittest.main()
