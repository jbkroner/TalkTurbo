from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_CLIENT = OpenAI(
    api_key=os.environ.get("OPENAI_SECRET_KEY")
)