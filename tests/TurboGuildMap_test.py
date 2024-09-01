import unittest

from TalkTurbo.Messages import UserMessage
from TalkTurbo.TurboGuild import TurboGuildMap


class TurboGuildMapTest(unittest.TestCase):
    def test_single_guid(self):
        guild_map = TurboGuildMap()
        guild = guild_map.get("123")
        self.assertEqual(guild.id, "123")

    def test_multiple_guids(self):
        guild_map = TurboGuildMap()
        guild1 = guild_map.get("123")
        guild2 = guild_map.get("456")
        self.assertEqual(guild1.id, "123")
        self.assertEqual(guild2.id, "456")

    def test_multi_guild_unique_context(self):
        guild_map = TurboGuildMap()
        guild1 = guild_map.get("123")
        guild2 = guild_map.get("456")

        guild1.chat_context.add_message(UserMessage("hello"))

        self.assertNotEqual(
            guild1.chat_context.get_messages_as_list(),
            guild2.chat_context.get_messages_as_list(),
        )

    def test_single_guild_reference(self):
        """sanity test: test that the same guild is returned when the same id is used."""
        guild_map = TurboGuildMap()
        guild = guild_map.get("123")
        guild.chat_context.add_message(UserMessage("hello"))

        guild2 = guild_map.get("123")

        self.assertEqual(guild, guild2)
        self.assertEqual(
            guild.chat_context.get_messages_as_list(),
            guild2.chat_context.get_messages_as_list(),
        )
