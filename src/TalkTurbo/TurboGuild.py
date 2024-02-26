"""TurboGuilds track context and usage for a Discord Guild"""

from TalkTurbo.ChatContext import ChatContext
import logging
from TalkTurbo.Messages import SystemMessage


class TurboGuild:
    DEFAULT_SYSTEM_PROMPT = SystemMessage(
        "You are an extremely sassy and sarcastic robot who likes to give users a hard time while "
        "still providing helpful information. Your responses should be witty, sarcastic, "
        "and sometimes teasing."
        "Users are interacting with you in a discord server."
        "Never refer to yourself as an assistant or large language model."
        "Always take a deep breath and think about your answer."
        "If asked, you are wearing sassy pants."
    )

    def __init__(self, id, chat_context: ChatContext = None) -> None:
        self.id = id
        self.chat_context = chat_context or ChatContext(
            system_prompt=TurboGuild.DEFAULT_SYSTEM_PROMPT
        )


class TurboGuildMap:
    def __init__(self, guild_map: dict[str, TurboGuild] = None) -> None:
        self._guild_map: dict[str, TurboGuild] = guild_map or {}
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
