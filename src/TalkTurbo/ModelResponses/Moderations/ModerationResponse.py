from TalkTurbo.ModelResponses.Moderations.ModerationResults import ModerationResults


class ModerationResponse:
    def __init__(self, id: int, model: str, results: ModerationResults) -> None:
        self.id = id
        self.model = model
        self.results: ModerationResults = results

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            id=data["id"],
            model=data["model"],
            results=ModerationResults.from_json(data["results"][0]),
        )
