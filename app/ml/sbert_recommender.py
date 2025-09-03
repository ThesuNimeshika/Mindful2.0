import numpy as np
from sentence_transformers import SentenceTransformer

class SBERTRecommender:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        # Load SBERT model once
        self.model = SentenceTransformer(model_name)
        self.item_texts = []
        self.item_ids = []
        self.item_embeddings = None

    def fit(self, items):
        if not items:
            return

        self.item_texts = [a["text"] for a in items]
        self.item_ids = [a["id"] for a in items]

        # Encode all items at once
        embeddings = self.model.encode(
            self.item_texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        self.item_embeddings = embeddings

    def recommend(self, text, top_k=5):
        if self.item_embeddings is None or len(self.item_embeddings) == 0 or not text:
            return []

        # Encode diary entry
        query_emb = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        # Cosine similarity = dot product (since normalized)
        sims = np.dot(self.item_embeddings, query_emb)

        # Get top-k
        top_indices = sims.argsort()[::-1][:top_k]
        return [
            {"id": self.item_ids[i], "score": float(sims[i])}
            for i in top_indices
        ]
