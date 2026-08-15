# Freight Intel IR System

Information Retrieval Assignment 2, focused on shipping and freight forwarding using only public sources.

## Features
- Public web crawling with configurable depth and multiple seed URLs
- Duplicate and near-duplicate detection
- Metadata/content separation
- Text preprocessing and mining
- Inverted index creation
- Search using TF-IDF or BM25
- Ranking importance using PageRank-based reranking
- Content-based recommendation
- Evaluation metrics dashboard
- Performance analytics of the dashboard


## Project Structure
- `app.py` - Main Streamlit application
- `modules/` - Functional modules
- `data/raw/` - Crawled pages and parsed documents
- `data/processed/` - Profiled records
- `data/indexes/` - Inverted index and metadata stores
- `data/evaluation/` - Relevance judgments and evaluation artifacts
- `data/seeds/` - Default crawl seeds

## Installation
```bash
pip install -r requirements.txt
```

## Run
```bash
streamlit run app.py
```

## Notes
- Run crawling from the Streamlit UI to satisfy the assignment requirement that the workflow be executable through the front end.
- Used public seed URLs only.
- Captured screenshots from each major section for the report.

## Recommended screenshots for report
1. Dashboard overview
2. Crawl interface with seed URLs and crawl output
3. Preprocessing and document profiling charts
4. Index statistics page
5. Search results page
6. Ranking comparison page
7. Recommendation page
8. Evaluation metrics dashboard
9. Performance analytics page
