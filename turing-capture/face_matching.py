# face_matching.py

import numpy as np
from numpy.linalg import norm

def cosine_similarity(emb1: np.ndarray, emb2: np.ndarray) -> float:
    """Compute cosine similarity between two embeddings."""
    if emb1 is None or emb2 is None:
        return 0.0
    return float(np.dot(emb1, emb2) / (norm(emb1) * norm(emb2)))

def is_match(emb1: np.ndarray, emb2: np.ndarray, threshold: float = 0.55) -> bool:
    """Return True if embeddings match above the similarity threshold."""
    score = cosine_similarity(emb1, emb2)
    return score >= threshold
