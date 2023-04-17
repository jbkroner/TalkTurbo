from datetime import datetime


class TurboInteraction:
    """
    A TurboInteraction object is used for tracking / logging
    completed interactions with the bot.
    """

    def __init__(
        self,
        interaction_id: int,
        interaction_time: datetime,
        guild_id: int,
        hashed_user_identifier: int,
        prompt_tokens_used: int,
        completion_tokens_used: int,
        isDalle: bool = False,
    ) -> None:
        self.interaction_id = interaction_id
        self.interaction_time = interaction_time
        self.guild_id = guild_id
        self.hashed_user_identifier = hashed_user_identifier
        self.prompt_tokens_used = prompt_tokens_used
        self.completion_tokens_used = completion_tokens_used
        self.isDalle = False
