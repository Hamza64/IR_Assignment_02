from __future__ import annotations
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from modules.utils import stable_hash


def parse_html_record(page: dict) -> dict:
    html = page.get("html", "") or ""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()
    title = soup.title.get_text(" ", strip=True) if soup.title else page.get("url", "Untitled")
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all(["p", "li"])]
    text = " ".join([p for p in paragraphs if p])
    meta_desc = ""
    desc_tag = soup.find("meta", attrs={"name": "description"})
    if desc_tag:
        meta_desc = desc_tag.get("content", "")
    domain = urlparse(page.get("url", "")).netloc
    doc_id = stable_hash((page.get("url", "") + title + text[:200]).strip())
    return {
        "doc_id": doc_id,
        "url": page.get("url", ""),
        "domain": domain,
        "title": title,
        "meta_description": meta_desc,
        "content": text,
        "content_length": len(text.split()),
        "status": page.get("status"),
        "elapsed_sec": page.get("elapsed_sec"),
    }
