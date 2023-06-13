# TalkTurbo

TalkTurbo is a lightweight chatbot platform for Discord that queries the OpenAI GPT 3.5 Turbo model.  TalkTurbo features simple controls for system prompting, context management, response length, and temperature.  It also utilizes the OpenAI Moderation Endpoint to protect your API key from abuse.   

Once TalkTurbo is added to your server you can talk to the bot by @ing it or using the slash commands.  Occasionally TalkTurbo will respond to messages on its own!

## Usage
- Clone this repo and `cd` into it.
- Setup a Discord App+Bot in the [Discord Developer Portal](https://discord.com/developers/docs/intro) + aquire the bot's key.  The [Discord.py docs](https://discordpy.readthedocs.io/en/stable/discord.html) have a good writeup on this.  
- Aquire an [OpenAI API key](https://platform.openai.com/account/api-keys). 
- Windows:
  - create a `.env` in the `TurboTalk` directory and add the following to it:
    ```
    DISCORD_SECRET_KEY=<discord_secret_key>
    OPENAI_SECRET_KEY=<openai_secret_key>
    ```  
- Linux / MacOS:
    - Export your keys as enviroment vars:
        - `$ export DISCORD_SECRET_KEY=<discord_secret_key>`
        - `$ export OPENAI_SECRET_KEY=<openai_secret_key>`

- Run the bot:
    - Windows: `> python ./src/TurboTalk/turbo.py`
    - Linux / MacOS: `$ python3 ./src/TurboTalk/turbo.py`

## Args

`-h`, `--help` - show this help message and exit
  
`-s`, `--system-prompt` - system prompt to initialize the bot with.
  
`-t`, `--temperature` - sampling temperature, in range [0, 2.0].  A lower temperature will give more deterministic responses.  Default is .7.

`-m` , `--max-response-length` - Max response length in tokens.  Defaults to 100.

`--sync-app-commands` - Sync new or udpated app commands with Discord 

`--no-user-identifier` - Do *not* send a user's unique hash to OpenAI with each request. 

`--disable-image-storage` - Do not store dalle images locally.  Image prompts and hashes may still be logged. 

## Slash Commands
Slash commands can be used within a Discord server to control the bot.

`/turbo` - talk to turbo!

`/generate_image` - enter a prompt and generate a DALL-E image.  Timeout defaults to 60 seconds.

`/estop` - shut down the bot. use at your discretion if you spot spam, abuse, or other problems. 

`/set_temperature` - set the bots temperature, in range [0, 2.0].

`/set_system_prompt` - set the bot's system prompt

`/clear_context` - clear the bot's context (except for the system prompt)

## Notes on Context Tracking
The bot tracks the 'context' of a conversation so that replies stay on topic.  Also included in the context is the system prompt.  Currently the context is set to a max length of 1024 tokens.  During every exchange with the bot the most recent message + response are appended to the context.  If the length goes over the limit then the oldest messages are removed from the context until the context fits within the max allowed length.  The system prompt is never removed from the context. 

If you notice the bot 'forgetting' things you told it is most likely that the relevant messages got bumped out of the bots context.  

The `gpt-3.5-turbo` model supports a context of up to 4096 tokens.  You may increase the max amount if you wish (and you should see improved recall from the bot), just keep in mind that the OpenAI API charges by the token.  In regular usage the context is almost always filled so you can expect a roughly 4* token usage increase if you raise the max allowed tokens to the limit supported by the `gpt-3.5-turbo` model. 

## Moderation

All system prompts and messages sent to Turbo are routed through the [OpenAI Moderation Endpoint](https://platform.openai.com/docs/guides/moderation). If any of the listed categories return as `true` then the message is not passed along to the gpt model and the user is warned.
