from enum import Enum


class ModerationCategories(Enum):
    """
    Moderation categories from https://platform.openai.com/docs/api-reference/moderations
    """

    HATE = "hate"
    HATE_THREATENING = "hate/threatening"
    SELF_HARM = "self-harm"
    SEXUAL = "sexual"
    SEXUAL_MINORS = "sexual/minors"
    VIOLENCE = "violence"
    VIOLENCE_GRAPHIC = "violence/graphic"
