import unittest

from TalkTurbo.ModelResponses.Usage import Usage


class TestUsage(unittest.TestCase):
    def test_from_dict(self):
        data = {"prompt_tokens": 9, "completion_tokens": 12, "total_tokens": 21}
        usage = Usage.from_dict(data)

        self.assertEqual(usage.prompt_tokens, 9)
        self.assertEqual(usage.completion_tokens, 12)
        self.assertEqual(usage.total_tokens, 21)

    def test_usage_attributes(self):
        usage = Usage(prompt_tokens=9, completion_tokens=12, total_tokens=21)

        self.assertEqual(usage.prompt_tokens, 9)
        self.assertEqual(usage.completion_tokens, 12)
        self.assertEqual(usage.total_tokens, 21)


if __name__ == "__main__":
    unittest.main()
