from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi
from modules.preprocessing import preprocess_tokens


def build_vector_models(records: list[dict]):
    docs = [" ".join(r.get("tokens", [])) for r in records]
    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform(docs) if docs else None
    bm25 = BM25Okapi([r.get("tokens", []) for r in records]) if docs else None
    return vectorizer, matrix, bm25


def search_records(records: list[dict], query: str, vectorizer, matrix, bm25, method: str = "tfidf", top_k: int = 10):
    if not records:
        return pd.DataFrame()
    q_tokens = preprocess_tokens(query, mode="lemmatize")
    if not q_tokens:
        return pd.DataFrame()
    if method == "bm25" and bm25 is not None:
        scores = bm25.get_scores(q_tokens)
    else:
        q_vec = vectorizer.transform([" ".join(q_tokens)])
        scores = cosine_similarity(q_vec, matrix)[0]
    rows = []
    for rec, score in zip(records, scores):
        rows.append({
            "doc_id": rec["doc_id"],
            "title": rec.get("title", ""),
            "url": rec.get("url", ""),
            "domain": rec.get("domain", ""),
            "topic": rec.get("topic", "other"),
            "score": float(score),
            "snippet": (rec.get("content", "")[:250] + "...") if rec.get("content") else "",
        })
    df = pd.DataFrame(rows).sort_values("score", ascending=False).head(top_k)
    return df.reset_index(drop=True)
