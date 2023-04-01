# Turbo

Turbo is a quick and dirty chatbot that combines Discord.py and the OpenAI api. It queries the GPT 3.5 Turbo model.

Add your discord and OpenAI API keys to a .env file, create a discord bot on the discord developer portal, and have fun!

## Moderation

All messages sent to Turbo are routed through the [OpenAI Moderation Endpoint](https://platform.openai.com/docs/guides/moderation). If any of the listed categories return as `true` then the message is not passed along to the gpt model and the user is warned.
