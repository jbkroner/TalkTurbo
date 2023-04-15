from discord import Guild


from ChatContext import ChatContext
from TurboTier import TurboTier


class TurboGuild:
    def __init__(self, id) -> None:
        self.id = id
        self.chat_context = ChatContext()
        self.messages_sent = 0
        self.tokens_used = 0
        self.turbo_tier = TurboTier.FREE
