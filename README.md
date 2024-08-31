# TalkTurbo

TalkTurbo is a lightweight chatbot platform for Discord that can query a variety of large language models.  TalkTurbo features simple controls for system prompting, context management, and Dalle-E image generation.  It also utilizes the OpenAI Moderation Endpoint to protect your API keys from abuse.

Once TalkTurbo is added to your server you can talk to the bot by @ing it or using the slash commands.

## Usage
- Clone this repo and `cd` into it.
- Setup a Discord App+Bot in the [Discord Developer Portal](https://discord.com/developers/docs/intro) + aquire the bot's key.  The [Discord.py docs](https://discordpy.readthedocs.io/en/stable/discord.html) have a good writeup on this.
- Aquire an [OpenAI API key](https://platform.openai.com/account/api-keys).
- Store environment vars in a `.env` file:
  - Create a `.env` file in the `TalkTurbo` directory and add the following to it:
    ```
    DISCORD_SECRET_KEY=<discord_secret_key>
    OPENAI_SECRET_KEY=<openai_secret_key>
    ```
- Alternatively:
    - Export your keys as enviroment vars:
        - `$ export DISCORD_SECRET_KEY=<discord_secret_key>`
        - `$ export OPENAI_SECRET_KEY=<openai_secret_key>`

- Run the bot:
    - Windows: `> python ./src/TurboTalk/turbo.py`
    - Linux / MacOS: `$ python3 ./src/TurboTalk/turbo.py`

## Run with Docker
The docker image is not currently distributed on the Docker hub but it is easy to build locally.
- Clone this repo and `cd` into it.
- Build the container: `docker build -t turbo:latest .`
- Run the container: `docker run -d --env-file .env turbo:latest`


## Args

`-h`, `--help` - show this help message and exit

`--sync-app-commands` - sync new or udpated app commands with Discord.  This will sync commands globally with all guilds that your instance of Turbo has joined.

`--no-user-identifier` - do *not* send a user's unique hash to OpenAI with each request.

`--disable-image-storage` - do not store dalle images locally.  Image prompts and hashes may still be logged.

## Slash Commands
Slash commands can be used within a Discord server to control the bot.

`/generate_image_dalle_3` - enter a prompt and generate a DALL-E-3 image.

`/estop` - shut down the bot. use at your discretion if you spot spam, abuse, or other problems.

`/list_models` - list available models.

`/list_current_model` - list model turbo is currently using.

`/set_model` - set the model that turbo will use.

## Notes on Context Tracking
The bot tracks the 'context' of a conversation so that replies stay on topic.  Also included in the context is the system prompt.  Currently the context is set to a max length of 1024 tokens.  During every exchange with the bot the most recent message + response are appended to the context.  If the length goes over the limit then the oldest messages are removed from the context until the context fits within the max allowed length.  Messages older than 24 hours are also dropped. The system prompt is never removed from the context.

If you notice the bot 'forgetting' things you told it is most likely that the relevant messages got bumped out of the bots context.

The `gpt-3.5-turbo` model supports a context of up to 4096 tokens.  You may increase the max amount if you wish (and you should see improved recall from the bot), just keep in mind that the OpenAI API charges by the token.  In regular usage the context is almost always filled so you can expect a roughly 4* token usage increase if you raise the max allowed tokens to the limit supported by the `gpt-3.5-turbo` model.

![chat](./docs/media/turbo_chatcontext.PNG)

## Moderation

All system prompts and messages sent to Turbo are routed through the [OpenAI Moderation Endpoint](https://platform.openai.com/docs/guides/moderation).  OpenAI moderation happens regardless of which chat model Turbo is currently using. Messages track their own moderation data and you can quickly check a messages moderation status with `message.flagged()`.

## Pre-load data
Pre-load data can be used to inject custom system prompts and conversational context.  Pre-load data is tracked seperately from the standard context.  Pre-load data is included when calculating context size.

```yaml
system_prompt: |
    "You are an orange cat named Jones"
    "You are cheerful and like to meow"

context:
    - user: "Hey Jones!"
      assistant: "Meow, hey there! How can I help you?"
    - user: "Hey Jones, where do you like to hang out?"
      assistant: "My favorite spot is the pilot's seat.  It has the best view! Meow!"
```


You can use the `--pre-load-context <path>` arg to pass in pre-load data. If no path is passed in `pre-load.yaml` will be used.  There is an example of [`pre-load.yaml`](./pre-load.yaml) provided in this repository.
