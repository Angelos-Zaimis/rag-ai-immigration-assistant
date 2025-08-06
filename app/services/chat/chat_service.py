from sqlalchemy.ext.asyncio import AsyncSession

from app.config.config import OPENAI_API_KEY
from app.models.chat import ChatThread, ChatMessage, RoleEnum
from app.services.chat.chat_model_service import ChatModelService
from app.services.prompts.prompt_generator import PromptGenerator
from app.services.search.qdrant_search_service import QdrantSearchService
from app.services.search.web_search_service import WebSearchService
from app.services.threads.thread_service import ThreadService
from services.prompts.citation_service import CitationService
from services.prompts.query_parser import QueryParser


class ChatService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.openai_api_key = OPENAI_API_KEY
        self.web_search_service = WebSearchService()
        self.qdrant_search_service = QdrantSearchService()
        self.prompt_generator = PromptGenerator()
        self.chat_model_service = ChatModelService()
        self.thread_service = ThreadService(db)
        self.query_parser = QueryParser()
        self.citation_service = CitationService()

    def generate_prompt(self, context: str, query: str):
        return self.prompt_generator.generate(
            "final_answer", context=context, question=query
        )

    def retrieve_query_chunks(self, query: str):
        relevant_chunks = self.qdrant_search_service.search_similarity(query, k=10)
        if not relevant_chunks:
            # search web
            pass
        return relevant_chunks

    # Saves a chat message (user or assistant) to the DB
    async def save_message(self, thread: ChatThread, role: RoleEnum, content: str):
        message = ChatMessage(thread_id=thread.id, role=role, content=content)
        self.db.add(message)
        await self.db.flush()

    # Main handler: receives a user query, responds, and saves everything
    async def handle_message(self, thread_id: str, user_query: str) -> dict:
        thread = await self.thread_service.get_or_create_thread(thread_id)
        await self.save_message(thread, RoleEnum.USER, user_query)

        # Step 1: Optimize query for semantic retrieval
        optimized_user_query = await self.query_parser.optimize(user_query)

        # Step 2: Retrieve relevant knowledge chunks
        relevant_chunks = self.retrieve_query_chunks(optimized_user_query)

        # Step 3: Assign citation IDs and build citation map + context string
        context_str, citation_map = self.citation_service.generate_citation_map(relevant_chunks)

        # Step 4: Build prompt with retrieved context and original query
        prompt = self.generate_prompt(context_str, user_query)

        # Step 5: Get LLM response
        llm_response = await self.chat_model_service.invoke(prompt, "gpt-4o")

        # Step 6: Post-process the LLM response with citations
        final_answer, bibliography = self.citation_service.replace_markers(llm_response.content, citation_map)

        # Step 7: Save assistant reply
        await self.save_message(thread, RoleEnum.ASSISTANT, final_answer)

        # Step 8: Return full response
        return {
            "reply": final_answer,
            "bibliography": bibliography
        }