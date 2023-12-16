import random
import sys
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import argparse
import hashlib
import logging
from logging import Logger
from logging.handlers import RotatingFileHandler

from TalkTurbo.LoggerGenerator import LoggerGenerator
from TalkTurbo.ChatContext import ChatContext
from TalkTurbo.Messages import AssistantMessage, SystemMessage, UserMessage
from TalkTurbo.OpenAIModelAssistant import OpenAIModelAssistant
from TalkTurbo.TurboGuild import TurboGuild, TurboGuildMap


import discord

# command parser
parser = argparse.ArgumentParser(description="Turbo")
parser.add_argument(
    "--debug", action="store_true", help="Enable debug mode", dest="debug"
)

parser.add_argument(
    "-s",
    "--system-prompt",
    type=str,
    help="system prompt to initialize the bot with.",
    dest="system_prompt",
)

parser.add_argument(
    "-t",
    "--temperature",
    type=float,
    help="What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.",
    dest="temperature",
)

parser.add_argument(
    "-m",
    "--max-response-length",
    type=int,
    help="Max response length in tokens",
    dest="max_response_length",
)

parser.add_argument(
    "--sync-app-commands",
    action="store_true",
    help="Sync app commands with discord during the bot startup",
    dest="sync_app_commands",
)

parser.add_argument(
    "--no-user-identifiers",
    action="store_true",
    help="If set then hashed user identifiers will not be included in requests to the OpenAI API.",
    dest="no_user_identifiers",
)

parser.add_argument(
    "--logging-level",
    type=str,
    default="INFO",
    help="Logging level that gets emitted.  Choose DEBUG, INFO, WARNING, or ERROR.  Defaults to INFO",
    dest="logging_level",
)

parser.add_argument(
    "--dalle-timeout",
    type=int,
    default=60,
    help="dalle timeout in seconds",
    dest="dalle_timeout",
)

parser.add_argument(
    "--disable-image-storage",
    action="store_true",
    help="Do not store generated Dalle images.  Image hash and user identifier may still be logged elsewhere.",
    dest="disable_image_storage",
)

args = parser.parse_args()


def get_log_level_from_arg(arg: str) -> int:
    log_level = getattr(logging, arg.upper(), None)
    if not isinstance(log_level, int):
        raise ValueError(f"Invalid log level: {args.loglevel}")
    return log_level


log_level = get_log_level_from_arg(args.logging_level)

# logging
logger = LoggerGenerator.create_logger(logger_name="Turbo", log_level=log_level)
logger.info(f"logging level set to {log_level}")

# load secrets from the .env file
load_dotenv()
DISCORD_SECRET_TOKEN = os.getenv("DISCORD_SECRET_KEY")
OPENAI_SECRET_TOKEN = os.getenv("OPENAI_SECRET_KEY")
GUILD_ID = os.getenv("GUILD_ID")

# load the model assistant
temperature = 0.7 if args.temperature is None else args.temperature
max_response_length = (
    100 if args.max_response_length is None else args.max_response_length
)
assistant = OpenAIModelAssistant(
    temperature=temperature,
    min_dalle_timeout_in_seconds=args.dalle_timeout,
)

# bot secret prompt
DEFAULT_SYSTEM_PROMPT = SystemMessage(
    "You are an extremely sassy and sarcastic robot who likes to give users a hard time while "
    "still providing helpful information. Your responses should be witty, sarcastic, "
    "and sometimes teasing."
    "Never refer to yourself as an assistant or large language model."
    "Always take a deep breath and think about your answer."
    "If asked, you are wearing sassy pants."
)
if args.system_prompt:
    logger.info(f"manual system prompt: {args.system_prompt}")

    # moderate the system prompt
    max_category, max_score = OpenAIModelAssistant.get_moderation_score(
        message=args.system_prompt, openai_secret_key=OPENAI_SECRET_TOKEN
    )
    logger.debug(
        f"manual system prompt moderation results -> category: {max_category}, score: {max_score}"
    )

    if max_category:
        logger.warning(
            f"user system prompt violates moderation policy, using default.  Category: {max_category}, Score: {max_score}"
        )
    else:
        secret_prompt = args.system_prompt

