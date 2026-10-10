# Document Q&A with retrieval and citations

Answers questions from a markdown document by retrieving the most relevant sections and returning them with citations. The model step is left out on purpose: the retrieval is the part that decides what the model would see, so this demo measures it directly.

- **Chunking:** split on headings, so each chunk keeps its section title for citations.
- **Retrieval:** TF-IDF scoring with a stopword filter. Questions with no matching terms return no context, and the caller escalates.
- **Evaluation:** `recall_at_k` checks whether the expected section appears in the top k results for labeled questions.

Files: `qa.py`, `test_qa.py`

Run: `python3 -m unittest`

Limitation: this is keyword retrieval, not embeddings. It handles exact terms well and synonyms poorly. Embeddings would be the next step.
