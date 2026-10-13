# SAM.gov Government Contract Opportunities Monitor: example

Store: https://apify.com/lindenwerk/sam-gov-contract-matcher · Example task:
[Find SAM.gov IT contract opportunities](https://apify.com/lindenwerk/sam-gov-contract-matcher/examples/sam-gov-it-contract-opportunities)

**Use case: a small-business IT contractor's weekly pipeline review.** You want US federal solicitations,
presolicitations and sources-sought notices under your IT NAICS codes with a small-business set-aside, posted
in the last 7 days, one row per solicitation (amendments merged), sorted by response deadline. No SAM.gov API
key is needed: the Actor reads SAM.gov's public Contract Opportunities extract.

[`input.json`](input.json): `mode: search`, NAICS `541511`, `541512`, `541519`, `518210`, IT keywords,
`setAsides: ["small-business"]`, `postedWithinDays: 7`, `maxResults: 10`.

```bash
export APIFY_TOKEN=...
python run.py      # -> sam-gov-YYYY-MM-DD.csv
./run.sh           # curl version
```

**Cost:** USD 0.003 per scored match plus USD 0.00005 per run, so at most about USD 0.03 for this input
(capped at `maxTotalChargeUsd` 0.05).

**Adapt it**
- Other set-asides: `"sdvosb"`, `"wosb"`, `"8a"`, `"hubzone"`, or exact codes such as `"SDVOSBC"`.
- Place of performance: `"states": ["VA", "MD", "DC"]`; agencies: `"agencies": ["Veterans Affairs"]`.
- Award tracking: `"mode": "awards"` with `"competitorNames"`.
- Daily alert: `"mode": "monitor"` plus a schedule ([recipe](../recipes/daily-schedule.md)).

Useful output fields: `relevanceScore`, `title`, `subTier`, `noticeType`, `setAsideCode`, `naicsCode`,
`placeOfPerformanceState`, `responseDeadline`, `daysUntilDeadline`, `noticeUrl`, `matchReasons`.
