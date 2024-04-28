import yaml

from TalkTurbo.Messages import (
    AssistantMessage,
    ContentMessage,
    MessageRole,
    SystemMessage,
    UserMessage,
)


def _validate_pre_load_data(pre_load_data: dict):
    if not isinstance(pre_load_data["system_prompt"], str):
        raise TypeError(
            f"Pre-load system prompt must be a string.  Data: {pre_load_data}"
        )

    if not isinstance(pre_load_data["context"], list):
        raise TypeError(
            f"Pre-load context data must be a list of dictionaries.  pre-load['context']: {pre_load_data.get('context')}"
        )

    for item in pre_load_data["context"]:
        if not isinstance(item, dict):
            raise TypeError(
                f"Each item in the pre-load data must be a dictionary.  Data: {item}"
            )
        if (
            MessageRole.USER.value not in item
            or MessageRole.ASSISTANT.value not in item
        ):
            raise ValueError(
                f"Each item in the pre-load data must have a user and system message.  Data: {item}"
            )


def get_pre_load_data(path: str) -> tuple[list[ContentMessage], SystemMessage]:
    with open(path, "r", encoding="utf-8") as file:
        pre_load_data = yaml.safe_load(file)

    _validate_pre_load_data(pre_load_data)

    # convert to UserMessage and SystemMessage objects
    pre_load_messages = []

    for item in pre_load_data["context"]:
        user_message = UserMessage(item[MessageRole.USER.value])
        system_message = AssistantMessage(item[MessageRole.ASSISTANT.value])
        pre_load_messages.append(user_message)
        pre_load_messages.append(system_message)

    system_message = SystemMessage(pre_load_data.get("system_prompt", ""))

    return pre_load_messages, system_message
