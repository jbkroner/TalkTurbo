"""TurboGuilds track context and usage for a Discord Guild"""

from TalkTurbo.ChatContext import ChatContext
import logging


class TurboGuild:
    def __init__(self, id, chat_context: ChatContext = None) -> None:
        self.id = id
        self.chat_context = chat_context or ChatContext()


class TurboGuildMap:
    def __init__(self, guild_map: dict[str, TurboGuild] = {}) -> None:
        self._guild_map: dict[str, TurboGuild] = guild_map
        self._logger = logging.getLogger("Turbo")
        self._logger.info("created new turbo guild map!")

    def get(self, id: str) -> TurboGuild:
        guild = self._guild_map.get(id, None)

        # create the guild if it does not exist in memory
        # eventually we will need to pull the guid data from
        # a db, not just construct a bare TurboGuild
        if not guild:
            self._logger.info(
                "could not find guild %s, adding new TurboGuild instance to guild map",
                id,
            )
            self._guild_map[id] = TurboGuild(id)
            guild = self._guild_map.get(id)

        return guild
