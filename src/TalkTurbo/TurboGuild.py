"""TurboGuilds track context and usage for a Discord Guild"""

from TalkTurbo.ChatContext import ChatContext
from typing import Dict


class TurboGuild:
    def __init__(self, id, chat_context=ChatContext()) -> None:
        self.id = id
        self.chat_context = chat_context


class TurboGuildMap:
    def __init__(self, guild_map: dict[str, TurboGuild] = {}) -> None:
        self._guild_map: dict[str, TurboGuild] = guild_map

    def get(self, id: str) -> TurboGuild:
        guild = self._guild_map.get(id, None)

        # create the guild if it does not exist in memory
        # eventually we will need to pull the guid data from
        # a db, not just construct a bare TurboGuild
        if not guild:
            self._guild_map[id] = TurboGuild(id)
