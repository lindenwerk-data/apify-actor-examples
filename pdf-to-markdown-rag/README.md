# PDF to Markdown & RAG Chunks: Document Parser (DOCX/PPTX/XLSX): example

Store: https://apify.com/lindenwerk/pdf-to-markdown-rag · Example task:
[Convert a PDF with tables to Markdown and RAG chunks](https://apify.com/lindenwerk/pdf-to-markdown-rag/examples/pdf-tables-to-markdown-rag-chunks)

**Use case: PDF to RAG chunks into a vector store.** You have PDFs, Word, PowerPoint or Excel files (tender
documents, manuals, reports) and want clean Markdown, with tables kept as Markdown tables, plus heading-aware
chunks that carry page numbers so your LLM answers can cite "page 4".

[`input.json`](input.json) converts a public one-page W3C sample PDF with a table into Markdown and
1,000-character chunks with 100 characters of overlap. Replace `documentUrls` with links to your own files.
Files that aren't public can go in via a key-value store (`keyValueStoreId`, `keyValueStoreKeys`) or as
`base64Documents`.

```bash
export APIFY_TOKEN=...
python run.py      # -> markdown/<file>.md + chunks.jsonl  ({id, text, metadata{fileName,pageStart,pageEnd,headingPath}})
./run.sh           # curl version, JSON Lines (document rows and chunk rows)
```

Load `chunks.jsonl` into a vector store, for example with Chroma (`pip install chromadb`):

```python
import json, chromadb
rows = [json.loads(line) for line in open("chunks.jsonl", encoding="utf-8")]
col = chromadb.PersistentClient(path="./vectors").get_or_create_collection("docs")
col.upsert(ids=[r["id"] for r in rows], documents=[r["text"] for r in rows],
           metadatas=[{k: v for k, v in r["metadata"].items() if v is not None} for r in rows])
print(col.query(query_texts=["What does the table show?"], n_results=3)["metadatas"])
```

The same `{id, text, metadata}` shape works for Qdrant, pgvector, Pinecone or LangChain/LlamaIndex loaders once
you add your embedding step.

**Cost:** USD 0.002 per converted document plus USD 0.0005 per page with text. Failed, encrypted, empty and
scanned-only files are free. Each run also has the USD 0.00005 start event. This input costs about USD 0.003; the scripts cap it at `maxTotalChargeUsd` 0.02.

**Adapt it**
- Only chunks (no full Markdown rows): `"outputMode": "chunks"`.
- Bigger chunks for long-context models: `"chunkSize": 3000, "chunkOverlap": 300`.
- Only part of a long PDF: `"pageRange": "1-10"`.
- Scanned pages are flagged (`scannedPageCount`) but not OCR'd.
