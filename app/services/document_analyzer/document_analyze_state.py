from typing_extensions import TypedDict


class DocumentAnalyzerState(TypedDict):
    document: str
    translated_text: str
    email: str
    retries: int
    user_language: str