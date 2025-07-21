from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent


class AgentService:

    def __init__(self):
        pass

    @staticmethod
    def create_agent(model: str, prompt: str, topic: str):
       return create_react_agent(
           model=model,
           tools=[],
           prompt=prompt,

       )

    @staticmethod
    def create_web_search_prompt():
        return ChatPromptTemplate.from_messages(
            messages=[
                ("system",
                 "You are a web researcher and your goal is to find Swiss official information about the provided topic."),
                ("human", "The topic is: {input}"),
            ],
        )


