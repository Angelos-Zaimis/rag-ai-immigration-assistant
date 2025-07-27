from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI



class QueryParser:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0)
        self.prompt = PromptTemplate.from_template("""
            You are a helpful assistant that rewrites user queries for semantic search in a vector DB.
            Remove filler, focus on intent, and make the query concise and relevant.

            Original query: {query}
            Optimized query:
        """)
        self.chain = self.prompt | self.llm  # new RunnableSequence

    async def optimize(self, user_prompt: str) -> str:
        result = await self.chain.ainvoke({"query": user_prompt})
        return result.content.strip()