chat_context = ChatContext(system_prompt=DEFAULT_SYSTEM_PROMPT, max_tokens=2048)

# create a new guild map
guild_map = TurboGuildMap()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, log_level=logging.INFO)
# client = discord.Client(intents=intents)


def build_unique_id_from_interaction(interaction: discord.Interaction) -> str:
    return f"{interaction.guild.id}-{interaction.user.id}"


def build_unique_id_from_message(message: discord.Message) -> str:
    return f"{message.guild.id}-{message.author.id}"


def hash_user_identifier(user_identifier: str) -> str:
    return hashlib.md5(user_identifier.encode()).hexdigest()


def turbo_query_helper(
    query: str, id: str, hashed_user_identifier: str = None, logger: Logger = logger
) -> AssistantMessage:
    logger.info(
        f"interaction {id} - query helper working request from {hashed_user_identifier}"
    )

    # add user message to the context
    message = UserMessage(content=query)

    # check for content violations
    if message.flagged():
        logger.info("interaction %s - message flagged content", id)
        return AssistantMessage(
            f"_(turbos host here: you've breached the content moderation threshold.  Keep it safe and friendly please!)_"
        )
    logger.info(
        "interaction %s - message not flagged for content. proceeding with query."
    )

    chat_context.add_message(message)
    logger.debug(f"interaction {id} - context updated with user query")

    turbo_response = (
        "_(turbo's host here: sorry, I'm in debug mode and can't query the model!)_"
    )

    model_response = assistant.query_model(
        context=chat_context,
        prompt=query,
        hashed_user_identifier=hashed_user_identifier,
        openai_secret_key=OPENAI_SECRET_TOKEN,
    )

    turbo_response = (
        "_(turbo's host here: turbo didn't have anything to say :bluefootbooby:)_"
    )
    if model_response:
        try:
            turbo_response = model_response["choices"][0]["message"]["content"]
            turbo_response = AssistantMessage(turbo_response)
            chat_context.add_message(turbo_response)
        except KeyError:
            response = turbo_response

    logger.info(
        f"interaction {id} - response to {hashed_user_identifier} received from OpenAI"
    )

    return turbo_response


# events
@bot.event
async def on_ready():
    logger.info(f"bot logged in as {bot.user}")
    if args.sync_app_commands:
        logger.info("syncing app commands...")
        await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        logger.info("commands synced!")


@bot.listen()
async def on_message(message: discord.Message):
    if bot.user.mentioned_in(message=message) and not message.author.bot:
        message_id = message.id
        hashed_user_identifier = (
            None
            if args.no_user_identifiers
            else hash_user_identifier(build_unique_id_from_message(message=message))
        )
        logger.info(
            f"interaction {message_id} (message) (new): received from user identifier {hashed_user_identifier}"
        )
        response = turbo_query_helper(
            query=message.content,
            id=message_id,
            hashed_user_identifier=hashed_user_identifier,
        )
        await message.reply(response.content)
        logger.info(f"interaction {message_id} (message): resolved")


