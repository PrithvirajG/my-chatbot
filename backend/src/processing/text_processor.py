from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from ...src.core.model_router import model_router
from ...src.core.config_loader import settings
from loguru import logger

class TextProcessor:
    def __init__(self):
        self.llm = model_router.get_model("text")
        self.prompt_template = self._create_prompt_template()
        self.qa_chain = self._create_qa_chain()

    def _create_prompt_template(self) -> PromptTemplate:
        return PromptTemplate(
            template=(
                "Context: {context}\n"
                "Chat History: {history}\n"
                "Question: {question}\n"
                "Answer:"
            ),
            input_variables=["context", "history", "question"]
        )

    def _create_qa_chain(self) -> ConversationalRetrievalChain:
        return ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            chain_type="stuff",
            combine_docs_chain_kwargs={"prompt": self.prompt_template},
            return_source_documents=True
        )

    def generate_response(self, query: str, history: list) -> dict:
        """Generate response with context and history"""
        try:
            result = self.qa_chain({
                "question": query,
                "chat_history": history
            })
            
            return {
                "response": result["answer"],
                "sources": [doc.metadata for doc in result["source_documents"]]
            }
        except Exception as e:
            logger.error(f"Text processing failed: {str(e)}")
            raise RuntimeError("Text generation error")

text_processor = TextProcessor()