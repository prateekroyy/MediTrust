# General RAG chatbot
import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


from genai.llm import get_llm
from genai.prompts import (
    GENERAL_SYSTEM_PROMPT,
    GENERAL_USER_PROMPT
)

# -------------------------
# Embeddings (Shared)
# -------------------------

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

# -------------------------
# Load & Index General Docs
# -------------------------

def load_and_index_general_docs(
    docs_path: str = "data/clinic_faq.txt",
    persist_path: str = "data/vectors/general"
):
    """
    Loads clinic / platform documents and builds a FAISS index.
    Call this once during app startup.
    """

    if not os.path.exists(docs_path):
        raise FileNotFoundError("General documents file not found")

    loader = TextLoader(docs_path, encoding="utf-8")
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=40
    )
    chunks = splitter.split_documents(documents)

    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)

    vectorstore.save_local(persist_path)
    return vectorstore

# -------------------------
# Load Existing Vector Store
# -------------------------

def load_general_vectorstore(persist_path: str = "data/vectors/general"):
    embeddings = get_embeddings()
    return FAISS.load_local(
        persist_path,
        embeddings,
        allow_dangerous_deserialization=True
    )

# -------------------------
# Ask General Question
# -------------------------

def ask_general_question(question: str, persist_path: str = "data/vectors/general") -> str:
    vectorstore = load_general_vectorstore(persist_path)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    docs = retriever.invoke(question)
    context = "\n\n".join([doc.page_content for doc in docs])

    llm = get_llm()

    prompt = GENERAL_SYSTEM_PROMPT + GENERAL_USER_PROMPT.format(
        context=context,
        question=question
    )

    response = llm.invoke(prompt)
    return response.content


if __name__ == "__main__":
    print("=== Testing General RAG ===")

    print("Building general document index...")
    load_and_index_general_docs()

    print("Asking test question...")
    answer = ask_general_question("What is MediTrust?")

    print("\n================ ANSWER ================")
    print(answer)
    print("=======================================\n")

