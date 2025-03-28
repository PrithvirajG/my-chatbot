import time

from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate

from backend.src.data.chroma_manager import get_retriever
from loguru import logger

from backend.src.utils.profiling_tools import measure_time


def create_chain(llm, chat_id: str, retriever):
    """Create a conversational retrieval chain."""
    try:
        _time = time.time()
        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""
            You are a helpful assistant. Use the following context to answer the question in markdown format.
    
            Context: {context}
            
            Question: {question}
            
            Answer:"""
        )

        chain = ConversationalRetrievalChain.from_llm(
            llm=llm,  # Pass the LlamaCpp object directly
            retriever=retriever,
            combine_docs_chain_kwargs={"prompt": prompt_template}
        )
        logger.debug(f"Finished creating the chain in {time.time() - _time} seconds")
        return chain
    except Exception as e:
        logger.exception(f"Chain creation failed: {str(e)}")
        raise RuntimeError("Chain creation error")