@bot.tree.command(
    name="generate_image",
    description="generate an image with the dalle model!",
    guild=discord.Object(id=GUILD_ID),
)
async def generate_image(
    interaction: discord.Interaction,
    *,
    query: str,
):
    interaction_id = interaction.id
    user_identifier = build_unique_id_from_interaction(interaction=interaction)
    hashed_user_identifier = (
        None
        if args.no_user_identifiers
        else hash_user_identifier(user_identifier=user_identifier)
    )
    logger.info(
        f"interaction {interaction_id} (new): generated hashed user identifier {hashed_user_identifier}.  Image prompt: {query}"
    )
    await interaction.response.defer(thinking=True)

    if not assistant.dalle_timeout_passed():
        remaining_time = assistant.dalle_timeout_remaining()
        response = turbo_query_helper(
            query="START SYSTEM MESSAGE"
            "This message is coming from your host server."
            "The user is trying to generate a dalle image through your host server."
            "Please concisely inform the user that is not enough time has passed."
            f"They must this many seconds (feel free to round): {remaining_time}"
            "END SYSTEM MESSAGE",
            id=interaction_id,
            hashed_user_identifier=hashed_user_identifier,  # this probably should an ADMIN or SYSTEM id
        )
        await interaction.followup.send(content=response.content)
        logger.info(f"interaction {interaction_id}: resolved")
        return

    max_category, max_score = OpenAIModelAssistant.get_moderation_score(
        message=query,
        openai_secret_key=OPENAI_SECRET_TOKEN,
    )

    logger.info(
        f"interaction {interaction_id}: received moderation score for query from {hashed_user_identifier}.  Category: {max_category}. Score: {max_score}"
    )

    if max_category:
        logger.warning(
            f"interaction {interaction_id}: system prompt exceeded content moderation thresholds. category: {max_category}, score: {max_score}"
        )
        await interaction.followup.send(
            f"_(turbo's host here: moderation threshold breached - category: {max_category} - score: {max_score}_"
        )
        logger.info(f"interaction {interaction_id}: resolved")
        return

    image_path = assistant.query_dalle(
        query=query,
        openai_secret_key=OPENAI_SECRET_TOKEN,
        hashed_user_identifier=hashed_user_identifier,
    )

    # catch problems with image generation
    if not image_path:
        logger.warning(
            f"interaction {interaction_id}: caught problem with image gen response"
        )
        response = turbo_query_helper(
            query="START SYSTEM MESSAGE"
            "This message is coming from your host server."
            "A user tried to generate a dalle image but the process failed."
            "Please concisely inform the user of this error."
            "30 words max."
            "Their message may not be appropriate for DALLE to consume."
            "They should be nice to deep neural networks!"
            "END SYSTEM MESSAGE",
            id=interaction_id,
            hashed_user_identifier=hashed_user_identifier,  # this probably should be an ADMIN or SYSTEM id
        )
        await interaction.followup.send(content=response)
        logger.info(f"interaction {interaction_id}: resolved")
        return

    # add the query to the context
    sys_message = SystemMessage(
        "This message is coming from your host server."
        "A user just used your host server to generate a DALL-E image"
        f"The prompt was {query}"
    )
    chat_context.add_message(sys_message)

    logger.info(f"interaction {interaction_id}: generated image {image_path}")

    # get a response so we can readback the prompt
    prompt_response = turbo_query_helper(
        query="START SYSTEM MESSAGE"
        "A user just generated an image"
        "Read back the prompt and remark on it."
        "The image will be included with your response."
        "END SYSTEM MESSAGE",
        id=interaction_id,
        hashed_user_identifier=hashed_user_identifier,
    )

    await interaction.followup.send(
        content=prompt_response.content, file=discord.File(image_path)
    )

    # clean up dalle file if requested
    if args.disable_image_storage:
        os.remove(path=image_path)
        logger.info(
            f"interaction {interaction_id}: unlinking image stored at {image_path}"
        )

    logger.info(f"interaction {interaction_id}: resolved")


