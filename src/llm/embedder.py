from sentence_transformers import SentenceTransformer
from typing import List, Union

_model = None

def get_embedder() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def get_embedding(text: str) -> List[float]:
    model = get_embedder()
    return model.encode(text, convert_to_numpy=True).tolist()

def embed_texts(texts: Union[List[str], str]) -> List[List[float]]:
    model = get_embedder()
    return model.encode(texts, show_progress_bar=True, convert_to_numpy=True).tolist()

