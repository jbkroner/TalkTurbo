# TalkTurbo

TalkTurbo is a lightweight chatbot platform for Discord that can query a variety of large language models. It features simple controls for system prompting, context management, and DALL-E image generation. It also utilizes the OpenAI Moderation Endpoint to protect your API keys from abuse.

Once TalkTurbo is added to your server, you can talk to the bot by @mentioning it or using slash commands.

## Table of Contents
- [TalkTurbo](#talkturbo)
  - [Table of Contents](#table-of-contents)
  - [Setup](#setup)
  - [Usage](#usage)
  - [Run with Docker](#run-with-docker)
  - [Command Line Arguments](#command-line-arguments)
  - [Slash Commands](#slash-commands)
  - [Context Tracking](#context-tracking)
  - [Moderation](#moderation)
  - [Pre-load Data](#pre-load-data)
  - [Development](#development)
  - [Running GitHub Actions Locally](#running-github-actions-locally)
    - [Installing Act](#installing-act)
    - [Running Actions](#running-actions)
  - [Contributing](#contributing)
  - [License](#license)
  - [Acknowledgments](#acknowledgments)

## Setup

1. Clone this repository and navigate to the project directory:
   ```
   git clone https://github.com/yourusername/TalkTurbo.git
   cd TalkTurbo
   ```

2. Set up a Discord App+Bot in the [Discord Developer Portal](https://discord.com/developers/docs/intro) and acquire the bot's key. The [Discord.py docs](https://discordpy.readthedocs.io/en/stable/discord.html) have a good writeup on this.

3. Acquire an [OpenAI API key](https://platform.openai.com/account/api-keys).

4. Store environment variables:
   - Create a `.env` file in the `TalkTurbo` directory and add the following:
     ```
     DISCORD_SECRET_KEY=<discord_secret_key>
     OPENAI_SECRET_KEY=<openai_secret_key>
     ```
   - Alternatively, export your keys as environment variables:
     ```
     export DISCORD_SECRET_KEY=<discord_secret_key>
     export OPENAI_SECRET_KEY=<openai_secret_key>
     ```

5. Install dependencies:
   ```
   make install-dev
   ```

## Usage

Run the bot:
- Windows: `python ./src/TurboTalk/turbo.py`
- Linux / macOS: `python3 ./src/TurboTalk/turbo.py`

## Run with Docker

The Docker image is not currently distributed on Docker Hub, but it's easy to build locally:

1. Build the container:
   ```
   make docker-build
   ```

2. Run the container:
   ```
   docker run -d --env-file .env turbo:dev_latest
   ```

## Command Line Arguments

- `-h`, `--help`: Show the help message and exit
- `--sync-app-commands`: Sync new or updated app commands with Discord globally
- `--no-user-identifier`: Do not send a user's unique hash to OpenAI with each request
- `--disable-image-storage`: Do not store DALL-E images locally (image prompts and hashes may still be logged)
- `--pre-load-context <path>`: Load pre-defined context from a YAML file (default: `pre-load.yaml`)

## Slash Commands

- `/generate_image_dalle_3`: Generate a DALL-E-3 image from a prompt
- `/estop`: Shut down the bot (use at your discretion for spam, abuse, or other problems)
- `/list_models`: List available models
- `/list_current_model`: Show the model TalkTurbo is currently using
- `/set_model`: Set the model that TalkTurbo will use

## Context Tracking

TalkTurbo tracks conversation context to maintain topic relevance. Key points:

- Max context length: 1024 tokens (including system prompt)
- Newest messages are kept, oldest are removed when limit is reached
- Messages older than 24 hours are dropped
- System prompt is never removed from context
- Context limit can be increased up to 4096 tokens for `gpt-3.5-turbo` (note: this will increase API usage and costs)

## Moderation

All system prompts and messages sent to TalkTurbo are routed through the [OpenAI Moderation Endpoint](https://platform.openai.com/docs/guides/moderation). Moderation occurs regardless of the current chat model. Messages track their own moderation data, which can be checked with `message.flagged()`.

## Pre-load Data

Pre-load data can be used to inject custom system prompts and conversational context. It's tracked separately from standard context but included in context size calculations.

Example `pre-load.yaml`:

```yaml
system_prompt: |
    "You are an orange cat named Jones"
    "You are cheerful and like to meow"

context:
    - user: "Hey Jones!"
      assistant: "Meow, hey there! How can I help you?"
    - user: "Hey Jones, where do you like to hang out?"
      assistant: "My favorite spot is the pilot's seat. It has the best view! Meow!"
```

Use the `--pre-load-context <path>` argument to specify a pre-load file. If no path is provided, `pre-load.yaml` in the project root will be used.

## Development

To set up the development environment:

1. Install development dependencies:
   ```
   make install-dev
   ```

2. Set up pre-commit hooks:
   ```
   make setup
   ```

3. Run linters and formatters:
   ```
   make lint
   make format
   ```

4. Run tests:
   ```
   make test
   ```

5. Run pre-commit checks:
   ```
   make pre-commit
   ```

For more development commands, check the Makefile in the project root.

## Running GitHub Actions Locally

You can use Act to run GitHub Actions locally. This is useful for testing your workflows before pushing changes to the repository.

### Installing Act

To install Act, please follow the instructions on the [Act GitHub repository](https://github.com/nektos/act).

### Running Actions

Once Act is installed, you can use the following commands to run the pre-commit job locally:

For x86 architecture:
```
make act-x86
```

For ARM architecture:
```
make act-arm
```

These commands will run the pre-commit job defined in your GitHub Actions workflow file using your local environment.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

Please ensure your code adheres to the project's coding standards and passes all tests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the OpenAI team for their powerful language models and moderation API
- Thanks to the Discord.py team for their excellent library
- Shoutout to all members of the Sweat Hotel Discord server who have put TalkTurbo through its paces since day one!

---

For any questions, issues, or suggestions, please open an issue on the GitHub repository.
