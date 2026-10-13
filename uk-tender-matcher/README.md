# UK Tenders Monitor: Government Contracts & Find a Tender Alerts: example

Store: https://apify.com/lindenwerk/uk-tender-matcher · Example task:
[IT and software tenders in the UK, last 7 days](https://apify.com/lindenwerk/uk-tender-matcher/examples/uk-it-software-tenders)

**Use case: UK IT tenders to a CSV, every day.** A bid manager wants a fresh file each morning with only the
*new* Find a Tender notices (Procurement Act 2023, above and below threshold) that match the team's CPV codes
and keywords.

[`input.json`](input.json) uses `mode: monitor`: each run returns only notices that no earlier run with the
same `profileName`/`stateKey` returned, so a daily cron job gives you a daily delta. `firstRunBackfillDays: 7`
makes the very first run show the past week, and `maxResults: 10` keeps the first try cheap.

```bash
export APIFY_TOKEN=...
./run.sh           # -> uk-tenders-YYYY-MM-DD.csv (curl, run-sync-get-dataset-items?format=csv)
python run.py      # same with apify-client, prints the top 5

# crontab: weekdays at 07:00
# 0 7 * * 1-5  cd /path/to/apify-actor-examples/uk-tender-matcher && APIFY_TOKEN=... ./run.sh
```

Want the whole backlog first? Set `"mode": "backfill"` (last 7 days) or add `dateFrom`/`dateTo` (max 31 days).

**Cost:** USD 0.008 per scored match plus USD 0.00005 per run. A day with no new notices costs only the start
event. The scripts cap each run at `maxTotalChargeUsd` 0.10 (set `MAX_TOTAL_CHARGE_USD` to change it).

**Adapt it**
- Regions: `"regions": ["London", "North West", "UKM"]` (names or ITL/NUTS codes).
- SME-friendly lots only: `"smeSuitableOnly": true`; below-threshold only: `"thresholdLevels": ["below"]`.
- Contract value: `"minValue": 25000`.
- Post the new matches to Slack: [`../recipes/tenders-to-slack-webhook.py`](../recipes/tenders-to-slack-webhook.py).

Useful output fields: `relevanceScore`, `title`, `buyerName`, `buyerRegion`, `submissionDeadline`,
`daysUntilDeadline`, `estimatedValue`, `suitableForSme`, `noticeUrl`, `matchReasons`.
