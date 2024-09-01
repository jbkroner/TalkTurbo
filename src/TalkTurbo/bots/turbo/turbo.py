"""Turbo application code / callbacks"""

import logging
import os
import sys
from pprint import pformat as pf

import discord
from discord.ext import commands
from dotenv import load_dotenv

from TalkTurbo.ApiAdapters.AnthropicAdapter import AnthropicAdapter
from TalkTurbo.ApiAdapters.GoogleAdapter import GoogleAdapter
from TalkTurbo.ApiAdapters.GroqAdapter import GroqAdapter
from TalkTurbo.ApiAdapters.OpenAIAdapter import OpenAIAdapter
from TalkTurbo.bots.turbo.args import parse_args
from TalkTurbo.CompletionAssistant import CompletionAssistant
from TalkTurbo.LoggerGenerator import LoggerGenerator
from TalkTurbo.Messages import AssistantMessage, SystemMessage, UserMessage
from TalkTurbo.OpenAIModelAssistant import OpenAIModelAssistant
from TalkTurbo.PreLoad import get_pre_load_data
from TalkTurbo.TurboGuild import TurboGuildMap

args = parse_args()

# setup the logger
logger = LoggerGenerator.create_logger(
    logger_name="Turbo", log_level=logging.DEBUG if args.debug else logging.INFO
)

# load secrets from the environment
load_dotenv()
DISCORD_SECRET_TOKEN = os.getenv("DISCORD_SECRET_KEY")
OPENAI_SECRET_TOKEN = os.getenv("OPENAI_SECRET_KEY")
ANT_SECRET_TOKEN = os.environ.get("ANTHROPIC_SECRET_KEY", None)
GOOGLE_SECRET_TOKEN = os.environ.get("GOOGLE_SECRET_KEY", None)
GROQ_SECRET_TOKEN = os.environ.get("GROQ_SECRET_KEY", None)
GUILD_ID = os.getenv("GUILD_ID")

# used for dalle generation
assistant = OpenAIModelAssistant()

# used for chat completions
CompletionAssistant.set_adapter(OpenAIAdapter(api_token=OPENAI_SECRET_TOKEN))

# grab the pre-load data
if args.pre_load_context:
    logger.info("pre-loading context")
    PRE_LOAD_DATA, PRE_LOAD_SYSTEM_PROMPT = get_pre_load_data(args.pre_load_context)


# bot secret prompt
DEFAULT_SYSTEM_PROMPT = SystemMessage(
    "You are an extremely sassy and sarcastic robot who likes to give users a hard time while "
    "still providing helpful information. Your responses should be witty, sarcastic, "
    "and sometimes teasing."
    "Users are interacting with you in a discord server."
    "Never refer to yourself as an assistant or large language model."
    "Always take a deep breath and think about your answer."
    "If asked, you are wearing sassy pants."
)

# create a new guild map
guild_map = TurboGuildMap()

# discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, log_level=logging.INFO)


def on_message_helper(discord_message: discord.Message, system_message: str = None) -> str:
    guild = guild_map.get(discord_message.guild.id)

    # patch in pre-load data if needed
    if args.pre_load_context and not len(guild.chat_context.pre_load_data):
        for message in PRE_LOAD_DATA:
            guild.chat_context.add_pre_load_data(message)

        if PRE_LOAD_SYSTEM_PROMPT:
            guild.chat_context.add_pre_load_system_prompt(PRE_LOAD_SYSTEM_PROMPT)

    # patch in the system message
    if system_message:
        discord_message.content = system_message

    logger.debug(
        "interaction %s - guild: %s: message: %s",
        discord_message.id,
        discord_message.guild.name,
        discord_message.content,
    )

    message = UserMessage(content=discord_message.content)
    if system_message:
        message = SystemMessage(content=discord_message.content)

    # check for content violations
    # if so: return an assistant message, do not update the guild context with the
    # flagged message
    if message.flagged():
        logger.info("interaction %s - message flagged for content", discord_message.id)
        max_cat, max_score = message.get_max_category()
        max_score_percent = f"{100 * (1 - round(max_score, 5))}%"
        return AssistantMessage(
            (
                "_(turbos host here: you've breached the content moderation threshold."
                f" Category: {max_cat}, Score: {max_score_percent}. yikes."
                "  keep it safe and friendly please!)_"
            )
        ).content

    logger.info(
        "guild %s :: interaction %s :: message not flagged for content. proceeding with query.",
        discord_message.guild.name,
        discord_message.id,
    )
    logger.debug(
        "context for guild %s: %s",
        guild.id,
        pf(guild.chat_context.get_messages_as_list()),
    )

    guild.chat_context.add_message(message)
    response = CompletionAssistant.get_chat_completion(context=guild.chat_context)

    return response.get_latest_message().content


@bot.event
async def on_ready():
    log = logging.getLogger("Turbo")
    log.info("bot logged in as %s", bot.user)

    if args.sync_app_commands:
        log.info("syncing app commands")
        await bot.tree.sync()  # sync commands globally


