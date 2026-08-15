from __future__ import annotations
from collections import defaultdict


def build_inverted_index(records: list[dict]):
    inverted = defaultdict(list)
    metadata = []
    contents = {}
    for rec in records:
        doc_id = rec["doc_id"]
        contents[doc_id] = rec.get("content", "")
        metadata.append({
            "doc_id": doc_id,
            "title": rec.get("title", ""),
            "url": rec.get("url", ""),
            "domain": rec.get("domain", ""),
            "topic": rec.get("topic", "other"),
            "token_count": rec.get("token_count", 0),
            "near_duplicate": rec.get("near_duplicate", False),
        })
        seen = set()
        for token in rec.get("tokens", []):
            if token not in seen:
                inverted[token].append(doc_id)
                seen.add(token)
    return dict(inverted), metadata, contents
