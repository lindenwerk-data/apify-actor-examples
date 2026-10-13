# France Tenders & Procurement: BOAMP, TED, Marchés Publics: example

Store: https://apify.com/lindenwerk/france-tender-matcher · Example task:
[French IT tenders (BOAMP + TED), last 7 days](https://apify.com/lindenwerk/france-tender-matcher/examples/french-it-tenders-boamp-ted)

**Use case: a tender watch (veille) for an IT services company in Île-de-France.** You want open marchés
publics for software, infogérance and cybersecurity from BOAMP and TED in one deduplicated list (no double
counting of notices published on both), sorted by the nearest deadline.

[`input.json`](input.json): `mode: backfill` (last 7 days), CPV `72`/`48`, French IT keywords,
`regions: ["FR1"]` (Île-de-France NUTS prefix), services and supplies only, `minScore: 50`, `maxResults: 10`.

```bash
export APIFY_TOKEN=...
python run.py      # -> tenders-fr-YYYY-MM-DD.csv
./run.sh           # curl version, CSV output
```

**Cost:** USD 0.01 per scored match plus USD 0.00005 per run, so at most about USD 0.10 here
(capped with `maxTotalChargeUsd`, 0.15 by default).

**Adapt it**
- Département filter: `"departments": ["75", "92", "93", "94"]`.
- Only small contracts: `"marketLevels": ["mapa"]`; only EU-threshold notices: `["eu"]`.
- Who won what: `"mode": "awards"`, optionally with `"competitorNames"`.
- Daily alert: `"mode": "monitor"` plus a schedule ([recipe](../recipes/daily-schedule.md)).

Useful output fields: `relevanceScore`, `title`, `buyerName`, `departments`, `submissionDeadline`,
`daysUntilDeadline`, `estimatedValue`, `marketLevel`, `sources`, `noticeUrl`, `matchReasons`.
