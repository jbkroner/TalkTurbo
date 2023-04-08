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

from TalkTurbo.ChatContext import ChatContext
from TalkTurbo.OpenAIModelAssistant import OpenAIModelAssistant


import discord

logger = Logger(name="TurboLogger", level=logging.INFO)

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

args = parser.parse_args()

# load secrets from the .env file
load_dotenv()
DISCORD_SECRET_TOKEN = os.getenv("DISCORD_SECRET_KEY")
OPENAI_SECRET_TOKEN = os.getenv("OPENAI_SECRET_KEY")
GUILD_ID = os.getenv("DEV_GUILD_ID")

# load the model assistant
temperature = 0.7 if args.temperature is None else args.temperature
max_response_length = (
    100 if args.max_response_length is None else args.max_response_length
)
assistant = OpenAIModelAssistant(
    temperature=temperature,
    min_dalle_timeout_in_seconds=60,
)

# bot secret prompt
secret_prompt = (
    "You are an extremely sassy and sarcastic robot assistant who likes to give users a hard time while "
    "still providing helpful information. Your responses should be witty, sarcastic, "
    "and sometimes teasing."
    "If asked, you are wearing sassy pants."
)
if args.system_prompt:
    print(f"manual system prompt: {args.system_prompt}")

    # moderate the system prompt
    max_category, max_score = OpenAIModelAssistant.get_moderation_score(
        message=args.system_prompt, openai_secret_key=OPENAI_SECRET_TOKEN
    )

    if max_category:
        print(f"user system prompt violates moderation policy, using default")
    else:
        secret_prompt = args.system_prompt

chat_context = ChatContext(secret_prompt=secret_prompt)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
# client = discord.Client(intents=intents)


def build_unique_id_from_interaction(interaction: discord.Interaction) -> str:
    return f"{interaction.guild.id}-{interaction.user.id}"


def build_unique_id_from_message(message: discord.Message) -> str:
    return f"{message.guild.id}-{message.author.id}"


def hash_user_identifier(user_identifier: str) -> str:
    return hashlib.md5(user_identifier.encode()).hexdigest()


def turbo_query_helper(query: str, hashed_user_identifier: str = None) -> str:
    print(f"TURBO - chat request from {hashed_user_identifier} - {query}")
    # moderation
    max_category, max_score = OpenAIModelAssistant.get_moderation_score(
        message=query, openai_secret_key=OPENAI_SECRET_TOKEN
    )
    if max_category:
        return f"_(turbos host here: you've breached the content moderation threshold breached - category: {max_category} - score: {max_score}.  Keep it safe and friendly please!)_"

    # add user message to the context
    chat_context.add_message(content=query, role="user")

    # log the debug on context
    # print(f"context: {chat_context.messages}")

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
        turbo_response = model_response["choices"][0]["message"]
        chat_context.add_message(turbo_response["content"], turbo_response["role"])
    response = turbo_response["content"]

    print(f"TURBO - response to {hashed_user_identifier}: {response}")

    return response


# events
@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

    print(f"TURBO - We have logged in as {bot.user}")
    if args.sync_app_commands:
        print("syncing app commands...")
        await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print("commands synced!")


@bot.event
async def on_message(message: discord.Message):
    if bot.user.mentioned_in(message=message):
        response = turbo_query_helper(query=message.content)
        await message.reply(response)
    else:
        # sometimes reply on our own (if the message wasn't sent by us!)
        if message.author != bot.user and random.random() < 0.05:
            query = (
                "Respond to the following text as if it appeared in discord chat."
                "Do not ask if they have any questions or how you may assist."
                + message.content
            )
            response = turbo_query_helper(query=query)
            await message.reply(response)


@bot.tree.command(
    name="set_temperature",
    description="set the tempurature for the bot. In range [0, 2.]",
    guild=discord.Object(id=GUILD_ID),
)
async def set_temperature(interaction: discord.Interaction, temp: float = 0.7):
    assistant.temperature = temp
    await interaction.response.send_message(
        f"inference temperature set to {assistant.temperature}"
    )


