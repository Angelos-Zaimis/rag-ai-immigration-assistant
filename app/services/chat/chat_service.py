from sqlalchemy.ext.asyncio import AsyncSession

from app.config.config import OPENAI_API_KEY
from app.models.chat import ChatThread, ChatMessage, RoleEnum
from app.services.chat.chat_model_service import ChatModelService
from app.services.prompts.prompt_generator import PromptGenerator
from app.services.search.qdrant_search_service import QdrantSearchService
from app.services.search.web_search_service import WebSearchService
from app.services.threads.thread_service import ThreadService


class ChatService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.api_key = OPENAI_API_KEY
        self.web_search_service = WebSearchService()
        self.vector_db_service = QdrantSearchService()
        self.prompt_generator = PromptGenerator()
        self.llm_service = ChatModelService()
        self.thread_service = ThreadService(db)

    def generate_prompt(self, context: str, query: str):
        return self.prompt_generator.generate(
            "final_answer", context=context, question=query
        )

    def retrieve_query_chunks(self, query: str):
        chunks = self.vector_db_service.search_similarity(query, k=3)
        if not chunks:
            # search web
            pass
        return chunks

# Saves a chat message (user or assistant) to the DB
    async def save_message(self, thread: ChatThread, role: RoleEnum, content: str):
        message = ChatMessage(thread_id=thread.id, role=role, content=content)
        self.db.add(message)
        await self.db.flush()

    # Main handler: receives a user query, responds, and saves everything
    async def handle_message(self, thread_id: str, query: str) -> dict:

        thread = await self.thread_service.get_or_create_thread(thread_id)
        await self.save_message(thread, RoleEnum.USER, query)

        chunks = self.retrieve_query_chunks(query)
        context = "\n".join(chunks)

        prompt = self.generate_prompt(context, query)
        llm_result = self.llm_service.invoke(prompt)

        await self.save_message(thread, RoleEnum.ASSISTANT, llm_result.content)
        return {
            "thread_id": thread.id,
            "question": query,
            "answer": llm_result.content,
        }