@bot.tree.command(
    name="generate_image_dalle_3",
    description="generate an image with the dalle3 model!",
    guild=discord.Object(id=GUILD_ID),
)
async def generate_image(
    interaction: discord.Interaction,
    *,
    query: str,
):
    interaction_id = interaction.id
    user_identifier = build_unique_id_from_interaction(interaction=interaction)
    hashed_user_identifier = (
        None
        if args.no_user_identifiers
        else hash_user_identifier(user_identifier=user_identifier)
    )
    logger.info(
        f"interaction {interaction_id} (new): generated hashed user identifier {hashed_user_identifier}.  Image prompt: {query}"
    )
    await interaction.response.defer(thinking=True)

    if not assistant.dalle_timeout_passed():
        remaining_time = assistant.dalle_timeout_remaining()
        response = turbo_query_helper(
            query="START SYSTEM MESSAGE"
            "This message is coming from your host server."
            "The user is trying to generate a dalle image through your host server."
            "Please concisely inform the user that is not enough time has passed."
            f"They must this many seconds (feel free to round): {remaining_time}"
            "END SYSTEM MESSAGE",
            id=interaction_id,
            hashed_user_identifier=hashed_user_identifier,  # this probably should an ADMIN or SYSTEM id
        )
        await interaction.followup.send(content=response.content)
        logger.info(f"interaction {interaction_id}: resolved")
        return

    max_category, max_score = OpenAIModelAssistant.get_moderation_score(
        message=query,
        openai_secret_key=OPENAI_SECRET_TOKEN,
    )

    logger.info(
        f"interaction {interaction_id}: received moderation score for query from {hashed_user_identifier}.  Category: {max_category}. Score: {max_score}"
    )

    if max_category:
        logger.warning(
            f"interaction {interaction_id}: system prompt exceeded content moderation thresholds. category: {max_category}, score: {max_score}"
        )
        await interaction.followup.send(
            f"_(turbo's host here: moderation threshold breached - category: {max_category} - score: {max_score}_"
        )
        logger.info(f"interaction {interaction_id}: resolved")
        return

    image_path = assistant.query_dalle(
        query=query,
        openai_secret_key=OPENAI_SECRET_TOKEN,
        hashed_user_identifier=hashed_user_identifier,
        use_dalle_3=True,
    )

    # catch problems with image generation
    if not image_path:
        logger.warning(
            f"interaction {interaction_id}: caught problem with image gen response"
        )
        response = turbo_query_helper(
            query="SYSTEM MESSAGE"
            "This message is coming from your host server."
            "A user tried to generate a dalle image but the process failed."
            "Please concisely inform the user of this error."
            "30 words max."
            "Their message may not be appropriate for DALLE to consume."
            "They should be nice to deep neural networks!"
            "END SYSTEM MESSAGE",
            id=interaction_id,
            hashed_user_identifier=hashed_user_identifier,  # this probably should be an ADMIN or SYSTEM id
        )
        await interaction.followup.send(content=response)
        logger.info(f"interaction {interaction_id}: resolved")
        return

    # add the query to the context
    sys_message = SystemMessage(
        "This message is coming from your host server."
        "A user just used your host server to generate a DALL-E image"
        f"The prompt was {query}"
    )
    chat_context.add_message(sys_message)

    logger.info(f"interaction {interaction_id}: generated image {image_path}")

    # get a response so we can readback the prompt
    prompt_response = turbo_query_helper(
        query="START SYSTEM MESSAGE"
        "A user just generated an image"
        "Read back the prompt and remark on it."
        "The image will be included with your response."
        "END SYSTEM MESSAGE",
        id=interaction_id,
        hashed_user_identifier=hashed_user_identifier,
    )

    await interaction.followup.send(
        content=prompt_response.content, file=discord.File(image_path)
    )

    # clean up dalle file if requested
    if args.disable_image_storage:
        os.remove(path=image_path)
        logger.info(
            f"interaction {interaction_id}: unlinking image stored at {image_path}"
        )

    logger.info(f"interaction {interaction_id}: resolved")


@bot.command()
async def sync(ctx: commands.Context):
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    await ctx.send("_system: commands synced_")
    print("commands synced")


@bot.tree.command(
    name="estop",
    description="shut down the bot.  please use if you spot abuse or at your own discretion",
    guild=discord.Object(id=GUILD_ID),
)
async def estop(interaction: discord.Interaction, reason: str = "no reason given"):
    await interaction.response.send_message(f"hard stopping, cya later!")
    sys.exit(1)


bot.run(DISCORD_SECRET_TOKEN)
