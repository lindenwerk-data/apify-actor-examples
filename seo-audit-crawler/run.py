#!/usr/bin/env python3
"""SEO audit of a small site sample: page scores, issues and the site summary (AI crawlers, llms.txt).

Usage:
    pip install -r ../requirements.txt
    export APIFY_TOKEN=...            # https://console.apify.com/settings/integrations
    python run.py                     # uses input.json next to this file

Cost cap: the run is started with max_total_charge_usd=0.06 (override with
MAX_TOTAL_CHARGE_USD). Pay-per-event prices: https://apify.com/lindenwerk/seo-audit-crawler
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

ACTOR_ID = "lindenwerk/seo-audit-crawler"
HERE = Path(__file__).resolve().parent
MAX_TOTAL_CHARGE_USD = Decimal(os.environ.get("MAX_TOTAL_CHARGE_USD", "0.06"))


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


FIELDS = ["url", "httpStatus", "score", "issueCount", "issueIds", "title", "indexable"]


def main() -> None:
    rows = run_actor()
    pages = [r for r in rows if r.get("rowType") != "site"]
    sites = [r for r in rows if r.get("rowType") == "site"]
    out = HERE / f"seo-pages-{date.today().isoformat()}.csv"
    write_csv(out, pages, FIELDS)
    print(f"{len(pages)} pages -> {out.name}")
    for page in sorted(pages, key=lambda r: r.get("score") or 0)[:5]:
        print(f"- score {page.get('score')}: {page.get('url')} -> {_flat(page.get('issueIds'))}")
    for site in sites:
        summary_path = HERE / "site-summary.json"
        summary_path.write_text(json.dumps(site.get("siteSummary"), indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Site summary for {site.get('site')} -> {summary_path.name}")


if __name__ == "__main__":
    main()
