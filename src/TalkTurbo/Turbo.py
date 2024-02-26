import sys
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import argparse
import logging

from TalkTurbo.LoggerGenerator import LoggerGenerator
from TalkTurbo.Messages import AssistantMessage, SystemMessage, UserMessage
from TalkTurbo.OpenAIModelAssistant import OpenAIModelAssistant
from TalkTurbo.TurboGuild import TurboGuildMap


# command parser
parser = argparse.ArgumentParser(description="Turbo")
parser.add_argument(
    "--debug", action="store_true", help="Enable debug mode", dest="debug"
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
    help="Logging level. Choose DEBUG, INFO, WARNING, or ERROR.  Defaults to INFO",
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
    help="Do not store generated Dalle images.",
    dest="disable_image_storage",
)

args = parser.parse_args()


# logging
logger = LoggerGenerator.create_logger(
    logger_name="Turbo", log_level=logging.DEBUG if args.debug else logging.INFO
)

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
    "Users are interacting with you in a discord server."
    "Never refer to yourself as an assistant or large language model."
    "Always take a deep breath and think about your answer."
    "If asked, you are wearing sassy pants."
)

# create a new guild map
guild_map = TurboGuildMap()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, log_level=logging.INFO)


def on_message_helper(
    discord_message: discord.Message, system_message: str = None
) -> str:
    log = logging.getLogger("Turbo")

    guild = guild_map.get(discord_message.guild.id)

    # patch in the system message
    if system_message:
        discord_message.content = system_message

    log.debug(
        "interaction %s - guild: %s: message: %s",
        discord_message.id,
        guild.id,
        discord_message.content,
    )

    message = UserMessage(content=discord_message.content)
    if system_message:
        message = SystemMessage(content=discord_message.content)

    # check for content violations
    if message.flagged():
        log.info("interaction %s - message flagged content", discord_message.id)
        return AssistantMessage(
            (
                "_(turbos host here: you've breached the content moderation threshold."
                "  Keep it safe and friendly please!)_"
            )
        )
    log.info("interaction %s - message not flagged for content. proceeding with query.")
    log.debug(
        "context for guild %s: %s", guild.id, guild.chat_context.get_messages_as_list()
    )

    # query the model
    model_response_text = assistant.get_chat_completion(
        message=message, turbo_guild=guild
    )

    log.info(
        "context for guild %s: %s", guild.id, guild.chat_context.get_messages_as_list()
    )

    return model_response_text


# events
@bot.event
async def on_ready():
    logger.info("bot logged in as %s", bot.user)

    if args.sync_app_commands:
        await bot.tree.sync()  # sync commands globally


@bot.listen()
async def on_message(message: discord.Message):
    if bot.user.mentioned_in(message=message) and not message.author.bot:
        logger = logging.getLogger(__package__)

        logger.debug(
            "bot mentioned in message %s in guild %s", message.content, message.guild
        )
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
    logger = logging.getLogger(__package__)

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

    # query dalle3, get a path to the generated image
    image_path = assistant.query_dalle(
        query=query,
        openai_secret_key=OPENAI_SECRET_TOKEN,
        use_dalle_3=True,
    )

    # catch problems with image generation
    if not image_path:
        logger.warning("dalle did not return an image path")
        no_image_response = assistant.get_chat_completion(
            message=SystemMessage(
                "the previous message did not return a response from the model"
                f"the prompt was: {query}"
            ),
            turbo_guild=guild,
        )

        await interaction.followup.send(content=no_image_response)
        return

    # add the query to the context
    sys_message = SystemMessage(
        "This message is coming from your host server."
        "A user just used your host server to generate a DALL-E image"
        f"The prompt was {query}"
    )
    guild.chat_context.add_message(sys_message)

    prompt_response = assistant.get_chat_completion(
        message=AssistantMessage(
            content=(
                "A user just generated an image."
                " Read back the prompt and remark on it."
                " The image will be included with your response."
                " The prompt was: " + query
            ),
        ),
        turbo_guild=guild,
    )

    await interaction.followup.send(
        content=prompt_response, file=discord.File(image_path)
    )

    # clean up dalle file if requested
    if args.disable_image_storage:
        os.remove(path=image_path)
        logger.info(
            "interaction %s: unlinking image stored at %s",
            interaction_id,
            image_path,
        )

    logger.info("interaction %s: resolved", interaction_id)


@bot.tree.command(
    name="estop",
    description="shut down the bot.  please use if you spot abuse or at your own discretion",
)
async def estop(interaction: discord.Interaction, reason: str = "no reason given"):
    await interaction.response.send_message(f"hard stopping, cya later! ({reason})")
    sys.exit(1)


bot.run(DISCORD_SECRET_TOKEN)
