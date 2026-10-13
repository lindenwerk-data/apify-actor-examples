#!/usr/bin/env python3
"""Post new tender matches to a Slack (or any JSON) incoming webhook.

Runs one of the Lindenwerk Data tender Actors in *monitor* mode, so each run returns
only notices that earlier runs with the same stateKey have not delivered yet (and only
those are charged). Then it posts a compact digest to the webhook in SLACK_WEBHOOK_URL.

    pip install -r ../requirements.txt
    export APIFY_TOKEN=...
    export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...   # leave unset for a dry run
    python tenders-to-slack-webhook.py uk-tender-matcher
    python tenders-to-slack-webhook.py german-eu-tender-matcher --max-charge 0.20

The input comes from ../<actor>/input.json; mode is forced to "monitor" and a stable
stateKey is set, so run it once a day from cron, GitHub Actions or an Apify schedule.
Without SLACK_WEBHOOK_URL the message is printed instead of posted.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from decimal import Decimal
from pathlib import Path

from apify_client import ApifyClient

ROOT = Path(__file__).resolve().parent.parent

# Output field names per Actor (from each Actor's dataset schema).
ACTORS = {
    "german-eu-tender-matcher": {"buyer": "buyerName", "where": "buyerState", "deadline": "submissionDeadline", "flag": "🇩🇪"},
    "france-tender-matcher": {"buyer": "buyerName", "where": "departments", "deadline": "submissionDeadline", "flag": "🇫🇷"},
    "uk-tender-matcher": {"buyer": "buyerName", "where": "buyerRegion", "deadline": "submissionDeadline", "flag": "🇬🇧"},
    "sam-gov-contract-matcher": {"buyer": "subTier", "where": "placeOfPerformanceState", "deadline": "responseDeadline", "flag": "🇺🇸"},
}
PER_MESSAGE = 15  # keep Slack messages readable


def _get(run, key: str, attr: str):
    if run is None:
        return None
    return run.get(key) if isinstance(run, dict) else getattr(run, attr, None)


def fetch_new_matches(actor: str, max_charge: Decimal) -> list[dict]:
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        sys.exit("Set APIFY_TOKEN first.")
    run_input = json.loads((ROOT / actor / "input.json").read_text(encoding="utf-8"))
    run_input["mode"] = "monitor"
    run_input.setdefault("stateKey", f"slack-{run_input.get('profileName', actor)}")
    # Fields such as postedWithinDays (SAM.gov search mode) are ignored in monitor mode.
    client = ApifyClient(token)
    run = client.actor(f"lindenwerk/{actor}").call(run_input=run_input, max_total_charge_usd=max_charge)
    status = str(_get(run, "status", "status")).split(".")[-1].upper()
    if status != "SUCCEEDED":
        sys.exit(f"Run ended with status {status}; check the run log in Apify Console.")
    return list(client.dataset(_get(run, "defaultDatasetId", "default_dataset_id")).iterate_items())


def _short(value, limit: int = 140) -> str:
    if isinstance(value, list):
        value = ", ".join(str(v) for v in value)
    text = str(value or "").strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


def format_lines(actor: str, rows: list[dict]) -> list[str]:
    f = ACTORS[actor]
    lines = []
    for r in rows:
        deadline = _short(r.get(f["deadline"]), 10) or "n/a"
        days = r.get("daysUntilDeadline")
        when = f"{deadline} ({days} d)" if days is not None else deadline
        lines.append(
            f"• *{r.get('relevanceScore', '-')}* <{r.get('noticeUrl')}|{_short(r.get('title'), 110)}>\n"
            f"   {_short(r.get(f['buyer']), 70)} · {_short(r.get(f['where']), 40)} · deadline {when}"
        )
    return lines


def post(webhook: str | None, text: str) -> None:
    if not webhook:
        print(text, end="\n\n")
        return
    req = urllib.request.Request(
        webhook,
        data=json.dumps({"text": text}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 (URL comes from your env)
        resp.read()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("actor", choices=sorted(ACTORS))
    parser.add_argument("--max-charge", type=Decimal, default=Decimal("0.10"),
                        help="maxTotalChargeUsd for the run (default 0.10)")
    parser.add_argument("--quiet-if-empty", action="store_true", help="post nothing when there are no new matches")
    args = parser.parse_args()

    rows = fetch_new_matches(args.actor, args.max_charge)
    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    flag = ACTORS[args.actor]["flag"]
    if not rows:
        if not args.quiet_if_empty:
            post(webhook, f"{flag} {args.actor}: no new matches today.")
        return
    lines = format_lines(args.actor, rows)
    for start in range(0, len(lines), PER_MESSAGE):
        head = f"{flag} *{len(rows)} new tender match(es)* from {args.actor}"
        if len(lines) > PER_MESSAGE:
            head += f" ({start // PER_MESSAGE + 1}/{-(-len(lines) // PER_MESSAGE)})"
        post(webhook, head + "\n" + "\n".join(lines[start:start + PER_MESSAGE]))
    print(f"{len(rows)} new matches {'posted' if webhook else 'printed (dry run)'}.")


if __name__ == "__main__":
    main()
