from __future__ import annotations
import time
from collections import deque
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from config import DEFAULT_TIMEOUT, DEFAULT_USER_AGENT


def is_valid_http_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


def extract_links(base_url: str, html: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    links = []
    for a in soup.find_all("a", href=True):
        href = urljoin(base_url, a["href"].strip())
        if is_valid_http_url(href):
            links.append(href.split("#")[0])
    return list(dict.fromkeys(links))


def fetch_url(url: str):
    headers = {"User-Agent": DEFAULT_USER_AGENT}
    start = time.perf_counter()
    try:
        r = requests.get(url, headers=headers, timeout=DEFAULT_TIMEOUT)
        elapsed = time.perf_counter() - start
        content_type = r.headers.get("Content-Type", "")
        if r.status_code == 200 and "text/html" in content_type:
            return {
                "url": url,
                "status": r.status_code,
                "elapsed_sec": round(elapsed, 4),
                "html": r.text,
                "content_type": content_type,
                "success": True,
            }
        return {
            "url": url,
            "status": r.status_code,
            "elapsed_sec": round(elapsed, 4),
            "html": "",
            "content_type": content_type,
            "success": False,
        }
    except Exception as e:
        elapsed = time.perf_counter() - start
        return {
            "url": url,
            "status": None,
            "elapsed_sec": round(elapsed, 4),
            "html": "",
            "content_type": "",
            "success": False,
            "error": str(e),
        }


def crawl(seed_urls: list[str], max_depth: int = 1, max_pages: int = 20):
    queue = deque([(u, 0) for u in seed_urls if is_valid_http_url(u)])
    visited = set()
    pages = []
    while queue and len(pages) < max_pages:
        url, depth = queue.popleft()
        if url in visited:
            continue
        visited.add(url)
        fetched = fetch_url(url)
        pages.append(fetched)
        if fetched.get("success") and depth < max_depth:
            for link in extract_links(url, fetched["html"]):
                if link not in visited and len(queue) + len(pages) < max_pages * 4:
                    queue.append((link, depth + 1))
    return pages
