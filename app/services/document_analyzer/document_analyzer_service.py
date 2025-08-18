from langgraph.graph import StateGraph

from services.document_analyzer.document_analyze_state import DocumentAnalyzerState
from services.ocr.ocr_service import OCRService
from services.translation.translation_service import TranslationService


class DocumentAnalyzerService:

    def __init__(self):
        self.ocr_service = OCRService()
        self.translation_service = TranslationService()

    def analyze_document(self, uploaded_file, ocr_language, user_language):
        # Step 1: Extract OCR text
        ocr_text = self.ocr_service.extract_text_from_file(uploaded_file, ocr_language)

        # Step 2: Build workflow
        workflow = StateGraph(DocumentAnalyzerState)
        workflow.add_node("TranslationNode", self._translate_text_node)
        workflow.add_node("EmailNode", self._write_email_node)

        workflow.add_edge("TranslationNode", "EmailNode")
        workflow.set_entry_point("TranslationNode")

        graph = workflow.compile()

        # Step 3: Initial state
        state: DocumentAnalyzerState = {
            "document": ocr_text,
            "translated_text": "",
            "email": "",
            "retries": 3,
            "user_language": user_language
        }

        # Step 4: Run graph
        result = graph.invoke(state)
        return result

    def _translate_text_node(self, state: DocumentAnalyzerState) -> DocumentAnalyzerState:
        document = state["document"]
        user_language = state["user_language"]
        translated_text = self.translation_service.translate_text(document, user_language)
        state["translated_text"] = translated_text
        return state

    def _write_email_node(self, state: DocumentAnalyzerState) -> DocumentAnalyzerState:
        translated_text = state["translated_text"]

        return state
