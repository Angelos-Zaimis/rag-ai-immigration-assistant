from context_cite import ContextCiter
from typing import List, Dict, Tuple
import re


class CitationService:

    def __init__(self, model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0", device: str = "cuda"):
        self.context_citer = ContextCiter.from_pretrained(model_name, device=device)

    @staticmethod
    def generate_citation_map(documents) -> Tuple[str, Dict[str, dict]]:
        citation_map = {}
        cited_contexts = []

        for i, document in enumerate(documents):
            source_id = f"source{i + 1}"
            marker = f"[@{source_id}]"

            citation_map[source_id] = {
                "marker": marker,
                "text": document.page_content,
                "metadata": document.metadata,
            }

            cited_contexts.append(f"{marker} {document.page_content}")

        context_str = "\n\n".join(cited_contexts)
        return context_str, citation_map

    def replace_markers(self, answer: str, citation_map: Dict[str, dict]) -> Tuple[str, str]:
        bibliography_entries: List[str] = []
        matched_sources = set()

        def marker_replacer(match):
            marker = match.group(0)
            source_id = marker[2:-1]
            citation = citation_map.get(source_id)
            print(f"🔎 Found marker: {marker} -> looking for: {source_id}")

            if citation:
                meta = citation["metadata"]
                author = meta.get("author", "Unknown Author")
                year = meta.get("year", "n.d.")
                title = meta.get("title", "Untitled")
                url = meta.get("url", "")

                bib_entry = f"{author} ({year}). *{title}*. {url}".strip()
                bibliography_entries.append(bib_entry)
                matched_sources.add(source_id)

                return f"({author}, {year})"
            return marker

        final_answer = re.sub(r"\[@source\d+\]", marker_replacer, answer)

        if not matched_sources:
            print("⚠️ No citation markers found in answer.")

        bibliography = "\n".join(sorted(set(bibliography_entries)))
        return final_answer, bibliography

    def cite_with_contextcite(self, context_documents: List, question: str) -> Tuple[str, str]:
        # Combine all context into one string
        context_text = "\n\n".join([doc.page_content for doc in context_documents])

        # Ask the context-cite model to generate an answer with inline citations
        cc_result = self.context_citer.generate(context=context_text, question=question)

        # Extract the answer
        cited_answer = cc_result.get_answer()

        # Get top source chunk IDs
        df = cc_result.get_attributions(as_dataframe=True, top_k=3)
        top_chunks = df['chunk_id'].unique().tolist()

        # Build bibliography from top chunks
        bibliography_entries = []
        for chunk_id in top_chunks:
            if chunk_id < len(context_documents):  # Safety check
                doc = context_documents[chunk_id]
                meta = doc.metadata
                author = meta.get("author", "Unknown Author")
                year = meta.get("year", "n.d.")
                title = meta.get("title", "Untitled")
                url = meta.get("url", "")
                bibliography_entries.append(f"{author} ({year}). *{title}*. {url}".strip())

        bibliography = "\n".join(sorted(set(bibliography_entries)))
        return cited_answer, bibliography