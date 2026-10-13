#!/usr/bin/env bash
# Tech stack of a few competitor domains, one JSON object per site.
# Runs lindenwerk/tech-stack-detector synchronously and prints the dataset items (json).
# Needs: APIFY_TOKEN (Apify Console > Settings > API & Integrations), curl.
# The run is capped with maxTotalChargeUsd=0.05 (pay-per-event Actors only); override with MAX_TOTAL_CHARGE_USD.
# Sync runs must finish within 300 s; for bigger jobs start the run asynchronously (see ../README.md).
set -euo pipefail
cd "$(dirname "$0")"
: "${APIFY_TOKEN:?Set APIFY_TOKEN first}"
CAP="${MAX_TOTAL_CHARGE_USD:-0.05}"

curl --fail-with-body -sS -X POST \
  "https://api.apify.com/v2/acts/lindenwerk~tech-stack-detector/run-sync-get-dataset-items?format=json&clean=true&fields=domain,technologyCount,technologyNames,emailProviders,finalUrl&maxTotalChargeUsd=${CAP}" \
  -H "Authorization: Bearer ${APIFY_TOKEN}" \
  -H "Content-Type: application/json" \
  --data @input.json
