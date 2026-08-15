from __future__ import annotations
from collections import Counter
from config import TOPIC_KEYWORDS
from modules.preprocessing import preprocess_tokens


def infer_topic(text: str) -> str:
    lower = text.lower()
    scores = {}
    for topic, kws in TOPIC_KEYWORDS.items():
        scores[topic] = sum(1 for kw in kws if kw in lower)
    best_topic = max(scores, key=scores.get) if scores else "other"
    return best_topic if scores.get(best_topic, 0) > 0 else "other"


def profile_documents(records: list[dict], mode: str = "lemmatize"):
    profiled = []
    corpus_counter = Counter()
    for rec in records:
        tokens = preprocess_tokens((rec.get("title", "") + " " + rec.get("content", "")), mode=mode)
        corpus_counter.update(tokens)
        profiled.append({
            **rec,
            "topic": infer_topic((rec.get("title", "") + " " + rec.get("content", ""))),
            "tokens": tokens,
            "token_count": len(tokens),
            "top_keywords": [w for w, _ in Counter(tokens).most_common(10)],
        })
    return profiled, corpus_counter
