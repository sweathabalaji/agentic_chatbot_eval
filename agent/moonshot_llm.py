"""
Moonshot AI LLM utility for the Mutual Funds Agent
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# We set OPENAI_API_BASE so LangChain/OpenAI client will call Groq endpoint
MOONSHOT_BASE = os.getenv("MOONSHOT_BASE_URL") or os.getenv("MOONSHOT_BASE_URL".upper()) or os.getenv("MOONSHOT_BASE_URL")
if MOONSHOT_BASE:
    os.environ["OPENAI_API_BASE"] = MOONSHOT_BASE  # LangChain/OpenAI will use this

# set API key for OpenAI client
MOONSHOT_KEY = os.getenv("MOONSHOT_API_KEY")
if MOONSHOT_KEY:
    os.environ["OPENAI_API_KEY"] = MOONSHOT_KEY

from langchain_openai import ChatOpenAI

def get_chat_llm(model_name: Optional[str] = None, temperature: float = 0.0) -> ChatOpenAI:
    """
    Returns a ChatOpenAI model configured to use your Groq (Moonshot) endpoint.
    
    Args:
        model_name: Model name to use (defaults to MOONSHOT_MODEL from env)
        temperature: Temperature setting for the model
        
    Returns:
        Configured ChatOpenAI instance
    """
    model = model_name or os.getenv("MOONSHOT_MODEL") or "moonshotai/kimi-k2-instruct"
    base_url = os.getenv("MOONSHOT_BASE_URL") or "https://api.groq.com/openai/v1"
    api_key = os.getenv("MOONSHOT_API_KEY")
    
    if not api_key:
        raise ValueError("MOONSHOT_API_KEY not found in environment variables")
    
    try:
        llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=1500,
            base_url=base_url,
            api_key=api_key
        )
        logging.info(f"Moonshot LLM initialized successfully with model: {model}")
        return llm
    except Exception as e:
        logging.exception("Failed to initialize ChatOpenAI: %s", e)
        raise
