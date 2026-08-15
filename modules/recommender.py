from __future__ import annotations
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


def recommend_similar(records: list[dict], matrix, selected_doc_id: str, top_k: int = 5):
    if matrix is None or not records:
        return pd.DataFrame()
    idx_map = {r["doc_id"]: i for i, r in enumerate(records)}
    if selected_doc_id not in idx_map:
        return pd.DataFrame()
    idx = idx_map[selected_doc_id]
    sims = cosine_similarity(matrix[idx], matrix)[0]
    rows = []
    for rec, score in zip(records, sims):
        if rec["doc_id"] == selected_doc_id:
            continue
        rows.append({
            "doc_id": rec["doc_id"],
            "title": rec.get("title", ""),
            "url": rec.get("url", ""),
            "topic": rec.get("topic", "other"),
            "similarity_score": float(score),
        })
    return pd.DataFrame(rows).sort_values("similarity_score", ascending=False).head(top_k).reset_index(drop=True)