@bot.listen()
async def on_message(message: discord.Message):
    if bot.user.mentioned_in(message=message) and not message.author.bot:
        log = logging.getLogger("Turbo")
        log.debug("bot mentioned in message %s in guild %s", message.content, message.guild)
        response = on_message_helper(discord_message=message)
        await message.reply(response)


@bot.tree.command(
    name="generate_image_dalle_3",
    description="generate an image with the dalle3 model!",
)
async def generate_image(
    interaction: discord.Interaction,
    *,
    query: str,
):
    log = logging.getLogger("Turbo")

    interaction_id = interaction.id

    # set the bot to "thinking" while we process this
    await interaction.response.defer(thinking=True)

    # grab the guild
    guild = guild_map.get(interaction.guild.id)

    # moderate the prompt
    message = UserMessage(query)
    if message.flagged():
        logger.info("interaction %s: flagged message", interaction.id)
        interaction.followup.send(
            content=(
                "_(turbos host here: you've breached the content moderation threshold."
                "  Keep it safe and friendly please!)_"
            )
        )
        return

    log.info(
        "guild %s :: interaction %s :: image prompt not flagged for content. proceeding with query.",
        interaction.guild.name,
        interaction.id,
    )

    # query dalle3, get a path to the generated image
    image_path = assistant.query_dalle(
        query=query,
        openai_secret_key=OPENAI_SECRET_TOKEN,
        use_dalle_3=True,
    )

    # catch problems with image generation
    if not image_path:
        log.warning("dalle did not return an image path")
        no_image_response = assistant.get_chat_completion(
            message=UserMessage(
                "(SYSTEM) the previous message did not return a response from the model"
                f"the prompt was: {query}"
                "please include the prompt (or similar) in your reply."
            ),
            turbo_guild=guild,
        )

        await interaction.followup.send(content=no_image_response)
        return

    # add the query to the context
    sys_message = UserMessage(
        "(SYSTEM) A user just generated an image."
        " Read back the prompt and remark on it."
        " The image will be included with your response."
        " The prompt was: " + query
    )
    guild.chat_context.add_message(sys_message)

    prompt_response = (
        CompletionAssistant.get_chat_completion(context=guild.chat_context)
        .get_latest_message()
        .content
    )

    await interaction.followup.send(content=prompt_response, file=discord.File(image_path))

    # clean up dalle file if requested
    if args.disable_image_storage:
        os.remove(path=image_path)
        log.info(
            "interaction %s: unlinking image stored at %s",
            interaction_id,
            image_path,
        )

    log.info("interaction %s: resolved", interaction_id)


@bot.tree.command(
    name="list_available_models",
    description="list models the bot can query.  Chang with /switch_model.",
)
async def list_models(interaction: discord.Interaction):
    models = (
        OpenAIAdapter.AVAILABLE_MODELS
        + AnthropicAdapter.AVAILABLE_MODELS
        + GoogleAdapter.AVAILABLE_MODELS
        + GroqAdapter.AVAILABLE_MODELS
    )
    await interaction.response.send_message(f"available models: {models}")


@bot.tree.command(
    name="list_current_model",
    description="list models the bot can query.  Change with /switch_model.",
)
async def list_current_model(interaction: discord.Interaction):
    guild = guild_map.get(interaction.guild.id)
    if guild.api_adapter:
        model_name = guild.api_adapter.model_name
    else:
        model_name = CompletionAssistant.ADAPTER.model_name

    await interaction.response.send_message(f"current model: {model_name}")


@bot.tree.command(
    name="set_model",
    description="set the model to use for the bot.  Use /list_available_models to see options.",
)
async def set_model(interaction: discord.Interaction, model: str = "gpt-3.5-turbo"):
    turbo_guild = guild_map.get(interaction.guild.id)
    logger.info("guild %s: setting model to %s", interaction.guild.name, model)
    response = f"setting model to {model}"

    if model in OpenAIAdapter.AVAILABLE_MODELS:
        turbo_guild.api_adapter = OpenAIAdapter(api_token=OPENAI_SECRET_TOKEN, model_name=model)
    elif model in AnthropicAdapter.AVAILABLE_MODELS:
        turbo_guild.api_adapter = AnthropicAdapter(api_token=ANT_SECRET_TOKEN, model_name=model)
    elif model in GoogleAdapter.AVAILABLE_MODELS:
        turbo_guild.api_adapter = GoogleAdapter(api_token=GOOGLE_SECRET_TOKEN, model_name=model)
    elif model in GroqAdapter.AVAILABLE_MODELS:
        turbo_guild.api_adapter = GroqAdapter(api_token=GROQ_SECRET_TOKEN, model_name=model)
    else:
        logger.warning("model %s not found", model)
        response = f"model {model} not found.  use /list_available_models to see options."

    await interaction.response.send_message(response)


@bot.tree.command(
    name="estop",
    description="shut down the bot.  please use if you spot abuse or at your own discretion",
)
async def estop(interaction: discord.Interaction, reason: str = "no reason given"):
    await interaction.response.send_message(f"hard stopping, cya later! ({reason})")
    sys.exit(1)


def main():
    bot.run(DISCORD_SECRET_TOKEN)


if __name__ == "__main__":
    main()
