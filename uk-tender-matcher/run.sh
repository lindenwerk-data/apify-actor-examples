#!/usr/bin/env bash
# UK tenders: daily IT tender alert from Find a Tender as a dated CSV (cron-friendly).
# Runs lindenwerk/uk-tender-matcher synchronously and prints the dataset items (csv).
# Needs: APIFY_TOKEN (Apify Console > Settings > API & Integrations), curl.
# The run is capped with maxTotalChargeUsd=0.10 (pay-per-event Actors only); override with MAX_TOTAL_CHARGE_USD.
# Sync runs must finish within 300 s; for bigger jobs start the run asynchronously (see ../README.md).
set -euo pipefail
cd "$(dirname "$0")"
: "${APIFY_TOKEN:?Set APIFY_TOKEN first}"
CAP="${MAX_TOTAL_CHARGE_USD:-0.10}"

curl --fail-with-body -sS -X POST \
  "https://api.apify.com/v2/acts/lindenwerk~uk-tender-matcher/run-sync-get-dataset-items?format=csv&clean=true&fields=relevanceScore,title,buyerName,buyerRegion,submissionDeadline,daysUntilDeadline,estimatedValue,suitableForSme,noticeUrl&maxTotalChargeUsd=${CAP}" \
  -H "Authorization: Bearer ${APIFY_TOKEN}" \
  -H "Content-Type: application/json" \
  --data @input.json \
  -o "uk-tenders-$(date +%F).csv"
echo "Saved uk-tenders-$(date +%F).csv (monitor mode: only notices not delivered before)"
