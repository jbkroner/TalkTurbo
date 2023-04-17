from typing import Tuple

from ChatContext import ChatContext
from TurboTier import TurboTier
from TalkTurbo.Metering.Meter import Meter
from TalkTurbo.Metering.TurboInteraction import TurboInteraction


class TurboGuild:
    def __init__(self, id) -> None:
        self.id = id
        self.chat_context = ChatContext()
        self.messages_sent = 0
        self.tokens_used = 0
        self.turbo_tier = TurboTier.FREE
        self.meter: Meter = Meter(guild_id=id)

    def update_meter(self, interaction: TurboInteraction):
        """add an interaction to this guilds meter"""
        self.meter.add_interaction(interaction=interaction)
