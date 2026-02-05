# Report RAG chatbot

import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from genai.llm import get_llm
from genai.prompts import (
    REPORT_SYSTEM_PROMPT,
    REPORT_USER_PROMPT,
    REPORT_SUMMARY_PROMPT
)

# Load environment variables
load_dotenv()

# -------------------------
# Embeddings (Local & Fast)
# -------------------------

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

# -------------------------
# Load & Index Medical Report
# -------------------------

def load_and_index_report(pdf_path: str, persist_path: str):
    """
    Loads a medical report PDF, chunks it, embeds it,
    and stores it in a FAISS vector index.
    """

    if not os.path.exists(pdf_path):
        raise FileNotFoundError("Report file not found")

    # Load PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)

    # Create vector store
    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)

    # Persist index
    vectorstore.save_local(persist_path)

    return vectorstore

# -------------------------
# Load Existing Vector Store
# -------------------------

def load_vectorstore(persist_path: str):
    embeddings = get_embeddings()
    return FAISS.load_local(
        persist_path,
        embeddings,
        allow_dangerous_deserialization=True
    )

# -------------------------
# Ask Question on Report
# -------------------------

def ask_report_question(question: str, persist_path: str) -> str:
    """
    Answers a patient question using RAG over the uploaded report.
    """

    vectorstore = load_vectorstore(persist_path)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    # Modern LangChain retrieval
    docs = retriever.invoke(question)
    context = "\n\n".join([doc.page_content for doc in docs])

    llm = get_llm()

    prompt = REPORT_SYSTEM_PROMPT + REPORT_USER_PROMPT.format(
        context=context,
        question=question
    )

    response = llm.invoke(prompt)
    return response.content

# -------------------------
# Generate Report Summary
# -------------------------

def summarize_report(persist_path: str) -> str:
    """
    Generates a simple, human-readable summary of the report.
    """

    vectorstore = load_vectorstore(persist_path)

    # Retrieve broad context for summary
    docs = vectorstore.similarity_search("", k=6)
    context = "\n\n".join([doc.page_content for doc in docs])

    llm = get_llm()

    prompt = REPORT_SUMMARY_PROMPT.format(context=context)
    response = llm.invoke(prompt)

    return response.content

# -------------------------
# Test Block
# -------------------------

if __name__ == "__main__":
    print("=== Testing Report RAG ===")

    report_path = "data/sample_report.pdf"
    index_path = "data/vectors/patient_test"

    print("Indexing medical report...")
    load_and_index_report(report_path, index_path)

    print("\nGenerating report summary...")
    summary = summarize_report(index_path)
    print("\n================ SUMMARY ================")
    print(summary)
    print("========================================")

    print("\nAsking question on report...")
    answer = ask_report_question(
        "Explain this report in simple language",
        index_path
    )
    print("\n================ ANSWER =================")
    print(answer)
    print("========================================")
