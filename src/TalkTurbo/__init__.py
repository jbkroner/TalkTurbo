import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_CLIENT = OpenAI(api_key=os.environ.get("OPENAI_SECRET_KEY", None))
