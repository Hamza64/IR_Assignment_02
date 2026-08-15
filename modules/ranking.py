from __future__ import annotations
import networkx as nx
import pandas as pd
from modules.preprocessing import preprocess_tokens


def build_similarity_graph(records: list[dict], min_overlap: int = 3):
    g = nx.DiGraph()
    token_sets = {r["doc_id"]: set(r.get("tokens", [])) for r in records}
    for rec in records:
        g.add_node(rec["doc_id"], title=rec.get("title", ""))
    doc_ids = list(token_sets.keys())
    for i, d1 in enumerate(doc_ids):
        for d2 in doc_ids[i+1:]:
            overlap = len(token_sets[d1].intersection(token_sets[d2]))
            if overlap >= min_overlap:
                g.add_edge(d1, d2, weight=overlap)
                g.add_edge(d2, d1, weight=overlap)
    return g


def pagerank_scores(graph):
    if graph.number_of_nodes() == 0:
        return {}
    return nx.pagerank(graph, weight="weight")


def rerank_with_pagerank(search_df: pd.DataFrame, pr_scores: dict, alpha: float = 0.8):
    if search_df.empty:
        return search_df
    df = search_df.copy()
    df["pagerank"] = df["doc_id"].map(pr_scores).fillna(0.0)
    max_pr = df["pagerank"].max() or 1.0
    max_score = df["score"].max() or 1.0
    df["norm_pr"] = df["pagerank"] / max_pr
    df["norm_score"] = df["score"] / max_score
    df["final_score"] = alpha * df["norm_score"] + (1 - alpha) * df["norm_pr"]
    return df.sort_values("final_score", ascending=False).reset_index(drop=True)
