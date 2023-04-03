import sys
import nltk
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import argparse

from TalkTurbo.ChatContext import ChatContext
from TalkTurbo.OpenAIModelAssistant import OpenAIModelAssistant

from logging import Logger

logger = Logger("discordpy")
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

args = parser.parse_args()

# tokenizer
nltk.download("punkt")

# load secrets from the .env file
load_dotenv()
DISCORD_SECRET_TOKEN = os.getenv("DISCORD_SECRET_KEY")
OPENAI_SECRET_TOKEN = os.getenv("OPENAI_SECRET_KEY")

# load the model assistant
temperature = 0.7 if args.temperature is None else args.temperature
max_response_length = (
    100 if args.max_response_length is None else args.max_response_length
)
assistant = OpenAIModelAssistant(
    temperature=temperature, max_response_length=max_response_length
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

bot = commands.Bot(command_prefix="!", intents=intents, logging=logger)


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
        return

    # moderation
    max_category, max_score = OpenAIModelAssistant.get_moderation_score(
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

    # log the debug on context
    print(f"context: {chat_context.messages}")

    turbo_response = (
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
