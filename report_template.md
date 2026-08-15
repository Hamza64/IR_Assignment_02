# Information Retrieval Assignment 2 Report

## Title
FreightIntel IR System: A Streamlit-Based End-to-End Information Retrieval Platform for Shipping and Freight Forwarding Knowledge Discovery

## Objective
This project develops a Streamlit-based end-to-end Information Retrieval system for the shipping and freight forwarding domain using public web sources. The system demonstrates crawling, preprocessing, indexing, ranked retrieval, recommendation, evaluation, and performance analytics in a single integrated application.

## Use Case
The chosen use case is freight forwarding knowledge retrieval, where users search and explore documents related to shipping concepts such as Incoterms, customs clearance, documentation, port congestion, containerization, and supply chain disruptions.

## Implementation Overview
- Public multi-source crawling through seed URLs
- Duplicate URL and duplicate document handling
- Metadata stored separately from document content
- Text preprocessing with tokenization, stopword removal, stemming and lemmatization comparison
- Keyword extraction and document profiling
- Inverted index and vector-space search
- Ranking importance via PageRank-based reranking
- Content-based Top-K recommendations
- Evaluation with Precision, Recall, F1-score, Precision@K, Recall@K, MAP, MRR, and NDCG

## Virtual Lab / Local Execution
Mention that the application was first tested locally and then prepared for execution in the virtual lab through the Streamlit front end.

## Experimental Results
Add screenshots, tables, and charts from the application.

## Compulsory Inference and Discussion
1. If highly relevant documents are retrieved but ranked poorly, possible causes include weak feature weighting, missing query expansion, insufficient field weighting, noisy documents, or graph-based signals not being included. Improvements include BM25 tuning, title weighting, query expansion, semantic reranking, and graph-based reranking.
2. Duplicate and near-duplicate documents inflate index size, distort ranking by repeating similar evidence, reduce diversity in recommendation, and bias evaluation metrics. Mitigation can include URL deduplication, content hashing, near-duplicate similarity checks, and cluster-level ranking.
3. Content-based recommendation is effective when document features are rich and user history is unavailable, which suits cold-start or knowledge retrieval systems. Collaborative recommendation is stronger when interaction history exists at scale and user behavior patterns are stable.
4. Crawling collects the corpus, preprocessing converts raw text into structured features, indexing supports efficient lookup, search retrieves relevant documents, ranking orders them effectively, and recommendation improves discovery beyond the initial query. Their integration improves usability, retrieval quality, and system completeness.
5. Add project-specific learnings after running experiments.

## Submission Checklist
- Streamlit application code
- Supporting files
- Dataset / crawled collection
- Report with screenshots and tables
- Demo evidence
- README with install and run commands
