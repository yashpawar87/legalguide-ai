import os
from backend.config import settings
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

# Explicitly push LangSmith settings into os.environ so LangChain picks them up automatically
if hasattr(settings, "LANGCHAIN_TRACING_V2"):
    os.environ["LANGCHAIN_TRACING_V2"] = settings.LANGCHAIN_TRACING_V2
    os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGCHAIN_ENDPOINT
    os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT


# ---------------------------------------------------------
# Tiered LLM Configuration
# ---------------------------------------------------------

# Fast / Extraction Tier
# Used by parallel agents (Statute, Precedent, Risk, Citation)
# Uses OpenRouter to bypass Groq rate limits
FAST_MODEL = os.getenv("FAST_LLM_MODEL", "deepseek/deepseek-v4-flash")

# Heavy / Reasoning Tier
# Used by deep reasoning agents (Analysis, Synthesis)
# Uses Groq for blazing fast Llama 3.3 70B
HEAVY_MODEL = os.getenv("HEAVY_LLM_MODEL", "llama-3.3-70b-versatile")


def get_fast_llm():
    """
    Returns an OpenRouter client using the OpenAI compatible endpoint.
    Used for parallel extraction nodes.
    """
    return ChatOpenAI(
        model=FAST_MODEL,
        temperature=0,
        api_key=settings.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )

def get_heavy_llm():
    """
    Returns a Groq client.
    Used for sequential reasoning nodes.
    """
    return ChatGroq(
        model_name=HEAVY_MODEL,
        temperature=0,
        api_key=settings.GROQ_API_KEY
    )
