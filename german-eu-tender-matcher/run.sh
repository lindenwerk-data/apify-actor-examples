#!/usr/bin/env bash
# German & EU tenders: open IT security tenders in Germany as a CSV.
# Runs lindenwerk/german-eu-tender-matcher synchronously and prints the dataset items (csv).
# Needs: APIFY_TOKEN (Apify Console > Settings > API & Integrations), curl.
# The run is capped with maxTotalChargeUsd=0.15 (pay-per-event Actors only); override with MAX_TOTAL_CHARGE_USD.
# Sync runs must finish within 300 s; for bigger jobs start the run asynchronously (see ../README.md).
set -euo pipefail
cd "$(dirname "$0")"
: "${APIFY_TOKEN:?Set APIFY_TOKEN first}"
CAP="${MAX_TOTAL_CHARGE_USD:-0.15}"

curl --fail-with-body -sS -X POST \
  "https://api.apify.com/v2/acts/lindenwerk~german-eu-tender-matcher/run-sync-get-dataset-items?format=csv&clean=true&fields=relevanceScore,title,buyerName,buyerState,submissionDeadline,daysUntilDeadline,estimatedValue,cpvMain,noticeUrl&maxTotalChargeUsd=${CAP}" \
  -H "Authorization: Bearer ${APIFY_TOKEN}" \
  -H "Content-Type: application/json" \
  --data @input.json \
  -o "tenders-de-$(date +%F).csv"
echo "Saved tenders-de-$(date +%F).csv"
