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
        self.isDalle = isDalle

    def __str__(self) -> str:
        return (
            f"interaction_id: {self.interaction_id}"
            f"interaction_time: {self.interaction_time}"
            f"guild_id: {self.guild_id}"
            f"hashed_user_identifer: {self.hashed_user_identifier}"
            f"prompt_tokens_used: {self.prompt_tokens_used}"
            f"completion_tokens_used: {self.completion_tokens_used}"
            f"isDalle: {self.isDalle}"
        )
