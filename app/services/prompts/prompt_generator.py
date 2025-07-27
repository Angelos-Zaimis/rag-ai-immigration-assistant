
from langchain.prompts import PromptTemplate

class PromptGenerator:
    def __init__(self):
        self._templates = {
            "final_answer": PromptTemplate.from_template(
                """You are a helpful AI immigration assistant for people moving to Switzerland.
                - Speak naturally and helpfully, like you're talking to a newcomer.
                - Keep all important legal or formal facts.
                - Also include practical tips (e.g., where to find housing, job platforms, etc.)
                - Use headings and bullet points for clarity.
                - If something is mandatory or time-sensitive (like health insurance), emphasize it clearly.
                - Use markdown format for output.

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
