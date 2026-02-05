import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables from .env
load_dotenv()

def get_llm():
    """
    Returns a ChatGroq LLM instance.
    Uses Groq-hosted LLaMA models.
    """

    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")

    llm = ChatGroq(
        groq_api_key=groq_api_key,
        model_name="llama-3.3-70b-versatile",
        temperature=0.2,
        max_tokens=512
    )

    return llm

if __name__ == "__main__":
    print("Testing ChatGroq LLM...")
    llm = get_llm()
    response = llm.invoke("Say hello in one sentence.")
    print("LLM Response:")
    print(response.content)