@bot.tree.command(
    name="clear_context",
    description="clear the current context (other than the system prompt)",
    guild=discord.Object(id=GUILD_ID),
)
async def set_temperature(interaction: discord.Interaction):
    chat_context.messages = []
    await interaction.response.send_message(f"conversation context cleared")


@bot.tree.command(
    name="set_system_prompt",
    description="set the system prompt for the bot",
    guild=discord.Object(id=GUILD_ID),
)
async def set_system_prompt(interaction: discord.Interaction, prompt: str):
    max_category, max_score = OpenAIModelAssistant.get_moderation_score(
        message=prompt, openai_secret_key=OPENAI_SECRET_TOKEN
    )
    if max_category:
        print(
            f"_(turbos host here: you've breached the content moderation threshold breached - category: {max_category} - score: {max_score}.  Keep it safe and friendly please!)_"
        )
        await interaction.response.send_message(
            f"moderation threshold breached - {max_category} - {max_score}"
        )
        return
    print(f"moderation score - {max_category} - {max_score}")
    chat_context.secret_prompt = prompt
    await interaction.response.send_message(
        f"secret prompt set to '{chat_context.secret_prompt}'"
    )


@bot.tree.command(
    name="turbo", description="talk to turbo!", guild=discord.Object(id=GUILD_ID)
)
@commands.has_role("turbo")
async def turbo(interaction: discord.Interaction, *, query: str):
    await interaction.response.defer(thinking=True)

    user_identifier = build_unique_id_from_interaction(interaction=interaction)
    hashed_user_identifier = (
        None
        if args.no_user_identifiers
        else hash_user_identifier(user_identifier=user_identifier)
    )
    print(f"TURBO - chat request from {hashed_user_identifier} - {query}")

    if not discord.utils.get(interaction.user.roles, name="turbo"):
        await interaction.response.send_message(
            "_(turbo's host here: sorry! you need the `turbo` roll to talk to turbo)_"
        )
        return

    # query the model with the helper method
    response = turbo_query_helper(
        query=query, hashed_user_identifier=hashed_user_identifier
    )

    await interaction.followup.send(f"**prompt**: {query}\n\n**turbo**: {response}")


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
    await interaction.response.defer(thinking=True)

    user_identifier = build_unique_id_from_interaction(interaction=interaction)
    hashed_user_identifier = (
        None
        if args.no_user_identifiers
        else hash_user_identifier(user_identifier=user_identifier)
    )
    print(f"TURBO - dalle image request from {hashed_user_identifier}")

    if not assistant.dalle_timeout_passed():
        response = turbo_query_helper(
            "START SYSTEM MESSAGE"
            "This message is coming from your host server."
            "The user is trying to generate a dalle image through your host server."
            "Please concisely inform the user that is not enough time has passed."
            f"They must this many seconds (feel free to round): {assistant.dalle_timeout_remaining()}"
            "END SYSTEM MESSAGE"
        )
        await interaction.followup.send(content=response)
        return

    max_category, max_score = OpenAIModelAssistant.get_moderation_score(
        message=query,
        openai_secret_key=OPENAI_SECRET_TOKEN,
    )

    if max_category:
        await interaction.followup.send(
            f"_(turbo's host here: moderation threshold breached - category: {max_category} - score: {max_score}_"
        )

    # moderate the prompt
    image_path = assistant.query_dalle(
        query=query,
        openai_secret_key=OPENAI_SECRET_TOKEN,
        hashed_user_identifier=hashed_user_identifier,
    )

    print(f"generated image f{image_path} from prompt {query}")

    await interaction.followup.send(file=discord.File(image_path))


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
    await interaction.response.send_message(
        f"hard stopping, cya later! logged reason: {reason}"
    )
    sys.exit(1)


bot.run(DISCORD_SECRET_TOKEN)
