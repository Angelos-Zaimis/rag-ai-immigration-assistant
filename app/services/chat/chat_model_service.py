
from langchain_community.chat_models import ChatOpenAI
from langchain.schema.messages import AIMessage
from langchain_core.language_models.chat_models import BaseChatModel
from typing import Optional, Literal


class ChatModelService:
    def __init__(
        self,
        default_model: Literal["gpt-3.5", "gpt-4"] = "gpt-4",
        temperature: float = 0.2,
        streaming: bool = False,
    ):
        # Store config
        self.temperature = temperature
        self.streaming = streaming

        # Load models
        self.models = {
            "gpt-3.5": ChatOpenAI(model="gpt-3.5-turbo", temperature=temperature, streaming=streaming),
            "gpt-4": ChatOpenAI(model="gpt-4", temperature=temperature, streaming=streaming),
            # Future: add Mistral, Claude, local, etc.
        }

        self.default_model = default_model

    def get_model(self, name: Optional[str] = None) -> BaseChatModel:
        """Get model instance by name (or return default)"""
        return self.models.get(name or self.default_model)

    def invoke(self, prompt: str, model_name: Optional[str] = None) -> AIMessage:
        """Invoke the selected model with a prompt"""
        model = self.get_model(model_name)
        return model.invoke(prompt)

    def stream(self, prompt: str, model_name: Optional[str] = None):
        """Stream LLM output token-by-token (generator)"""
        model = self.get_model(model_name)
        return model.stream(prompt)
