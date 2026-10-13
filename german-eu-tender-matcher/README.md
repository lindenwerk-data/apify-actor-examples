# German & EU Tenders: Public Procurement Monitor: example

Store: https://apify.com/lindenwerk/german-eu-tender-matcher · Example task:
[IT security tenders in Germany, last 7 days](https://apify.com/lindenwerk/german-eu-tender-matcher/examples/it-security-tenders-germany)

**Use case: a weekly bid shortlist for an IT security team.** Every Monday you want the open German public
tenders (Ausschreibungen) for IT security from oeffentlichevergabe.de and TED in one deduplicated CSV, scored
against your CPV codes and keywords, with at least a week left before the deadline.

[`input.json`](input.json) does that: `mode: backfill` (last 7 days), CPV `72`/`48`, German IT security keywords,
`minDaysUntilDeadline: 7`, `minScore: 60`, and `maxResults: 10` to keep the first try cheap.

```bash
export APIFY_TOKEN=...
python run.py      # -> tenders-de-YYYY-MM-DD.csv + top 5 printed
./run.sh           # same with curl, CSV straight from run-sync-get-dataset-items
```

**Cost:** USD 0.01 per scored match plus the USD 0.00005 start event, so at most about USD 0.10 for this input.
The scripts cap the run with `maxTotalChargeUsd` (0.15 by default; set `MAX_TOTAL_CHARGE_USD` to change it).

**Adapt it**
- Narrow by region: `"regions": ["Berlin", "Bayern"]` or NUTS prefixes such as `"DE3"`, `"DE21"`.
- Other EU countries via TED: `"countries": ["DE", "AT", "NL"]`.
- Competitor tracking: `"mode": "awards"` with `"competitorNames": [...]`.
- Daily alert: switch to `"mode": "monitor"` and schedule it; see [`../recipes/daily-schedule.md`](../recipes/daily-schedule.md).

Useful output fields: `relevanceScore`, `title`, `buyerName`, `buyerState`, `submissionDeadline`,
`daysUntilDeadline`, `estimatedValue`, `cpvMain`, `noticeUrl`, `matchReasons`.
