from TalkTurbo.Metering.TurboInteraction import TurboInteraction


class Meter:
    """
    A Meter object tracks usage across a guild.
    """

    def __init__(self, guild_id: int) -> None:
        self.guild_id = guild_id
        self.interactions_log: dict = {}

    def add_interaction(self, interaction: TurboInteraction):
        # ensure that this interaction belongs to this guild
        if interaction.guild_id != self.guild_id:
            raise ValueError(
                f"cannot add interaction guild_id ({interaction.guild_id}) to the meter for guild_id {self.guild_id}"
            )

        self.interactions_log[interaction.interaction_id] = interaction

    def total_prompt_tokens(self) -> int:
        return sum(
            interaction.prompt_tokens_used
            for interaction in self.interactions_log.values()
        )

    def total_completion_tokens(self) -> int:
        return sum(
            interaction.completion_tokens_used
            for interaction in self.interactions_log.values()
        )

    def total_dalle_images(self) -> int:
        return sum(
            interaction.isDalle for interaction in self.interactions_log.values()
        )

    def __str__(self) -> str:
        return (
            f"guild_id: {self.guild_id}, "
            f"total interactions: {len(self.interactions_log)}, "
            f"total prompt tokens: {self.total_prompt_tokens()}, "
            f"total completion tokens: {self.total_completion_tokens()}, "
            f"total dalle images: {self.total_dalle_images()}"
        )
