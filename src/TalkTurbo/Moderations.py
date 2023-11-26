class Categories:
    def __iter__(self):
        for attr, value in vars(self).items():
            yield (attr, value)


class CategoryFlags(Categories):
    def __init__(
        self,
        sexual: bool, 
        hate: bool, 
        harassment: bool, 
        self_harm: bool, 
        sexual_minors: bool,
        hate_threatening: bool, 
        violence_graphic: bool,
        self_harm_intent: bool,
        self_harm_instructions: bool,
        harassment_threatening: bool,
        violence: bool
    ) -> None:
        self.sexual = sexual
        self.hate = hate
        self.harassment = harassment
        self.selfharm = self_harm
        self.sexual_minor = sexual_minors
        self.hate_threatening = hate_threatening
        self.violence_graphic = violence_graphic
        self.self_harm_inten = self_harm_intent
        self.self_harm_instruction = self_harm_instructions
        self.harassment_threatening = harassment_threatening
        self.violence = violence

    @classmethod
    def from_moderation_response(cls, response):
        categories = response['results'][0]['categories']
        return cls(
            sexual=categories.get("sexual", False),
            hate=categories.get("hate", False),
            harassment=categories.get("harassment", False),
            self_harm=categories.get("self-harm", False),
            sexual_minors=categories.get("sexual/minors", False),
            hate_threatening=categories.get("hate/threatening", False),
            violence_graphic=categories.get("violence/graphic", False),
            self_harm_intent=categories.get("self-harm/intent", False),
            self_harm_instructions=categories.get("self-harm/instructions", False),
            harassment_threatening=categories.get("harassment/threatening", False),
            violence=categories.get("violence", False)
        )


class CategoryScores(Categories):
    def __init__(
        self,
        sexual: float,
        hate: float,
        harassment: float,
        self_harm: float,
        sexual_minors: float, 
        hate_threatening: float,
        violence_graphic: float,
        self_harm_intent: float,  
        self_harm_instructions:  float, 
        harassment_threatening:  float,
        violence: float
    ) -> None:
        self.sexual = sexual
        self.hate = hate
        self.harassment = harassment
        self.selfharm = self_harm
        self.sexual_minor = sexual_minors
        self.hate_threatening = hate_threatening
        self.violence_graphic = violence_graphic
        self.self_harm_intent = self_harm_intent
        self.self_harm_instruction = self_harm_instructions
        self.harassment_threatening = harassment_threatening
        self.violence = violence

    @classmethod
    def from_moderation_response(cls, response):
        scores = response['results'][0]['category_scores']
        return cls(
            sexual=scores.get("sexual", 0.0),
            hate=scores.get("hate", 0.0),
            harassment=scores.get("harassment", 0.0),
            self_harm=scores.get("self-harm", 0.0),
            sexual_minors=scores.get("sexual/minors", 0.0),
            hate_threatening=scores.get("hate/threatening", 0.0),
            violence_graphic=scores.get("violence/graphic", 0.0),
            self_harm_intent=scores.get("self-harm/intent", 0.0),
            self_harm_instructions=scores.get("self-harm/instructions", 0.0),
            harassment_threatening=scores.get("harassment/threatening", 0.0),
            violence=scores.get("violence", 0.0)
        )