from TalkTurbo.ModelResponses.Moderations.ModerationCategories import (
    ModerationCategories,
)


class ModerationResults:
    def __init__(self, category_scores: dict, flagged: bool) -> None:
        self.category_scores = {}

        for category in ModerationCategories.__members__.values():
            self.category_scores[category] = category_scores[category.value]

        self.flagged = flagged

    @classmethod
    def from_json(cls, moderation_response_data: dict):
        return cls(
            category_scores=moderation_response_data["results"][0]["category_scores"],
            flagged=moderation_response_data["results"][0]["flagged"],
        )
