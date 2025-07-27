from langchain_openai import ChatOpenAI
from langchain.schema.messages import AIMessage
from langchain_core.language_models.chat_models import BaseChatModel
from typing import Optional, Literal


class ChatModelService:
    def __init__(
        self,
        default_model: Literal["gpt-3.5", "gpt-4"] = "gpt-4o",
        temperature: float = 0.2,
        streaming: bool = True,
    ):
        self.temperature = temperature
        self.streaming = streaming

        self.models = {
            "gpt-3.5": ChatOpenAI(model="gpt-3.5-turbo", temperature=temperature, streaming=streaming),
            "gpt-4o": ChatOpenAI(model="gpt-4o", temperature=temperature, streaming=streaming),
        }

        self.default_model = default_model

    def get_model(self, name: Optional[str] = None) -> BaseChatModel:
        return self.models.get(name or self.default_model)

    async def invoke(self, prompt: str, model_name: Optional[str] = None) -> AIMessage:
        """Async invoke for the selected model"""
        model = self.get_model(model_name)
        return await model.ainvoke(prompt)  # <-- USE async invocation

    def stream(self, prompt: str, model_name: Optional[str] = None):
        model = self.get_model(model_name)
        return model.stream(prompt)
