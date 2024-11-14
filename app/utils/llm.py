from langchain_openai import ChatOpenAI
from app.config import config

def get_chat_openai_client(
    model: str = "gpt-4o",
    temperature: float = 0.7,
    max_tokens: int = None,
    timeout: int = None,
    max_retries: int = 2,
    api_key: str = config.OPENAI_API_KEY
) -> ChatOpenAI:
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
        max_retries=max_retries,
        api_key=api_key
    )
