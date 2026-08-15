from __future__ import annotations
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from config import STOPWORDS_EXTRA

for pkg in ["punkt", "stopwords", "wordnet", "omw-1.4"]:
    try:
        nltk.data.find(pkg)
    except Exception:
        nltk.download(pkg, quiet=True)

STOP_WORDS = set(stopwords.words("english")).union(set(STOPWORDS_EXTRA))
STEMMER = PorterStemmer()
LEMMATIZER = WordNetLemmatizer()


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> list[str]:
    return [t for t in normalize_text(text).split() if t]


def preprocess_tokens(text: str, mode: str = "lemmatize") -> list[str]:
    tokens = [t for t in tokenize(text) if t not in STOP_WORDS and len(t) > 2]
    if mode == "stem":
        return [STEMMER.stem(t) for t in tokens]
    if mode == "lemmatize":
        return [LEMMATIZER.lemmatize(t) for t in tokens]
    return tokens
