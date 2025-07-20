from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.config import OPENAI_API_KEY
from app.models.chat import ChatThread, ChatMessage, RoleEnum
from app.services.chat.chat_model_service import ChatModelService
from app.services.prompts.prompt_generator import PromptGenerator
from app.services.vector_db.qdrant_search_service import QdrantSearchService
from app.services.web.web_search_service import WebSearchService


class ChatService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.api_key = OPENAI_API_KEY
        self.web_search_service = WebSearchService()
        self.vector_db_service = QdrantSearchService()
        self.prompt_generator = PromptGenerator()
        self.llm_service = ChatModelService()

    # Finds or creates a thread by ID
    async def get_or_create_thread(self, thread_id: str) -> ChatThread:
        result = await self.db.execute(
            select(ChatThread).where(ChatThread.id == thread_id)
        )

        thread = result.scalars().first()

        if thread:
            return thread

        # Create new thread with default anonymous user_id for now
        # TODO: Replace with actual user_id when authentication is implemented
        thread = ChatThread(id=thread_id, user_id="anonymous")
        self.db.add(thread)
        await self.db.flush()
        return thread

    # Saves a chat message (user or assistant) to the DB
    async def save_message(self, thread: ChatThread, role: RoleEnum, content: str):
        message = ChatMessage(thread_id=thread.id, role=role, content=content)
        self.db.add(message)
        await self.db.flush()

    # Main handler: receives a user query, responds, and saves everything
    async def handle_message(self, thread_id: str, query: str) -> dict:
        thread = await self.get_or_create_thread(thread_id)
        await self.save_message(thread, RoleEnum.USER, query)

        prompt = ""

        # Search internal knowledge base
        chunks = self.vector_db_service.search_similarity(query, k=3)
        if not chunks:
            # search web
            pass
        else:
            context = "\n".join(chunks)
            prompt = self.prompt_generator.generate(
                "final_answer", context=context, question=query
            )

        # Send prompt to selected LLM
        llm_result = self.llm_service.invoke(prompt)

        # Save assistant reply
        await self.save_message(thread, RoleEnum.ASSISTANT, llm_result.content)

        return {
            "thread_id": thread.id,
            "question": query,
            "answer": llm_result.content,
        }





