from __future__ import annotations
import math
import pandas as pd


def precision_at_k(relevant, retrieved, k):
    retrieved_k = retrieved[:k]
    if not retrieved_k:
        return 0.0
    rel = sum(1 for d in retrieved_k if d in relevant)
    return rel / len(retrieved_k)


def recall_at_k(relevant, retrieved, k):
    if not relevant:
        return 0.0
    rel = sum(1 for d in retrieved[:k] if d in relevant)
    return rel / len(relevant)


def f1_score(p, r):
    return 0.0 if (p + r) == 0 else 2 * p * r / (p + r)


def average_precision(relevant, retrieved):
    if not relevant:
        return 0.0
    score, hit_count = 0.0, 0
    for i, doc in enumerate(retrieved, start=1):
        if doc in relevant:
            hit_count += 1
            score += hit_count / i
    return score / len(relevant)


def reciprocal_rank(relevant, retrieved):
    for i, doc in enumerate(retrieved, start=1):
        if doc in relevant:
            return 1 / i
    return 0.0


def ndcg_at_k(relevant, retrieved, k):
    dcg = 0.0
    for i, doc in enumerate(retrieved[:k], start=1):
        rel = 1 if doc in relevant else 0
        dcg += rel / math.log2(i + 1)
    ideal_hits = min(len(relevant), k)
    idcg = sum(1 / math.log2(i + 1) for i in range(1, ideal_hits + 1)) if ideal_hits > 0 else 0.0
    return 0.0 if idcg == 0 else dcg / idcg


def evaluate_runs(qrels: dict, run_results: dict, k: int = 5):
    rows = []
    for query, relevant in qrels.items():
        retrieved = run_results.get(query, [])
        p = precision_at_k(relevant, retrieved, k)
        r = recall_at_k(relevant, retrieved, k)
        rows.append({
            "query": query,
            "Precision@K": p,
            "Recall@K": r,
            "F1@K": f1_score(p, r),
            "MAP": average_precision(relevant, retrieved),
            "MRR": reciprocal_rank(relevant, retrieved),
            "NDCG@K": ndcg_at_k(relevant, retrieved, k),
        })
    df = pd.DataFrame(rows)
    if df.empty:
        return df, {}
    summary = {
        "Precision": round(df["Precision@K"].mean(), 4),
        "Recall": round(df["Recall@K"].mean(), 4),
        "F1-score": round(df["F1@K"].mean(), 4),
        "Precision@K": round(df["Precision@K"].mean(), 4),
        "Recall@K": round(df["Recall@K"].mean(), 4),
        "MAP": round(df["MAP"].mean(), 4),
        "MRR": round(df["MRR"].mean(), 4),
        "NDCG": round(df["NDCG@K"].mean(), 4),
    }
    return df, summary
