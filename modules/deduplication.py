from __future__ import annotations
from difflib import SequenceMatcher
from modules.utils import stable_hash


def exact_deduplicate(records: list[dict]):
    seen_urls, seen_content = set(), set()
    unique, duplicates = [], []
    for rec in records:
        content_hash = stable_hash((rec.get("content") or "")[:5000])
        url = rec.get("url")
        if url in seen_urls or content_hash in seen_content:
            duplicates.append({**rec, "duplicate_type": "exact"})
        else:
            seen_urls.add(url)
            seen_content.add(content_hash)
            unique.append({**rec, "content_hash": content_hash})
    return unique, duplicates


def mark_near_duplicates(records: list[dict], threshold: float = 0.9):
    marked = []
    for i, rec in enumerate(records):
        is_near_dup = False
        for j in range(i):
            ratio = SequenceMatcher(None, (rec.get("content") or "")[:1500], (records[j].get("content") or "")[:1500]).ratio()
            if ratio >= threshold:
                is_near_dup = True
                break
        marked.append({**rec, "near_duplicate": is_near_dup})
    return marked
