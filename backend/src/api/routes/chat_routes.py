import time

from fastapi import APIRouter, Depends, HTTPException
from ...api.schemas import ChatRequest, ChatResponse
from ...data.chroma_manager import add_to_chroma, get_retriever
from ...data.redis_manager import redis_client
from ...data.session_manager import SessionManager
from ...core.model_router import model_router
from ...processing.chain_factory import create_chain
from loguru import logger

from ...utils.profiling_tools import measure_time

router = APIRouter()
session_manager = SessionManager(redis_client=redis_client)
# model_router = ModelRouter()

@router.post("/chat/text", response_model=ChatResponse)
async def handle_text_chat(request: ChatRequest):
    """Handle text chat requests."""
    try:
        logger.info(f"Received message for session {request.session_id}: {request.message}")

        # Retrieve session from Redis
        session = session_manager.get_session(request.session_id)
        if not session:
            raise ValueError("Session not found")
        logger.debug(f"The ongoing sessions content: {session}")

        # chat_history = [(entry["user"], entry["ai"]) for entry in session["history"]]
        retriever = get_retriever(request.session_id)  # Assuming this function exists
        logger.debug(f"Retrieved object received: {retriever}")

        # Select LLM for text
        llm = model_router.get_model("text")

        # Create conversational chain
        chain = create_chain(llm, request.session_id, retriever)

        logger.debug(f"Chain created for session id {request.session_id}")
        logger.debug(f"Relevant documents: {retriever.invoke(request.message)}")

        # Invoke chain with message and history
        _time = time.time()
        response = chain.invoke({
            "question": request.message,
            "chat_history": []
        })


        answer = response.get('answer', "Error in Giving a Response !")

        logger.debug(f"Invoke chain response received in time {time.time() - _time} | Answer: {answer}")
        add_to_chroma(
            documents=[f"User Query: {request.message} \nAI Response: {answer}"],
            metadatas=[{"chat_id": request.session_id, "timestamp": time.time()}]
        )

        # Update chat history in Redis
        session_manager.add_chat_history(request.session_id, request.message, answer)

        return ChatResponse(response=answer)
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))