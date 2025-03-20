# import chromadb
# from chromadb.config import Settings
# import os
#
# chroma_client = chromadb.Client(
#     Settings(
#         chroma_db_impl="duckdb+parquet",
#         persist_directory=os.getenv("CHROMA_DB_PATH", "/data/chroma")
#     )
# )
import time

import chromadb
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from loguru import logger

# Initialize ChromaDB HTTP client
client = chromadb.HttpClient(host="localhost", port=8001)

# Define the embedding function
embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def get_retriever(chat_id: str):
    """Create a retriever filtered by chat_id."""
    try:
        _time = time.time()
        # Wrap the Chroma client in LangChain's Chroma vector store
        vector_store = Chroma(
            client=client,
            collection_name="documents",
            embedding_function=embedding
        )

        # Create a retriever with a filter on chat_id
        retriever = vector_store.as_retriever(
            search_kwargs={"filter": {"chat_id": chat_id}}
        )

        logger.debug(f"Retriever created for chat_id: {chat_id} in {time.time() - _time} seconds")
        return retriever

    except Exception as e:
        logger.error(f"Failed to create retriever: {e}")
        raise
# def get_retriever(chat_id: str):
#     """Create a retriever filtered by chat_id."""
#     collection = client.get_or_create_collection("documents")
#     retriever = collection.as_retriever(search_kwargs={"filter": {"chat_id": chat_id}})
#     return retriever