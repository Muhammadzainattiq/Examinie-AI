from openai import OpenAI

from app.config import config
client = OpenAI(api_key = config.OPENAI_API_KEY)