from typing import Tuple
from logging import Logger

from ChatContext import ChatContext
from TurboTier import TurboTier
from TalkTurbo.Metering.Meter import Meter
from TalkTurbo.Metering.TurboInteraction import TurboInteraction


class TurboGuild:
    def __init__(self, id, logger: Logger) -> None:
        self.id = id
        self.chat_context = ChatContext()
        self.messages_sent = 0
        self.tokens_used = 0
        self.turbo_tier = TurboTier.FREE
        self.meter: Meter = Meter(guild_id=id)
        self.logger = logger

    def update_meter(self, interaction: TurboInteraction):
        """add an interaction to this guilds meter"""
        self.logger.info(
            f"guild {self.id}: adding interaction {interaction.interaction_id} to meter"
        )
        self.logger.debug(
            f"guild {self.id}: debug interaction info ->\n{str(interaction)}"
        )
        self.logger.debug(f"guild {self.id} usage:\n{str(self.meter)}")
        self.meter.add_interaction(interaction=interaction)
