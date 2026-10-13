#!/usr/bin/env bash
# SAM.gov: open US federal IT opportunities with a small-business set-aside as a CSV.
# Runs lindenwerk/sam-gov-contract-matcher synchronously and prints the dataset items (csv).
# Needs: APIFY_TOKEN (Apify Console > Settings > API & Integrations), curl.
# The run is capped with maxTotalChargeUsd=0.05 (pay-per-event Actors only); override with MAX_TOTAL_CHARGE_USD.
# Sync runs must finish within 300 s; for bigger jobs start the run asynchronously (see ../README.md).
set -euo pipefail
cd "$(dirname "$0")"
: "${APIFY_TOKEN:?Set APIFY_TOKEN first}"
CAP="${MAX_TOTAL_CHARGE_USD:-0.05}"

curl --fail-with-body -sS -X POST \
  "https://api.apify.com/v2/acts/lindenwerk~sam-gov-contract-matcher/run-sync-get-dataset-items?format=csv&clean=true&fields=relevanceScore,title,subTier,noticeType,setAsideCode,naicsCode,responseDeadline,daysUntilDeadline,noticeUrl&maxTotalChargeUsd=${CAP}" \
  -H "Authorization: Bearer ${APIFY_TOKEN}" \
  -H "Content-Type: application/json" \
  --data @input.json \
  -o "sam-gov-$(date +%F).csv"
echo "Saved sam-gov-$(date +%F).csv"
