from sentence_transformers import CrossEncoder


class Reranker:

    def __init__(self):
        self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')


    def rerank(self, query: str, documents: list, top_k: int = 5) -> list:
        # Prepare (query, document) pairs
        pairs = [(query, document.page_content) for document in documents]

        # Get scores
        scores = self.cross_encoder.predict(pairs)

        # Combine with results
        scored_hits = list(zip(documents, scores))

        # Sort by score descending
        scored_hits.sort(key=lambda x: x[1], reverse=True)

        # Final top-k results
        top_results = [hit[0] for hit in scored_hits[:top_k]]
        return top_results





