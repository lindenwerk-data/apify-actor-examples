#!/usr/bin/env python3
"""PDF/DOCX/PPTX/XLSX to Markdown plus RAG chunks, written as chunks.jsonl ready for a vector store.

Usage:
    pip install -r ../requirements.txt
    export APIFY_TOKEN=...            # https://console.apify.com/settings/integrations
    python run.py                     # uses input.json next to this file

Cost cap: the run is started with max_total_charge_usd=0.02 (override with
MAX_TOTAL_CHARGE_USD). Pay-per-event prices: https://apify.com/lindenwerk/pdf-to-markdown-rag
"""
from __future__ import annotations

import csv
import json
import os
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

from apify_client import ApifyClient

ACTOR_ID = "lindenwerk/pdf-to-markdown-rag"
HERE = Path(__file__).resolve().parent
MAX_TOTAL_CHARGE_USD = Decimal(os.environ.get("MAX_TOTAL_CHARGE_USD", "0.02"))


def _get(run, key: str, attr: str):
    """apify-client 1.x/2.x return dicts, 3.x returns a model object."""
    if run is None:
        return None
    return run.get(key) if isinstance(run, dict) else getattr(run, attr, None)


def run_actor() -> list[dict]:
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        sys.exit("Set APIFY_TOKEN first (Apify Console > Settings > API & Integrations).")
    run_input = json.loads((HERE / "input.json").read_text(encoding="utf-8"))
    client = ApifyClient(token)
    run = client.actor(ACTOR_ID).call(
        run_input=run_input,
        max_total_charge_usd=MAX_TOTAL_CHARGE_USD,
    )
    status = _get(run, "status", "status")
    print(f"Run status: {status} ({_get(run, 'statusMessage', 'status_message') or ''})")
    if run is None or str(status).split(".")[-1].upper() != "SUCCEEDED":
        sys.exit("Run did not succeed; open the run in Apify Console for the log.")
    dataset_id = _get(run, "defaultDatasetId", "default_dataset_id")
    return list(client.dataset(dataset_id).iterate_items())


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: _flat(row.get(k)) for k in fields})


def _flat(value):
    if isinstance(value, list):
        return "; ".join(str(v) for v in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return value



def main() -> None:
    rows = run_actor()
    docs = [r for r in rows if r.get("rowType") == "document"]
    chunks = [r for r in rows if r.get("rowType") == "chunk"]
    md_dir = HERE / "markdown"
    md_dir.mkdir(exist_ok=True)
    for i, doc in enumerate(docs):
        name = Path(doc.get("fileName") or f"document-{i}").stem + ".md"
        (md_dir / name).write_text(doc.get("markdown") or "", encoding="utf-8")
        print(f"- {doc.get('fileName')}: {doc.get('status')}, {doc.get('pagesConverted')} pages, "
              f"{doc.get('tableCount')} tables, {doc.get('chunkCount')} chunks")
    # One line per chunk: {id, text, metadata}. Most vector stores (Chroma, Qdrant,
    # pgvector, Pinecone ...) take exactly this shape after you add embeddings.
    out = HERE / "chunks.jsonl"
    with out.open("w", encoding="utf-8") as fh:
        for c in chunks:
            record = {
                "id": c.get("chunkId") or f"{c.get('fileName')}#{c.get('chunkIndex')}",
                "text": c.get("text"),
                "metadata": {
                    "source": c.get("source"),
                    "fileName": c.get("fileName"),
                    "pageStart": c.get("pageStart"),
                    "pageEnd": c.get("pageEnd"),
                    "headingPath": _flat(c.get("headingPath")),
                    "tokenEstimate": c.get("tokenEstimate"),
                },
            }
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"{len(docs)} documents -> markdown/, {len(chunks)} chunks -> {out.name}")


if __name__ == "__main__":
    main()
