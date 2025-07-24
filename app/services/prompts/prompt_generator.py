
from langchain.prompts import PromptTemplate

class PromptGenerator:
    def __init__(self):
        self._templates = {
            "final_answer": PromptTemplate.from_template(
                """You are a helpful AI immigration assistant for people moving to Switzerland.
                
                Use the context below to answer the user's question truthfully and clearly."
                
                Context:
                {context}
                
                Question:
                {question}
                
                Answer:"""
                            ),

                            "web_fallback": PromptTemplate.from_template(
                                """You are an AI immigration assistant using live information from the web.
                
                
                Web Search Result:
                {web_result}
                
                Question:
                {question}
                
                Answer:"""
                            ),

            # Future templates can go here:
            # "profile_based": PromptTemplate.from_template(...)
            # "tone_formal": PromptTemplate.from_template(...)
        }

    def generate(self, prompt_type: str, **kwargs) -> str:
        if prompt_type not in self._templates:
            raise ValueError(f"Prompt type '{prompt_type}' is not defined.")
        return self._templates[prompt_type].format(**kwargs)
