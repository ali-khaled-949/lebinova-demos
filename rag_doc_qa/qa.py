"""Tiny retrieval-augmented Q&A over markdown: heading-based chunks, TF-IDF retrieval, cited answers.

No API key needed. The retriever is the part that decides what an LLM would see, so it is measured with recall@k.
"""
import math
import re
from collections import Counter

WORD = re.compile(r"[a-z0-9]+")
STOPWORDS = {"a", "an", "the", "is", "are", "be", "in", "of", "on", "to", "for", "and", "or", "it", "do", "does",
             "what", "how", "long", "when", "where", "which", "who", "why", "there", "that", "this", "with"}


def chunk_markdown(text: str, source: str) -> list[dict]:
    """Split on headings so each chunk keeps its section title for citations."""
    chunks, title, body = [], "intro", []
    for line in text.splitlines():
        if line.startswith("#"):
            if body:
                chunks.append({"source": source, "section": title, "text": " ".join(body)})
            title, body = line.lstrip("# ").strip(), []
        elif line.strip():
            body.append(line.strip())
    if body:
        chunks.append({"source": source, "section": title, "text": " ".join(body)})
    return chunks


def tokens(text: str) -> list[str]:
    return [w for w in WORD.findall(text.lower()) if w not in STOPWORDS]


class Index:
    def __init__(self, chunks: list[dict]):
        self.chunks = chunks
        self.docs = [Counter(tokens(c["section"] + " " + c["text"])) for c in chunks]
        n = len(chunks)
        df = Counter(term for doc in self.docs for term in doc)
        self.idf = {t: math.log((1 + n) / (1 + d)) + 1 for t, d in df.items()}

    def search(self, query: str, k: int = 3) -> list[tuple[float, dict]]:
        q = Counter(tokens(query))
        scored = []
        for doc, chunk in zip(self.docs, self.chunks):
            score = sum(q[t] * doc[t] * self.idf.get(t, 0) for t in q if t in doc)
            if score > 0:
                scored.append((score / (1 + math.sqrt(sum(v * v for v in doc.values()))), chunk))
        return sorted(scored, key=lambda s: s[0], reverse=True)[:k]

    def answer(self, query: str, k: int = 3) -> dict:
        hits = self.search(query, k)
        if not hits:
            return {"context": [], "citations": [], "note": "No supporting text found; escalate to a person."}
        return {
            "context": [h[1]["text"] for h in hits],
            "citations": [f"{h[1]['source']} > {h[1]['section']}" for h in hits],
        }


def recall_at_k(index: Index, cases: list[tuple[str, str]], k: int = 3) -> float:
    """cases: (question, expected source > section). Share of questions whose expected section is in the top k."""
    hits = 0
    for question, expected in cases:
        cites = [f"{c['source']} > {c['section']}" for _, c in index.search(question, k)]
        hits += expected in cites
    return hits / len(cases) if cases else 0.0
