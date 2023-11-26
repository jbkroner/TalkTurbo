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