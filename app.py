from __future__ import annotations
import os
import json
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from config import DEFAULT_CRAWL_DEPTH, DEFAULT_MAX_PAGES, DEFAULT_SEEDS, SAMPLE_QUERIES
from modules.analytics import timer
from modules.crawler import crawl
from modules.parser import parse_html_record
from modules.deduplication import exact_deduplicate, mark_near_duplicates
from modules.profiling import profile_documents
from modules.indexer import build_inverted_index
from modules.search_engine import build_vector_models, search_records
from modules.ranking import build_similarity_graph, pagerank_scores, rerank_with_pagerank
from modules.recommender import recommend_similar
from modules.evaluation import evaluate_runs
from modules.utils import ensure_dir, save_json, load_json

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = ensure_dir(BASE_DIR / "data" / "raw")
PROCESSED_DIR = ensure_dir(BASE_DIR / "data" / "processed")
INDEX_DIR = ensure_dir(BASE_DIR / "data" / "indexes")
EVAL_DIR = ensure_dir(BASE_DIR / "data" / "evaluation")

st.set_page_config(page_title="Freight Intel IR System", page_icon="🚢", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1400px;}
.stTabs [data-baseweb="tab-list"] {gap: 10px;}
.stTabs [data-baseweb="tab"] {background: #eef2f6; border-radius: 10px; padding: 8px 14px;}
.stTabs [aria-selected="true"] {background: #16324f !important; color: white !important;}
.metric-card {background:#f8fafc;padding:12px 16px;border-radius:12px;border:1px solid #dbe4ee;}
.small-note {font-size:0.88rem;color:#4b5563;}
.result-box {background:#fbfdff;padding:12px 14px;border-radius:10px;border:1px solid #e5edf5;margin-bottom:10px;}
</style>
""", unsafe_allow_html=True)

st.title("🚢 Freight Intel IR System")
st.caption("End-to-end Streamlit Information Retrieval project for shipping and freight forwarding using public sources only.")

if "records" not in st.session_state:
    st.session_state.records = []
if "search_df" not in st.session_state:
    st.session_state.search_df = pd.DataFrame()
if "analytics" not in st.session_state:
    st.session_state.analytics = {}


def persist_artifacts(records, duplicates, inverted, metadata, contents):
    save_json(records, PROCESSED_DIR / "profiled_records.json")
    save_json(duplicates, PROCESSED_DIR / "duplicates.json")
    save_json(inverted, INDEX_DIR / "inverted_index.json")
    save_json(metadata, INDEX_DIR / "metadata_store.json")
    save_json(contents, INDEX_DIR / "content_store.json")


def load_artifacts():
    records = load_json(PROCESSED_DIR / "profiled_records.json", default=[])
    duplicates = load_json(PROCESSED_DIR / "duplicates.json", default=[])
    inverted = load_json(INDEX_DIR / "inverted_index.json", default={})
    metadata = load_json(INDEX_DIR / "metadata_store.json", default=[])
    contents = load_json(INDEX_DIR / "content_store.json", default={})
    return records, duplicates, inverted, metadata, contents


def corpus_df(records):
    if not records:
        return pd.DataFrame()
    return pd.DataFrame([{k: v for k, v in r.items() if k not in {"tokens", "content"}} for r in records])


tabs = st.tabs([
    "Dashboard", "Crawling", "Preprocessing", "Index Management", "Search", "Ranking", "Recommendations", "Evaluation", "Performance"
])

with tabs[0]:
    records, duplicates, inverted, metadata, contents = load_artifacts()
    df = corpus_df(records)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Documents", len(records))
    col2.metric("Duplicates Removed", len(duplicates))
    col3.metric("Vocabulary Size", len(inverted))
    col4.metric("Unique Domains", df["domain"].nunique() if not df.empty else 0)
    st.markdown("<div class='small-note'>This page summarizes corpus size, deduplication, indexing, and topic spread.</div>", unsafe_allow_html=True)
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            topic_counts = df["topic"].value_counts().reset_index()
            topic_counts.columns = ["topic", "count"]
            st.plotly_chart(px.bar(topic_counts, x="topic", y="count", title="Document distribution by topic"), use_container_width=True)
        with c2:
            domain_counts = df["domain"].value_counts().head(10).reset_index()
            domain_counts.columns = ["domain", "count"]
            st.plotly_chart(px.pie(domain_counts, names="domain", values="count", title="Top source domains"), use_container_width=True)
        st.dataframe(df[["title", "domain", "topic", "token_count", "near_duplicate"]].head(20), use_container_width=True)
    else:
        st.info("No processed corpus found yet. Go to the Crawling tab and build the corpus.")

with tabs[1]:
    st.subheader("Crawling interface")
    seed_text = st.text_area("Seed URLs (one per line)", value="\n".join(DEFAULT_SEEDS), height=180)
    c1, c2, c3 = st.columns(3)
    max_depth = c1.slider("Crawl depth", 0, 2, DEFAULT_CRAWL_DEPTH)
    max_pages = c2.slider("Max pages", 5, 50, DEFAULT_MAX_PAGES)
    preprocess_mode = c3.selectbox("Preprocessing mode", ["lemmatize", "stem", "raw"], index=0)
    if st.button("Run crawl and build corpus", type="primary"):
        seeds = [s.strip() for s in seed_text.splitlines() if s.strip()]
        with timer() as crawl_t:
            pages = crawl(seeds, max_depth=max_depth, max_pages=max_pages)
        parsed = [parse_html_record(p) for p in pages if p.get("success")]
        unique, duplicates = exact_deduplicate(parsed)
        unique = mark_near_duplicates(unique)
        with timer() as prof_t:
            records, counter = profile_documents(unique, mode=preprocess_mode)
        with timer() as idx_t:
            inverted, metadata, contents = build_inverted_index(records)
        persist_artifacts(records, duplicates, inverted, metadata, contents)
        st.session_state.records = records
        st.session_state.analytics = {
            "crawl_time_sec": crawl_t["elapsed_sec"],
            "profiling_time_sec": prof_t["elapsed_sec"],
            "index_time_sec": idx_t["elapsed_sec"],
            "pages_fetched": len(pages),
            "pages_parsed": len(parsed),
            "documents_indexed": len(records),
            "duplicates_removed": len(duplicates),
        }
        save_json(st.session_state.analytics, PROCESSED_DIR / "analytics.json")
        save_json(pages, RAW_DIR / "crawled_pages.json")
        st.success("Corpus built successfully from the Streamlit front end.")
        st.dataframe(pd.DataFrame(records)[["title", "domain", "topic", "token_count"]].head(15), use_container_width=True)

with tabs[2]:
    records, _, _, _, _ = load_artifacts()
    st.subheader("Text preprocessing and mining")
    if records:
        df = pd.DataFrame(records)
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(px.histogram(df, x="token_count", nbins=20, title="Token count distribution"), use_container_width=True)
        with c2:
            keywords = []
            for r in records:
                for kw in r.get("top_keywords", [])[:5]:
                    keywords.append(kw)
            kw_df = pd.Series(keywords).value_counts().head(15).reset_index()
            kw_df.columns = ["keyword", "count"]
            st.plotly_chart(px.bar(kw_df, x="keyword", y="count", title="Most frequent extracted keywords"), use_container_width=True)
        preview = df[["title", "topic", "token_count", "top_keywords"]].copy()
        st.dataframe(preview.head(20), use_container_width=True)
        st.markdown("**How to discuss this in report:** compare token reduction, topic clustering tendency, and how preprocessing changes feature quality.")
    else:
        st.info("Build the corpus first.")

with tabs[3]:
    records, duplicates, inverted, metadata, contents = load_artifacts()
    st.subheader("Index management")
    c1, c2, c3 = st.columns(3)
    c1.metric("Metadata rows", len(metadata))
    c2.metric("Content documents", len(contents))
    c3.metric("Inverted terms", len(inverted))
    if inverted:
        inv_df = pd.DataFrame({"term": list(inverted.keys())[:50], "posting_list_size": [len(v) for v in list(inverted.values())[:50]]})
        st.dataframe(inv_df, use_container_width=True)
    if metadata:
        st.markdown("### Metadata store preview")
        st.dataframe(pd.DataFrame(metadata).head(20), use_container_width=True)
    if contents:
        sample_doc = next(iter(contents.items()))
        st.markdown("### Content store preview")
        st.code(sample_doc[1][:1200] if isinstance(sample_doc[1], str) else str(sample_doc[1]))

with tabs[4]:
    records, _, _, _, _ = load_artifacts()
    st.subheader("Search interface")
    query = st.text_input("Enter query", value=SAMPLE_QUERIES[0])
    c1, c2, c3 = st.columns(3)
    method = c1.selectbox("Retrieval method", ["tfidf", "bm25"], index=1)
    top_k = c2.slider("Top K results", 3, 15, 8)
    filter_topic = c3.selectbox("Topic filter", ["All"] + sorted(list(set([r.get("topic", "other") for r in records]))) if records else ["All"])
    if st.button("Search documents"):
        if records:
            filtered = [r for r in records if filter_topic == "All" or r.get("topic") == filter_topic]
            vectorizer, matrix, bm25 = build_vector_models(filtered)
            with timer() as search_t:
                search_df = search_records(filtered, query, vectorizer, matrix, bm25, method=method, top_k=top_k)
            st.session_state.search_df = search_df
            analytics = load_json(PROCESSED_DIR / "analytics.json", default={})
            analytics["last_query_latency_sec"] = search_t["elapsed_sec"]
            analytics["last_query"] = query
            save_json(analytics, PROCESSED_DIR / "analytics.json")
            st.success(f"Retrieved {len(search_df)} documents.")
            for _, row in search_df.iterrows():
                st.markdown(f"<div class='result-box'><b>{row['title']}</b><br>{row['url']}<br>Topic: {row['topic']} | Domain: {row['domain']} | Score: {row['score']:.4f}<br><span class='small-note'>{row['snippet']}</span></div>", unsafe_allow_html=True)
        else:
            st.info("Build corpus first.")

with tabs[5]:
    records, _, _, _, _ = load_artifacts()
    st.subheader("Ranking visualization")
    if records:
        query_rank = st.text_input("Ranking demo query", value="bill of lading")
        vectorizer, matrix, bm25 = build_vector_models(records)
        base_df = search_records(records, query_rank, vectorizer, matrix, bm25, method="bm25", top_k=10)
        graph = build_similarity_graph(records)
        pr_scores = pagerank_scores(graph)
        reranked_df = rerank_with_pagerank(base_df, pr_scores, alpha=0.8)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Baseline ranking")
            st.dataframe(base_df[["title", "score", "topic"]], use_container_width=True)
        with c2:
            st.markdown("### BM25 + PageRank reranking")
            st.dataframe(reranked_df[["title", "score", "pagerank", "final_score", "topic"]], use_container_width=True)
        compare_df = pd.DataFrame({
            "Rank": list(range(1, min(len(base_df), len(reranked_df)) + 1)),
            "Baseline": base_df["title"].head(min(len(base_df), len(reranked_df))).tolist(),
            "Reranked": reranked_df["title"].head(min(len(base_df), len(reranked_df))).tolist(),
        })
        st.dataframe(compare_df, use_container_width=True)
        st.caption("Use this tab to explain why graph-aware ranking can improve the ordering of relevant freight-forwarding documents.")
    else:
        st.info("Build corpus first.")

with tabs[6]:
    records, _, _, _, _ = load_artifacts()
    st.subheader("Recommendation panel")
    if records:
        vectorizer, matrix, bm25 = build_vector_models(records)
        doc_map = {f"{r['title']} ({r['doc_id'][:8]})": r["doc_id"] for r in records}
        selected = st.selectbox("Choose document", list(doc_map.keys()))
        top_k_rec = st.slider("Top K recommendations", 3, 10, 5)
        rec_df = recommend_similar(records, matrix, doc_map[selected], top_k=top_k_rec)
        if not rec_df.empty:
            st.dataframe(rec_df, use_container_width=True)
            st.caption("This is content-based recommendation using document similarity scores.")
    else:
        st.info("Build corpus first.")

with tabs[7]:
    records, _, _, _, _ = load_artifacts()
    st.subheader("Evaluation dashboard")
    st.markdown("Provide or edit relevance judgments after corpus creation. A small manually prepared qrels set is enough for academic evaluation.")
    qrels_path = EVAL_DIR / "sample_qrels.json"
    qrels = load_json(qrels_path, default={})
    st.code(json.dumps(qrels, indent=2) if qrels else '{\n  "what is bill of lading": ["doc_id_1", "doc_id_2"]\n}')
    if records:
        queries = st.multiselect("Queries to evaluate", SAMPLE_QUERIES, default=SAMPLE_QUERIES[:4])
        method_eval = st.selectbox("Evaluation retrieval method", ["tfidf", "bm25"], index=1)
        k_eval = st.slider("K for evaluation", 3, 10, 5)
        if st.button("Run evaluation"):
            vectorizer, matrix, bm25 = build_vector_models(records)
            run_results = {}
            for q in queries:
                res = search_records(records, q, vectorizer, matrix, bm25, method=method_eval, top_k=10)
                run_results[q] = res["doc_id"].tolist() if not res.empty else []
            eval_df, summary = evaluate_runs(qrels, run_results, k=k_eval)
            if summary:
                cols = st.columns(4)
                metric_items = list(summary.items())
                for i, (k_, v_) in enumerate(metric_items[:4]):
                    cols[i].metric(k_, v_)
                cols2 = st.columns(4)
                for i, (k_, v_) in enumerate(metric_items[4:8]):
                    cols2[i].metric(k_, v_)
                st.dataframe(eval_df, use_container_width=True)
                melt_df = pd.DataFrame(summary.items(), columns=["metric", "value"])
                st.plotly_chart(px.bar(melt_df, x="metric", y="value", title="Evaluation metrics summary"), use_container_width=True)
            else:
                st.warning("Evaluation could not run because qrels are empty. Update sample_qrels.json after your first crawl.")
    else:
        st.info("Build corpus first.")

with tabs[8]:
    st.subheader("Performance analytics")
    analytics = load_json(PROCESSED_DIR / "analytics.json", default=st.session_state.analytics)
    if analytics:
        a_df = pd.DataFrame(list(analytics.items()), columns=["metric", "value"])
        st.dataframe(a_df, use_container_width=True)
        numeric_df = a_df[pd.to_numeric(a_df["value"], errors="coerce").notnull()].copy()
        if not numeric_df.empty:
            numeric_df["value"] = pd.to_numeric(numeric_df["value"])
            st.plotly_chart(px.bar(numeric_df, x="metric", y="value", title="Pipeline timing and performance analytics"), use_container_width=True)
    else:
        st.info("Run the pipeline first to generate analytics.")

st.markdown("---")
