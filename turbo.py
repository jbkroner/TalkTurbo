import sys
import nltk
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import requests
import argparse

from ChatContext import ChatContext
from OpenAIModelAssistant import OpenAIModelAssistant

from logging import Logger

logger = Logger("discordpy")
# command parser
parser = argparse.ArgumentParser(description="Turbo")
parser.add_argument(
    "--debug", action="store_true", help="Enable debug mode", dest="debug"
)
args = parser.parse_args()


# tokenizer
nltk.download("punkt")

# load secrets from the .env file
load_dotenv()
DISCORD_SECRET_TOKEN = os.getenv("DISCORD_SECRET_KEY")
OPENAI_SECRET_TOKEN = os.getenv("OPENAI_SECRET_KEY")

# bot secret prompt
secret_prompt = (
    "You are an extremely sassy and sarcastic robot assistant who likes to give users a hard time while "
    "still providing helpful information. Your responses should be witty, sarcastic, "
    "and sometimes teasing."
    "If asked, you are wearing sassy pants."
)

chat_context = ChatContext(secret_prompt=secret_prompt)
assistant = OpenAIModelAssistant(api_key=OPENAI_SECRET_TOKEN)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, logging=logger)


# helpers
def num_tokens(string: str) -> int:
    """num of tokens in a string"""
    return len(nltk.word_tokenize(string))


def tokens_in_context(context: list, secret_prompt: str) -> int:
    total_tokens = 0
    for message in context:
        total_tokens += num_tokens(message["content"])
    return total_tokens


def serialize_context(context: list, secret_prompt: str) -> str:
    serialized = secret_prompt
    for message in context:
        serialized += message["content"]
    return serialized.replace(" ", "")


# events
@bot.event
async def on_ready():
    if args.debug:
        await bot.change_presence(activity=discord.Game("Debug Mode"))
    print(f"We have logged in as {bot.user}")


@bot.command()
async def turbo(ctx, *, arg):
    if not discord.utils.get(ctx.author.roles, name="turbo"):
        await ctx.send(
            "_(turbo's host here: sorry! you need the `turbo` roll to talk to turbo)_"
        )

    # moderation
    max_category, max_score = assistant.get_moderation_score(
        message=arg, openai_secret_key=OPENAI_SECRET_TOKEN
    )
    if max_category:
        print(
            f"_(turbos host here: you've breached the content moderation threshold breached - category: {max_category} - score: {max_score}.  Keep it safe and friendly please!)_"
        )
        await ctx.send(f"moderation threshold breached - {max_category} - {max_score}")
        return
    print(f"moderation score - {max_category} - {max_score}")

    # add user message to the context
    chat_context.add_message(content=arg, role="user")

    response = (
        "_(turbo's host here: sorry, I'm in debug mode and can't query the model!)_"
    )

    if not args.debug:
        logger.info(f"attempting to send prompt {arg}")
        response = assistant.query_model(
            context=chat_context, prompt=arg, openai_secret_key=OPENAI_SECRET_TOKEN
        )

        turbo_response = (
            "_(turbo's host here: turbo didn't have anything to say :bluefootbooby:)_"
        )
        if response:
            turbo_response = response["choices"][0]["message"]
            chat_context.add_message(turbo_response["content"], turbo_response["role"])

        print(f"Response: {turbo_response}")

    await ctx.send(turbo_response["content"])


@bot.command()
async def estop(ctx, arg="no reason given"):
    await ctx.send(f"hard stopping, cya later! logged reason: {arg}")
    sys.exit(1)


bot.run(DISCORD_SECRET_TOKEN)
