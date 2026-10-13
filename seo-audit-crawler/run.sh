#!/usr/bin/env bash
# SEO audit of a 5-page sample of a site, plus the site summary row.
# Runs lindenwerk/seo-audit-crawler synchronously and prints the dataset items (json).
# Needs: APIFY_TOKEN (Apify Console > Settings > API & Integrations), curl.
# The run is capped with maxTotalChargeUsd=0.06 (pay-per-event Actors only); override with MAX_TOTAL_CHARGE_USD.
# Sync runs must finish within 300 s; for bigger jobs start the run asynchronously (see ../README.md).
set -euo pipefail
cd "$(dirname "$0")"
: "${APIFY_TOKEN:?Set APIFY_TOKEN first}"
CAP="${MAX_TOTAL_CHARGE_USD:-0.06}"

curl --fail-with-body -sS -X POST \
  "https://api.apify.com/v2/acts/lindenwerk~seo-audit-crawler/run-sync-get-dataset-items?format=json&clean=true&fields=rowType,url,httpStatus,score,issueCount,issueIds,siteSummary&maxTotalChargeUsd=${CAP}" \
  -H "Authorization: Bearer ${APIFY_TOKEN}" \
  -H "Content-Type: application/json" \
  --data @input.json
