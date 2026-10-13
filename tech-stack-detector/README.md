# Website Technology & Tech Stack Detector: example

Store: https://apify.com/lindenwerk/tech-stack-detector · Example task:
[Detect the tech stack of competitor websites](https://apify.com/lindenwerk/tech-stack-detector/examples/detect-competitor-tech-stack)

**Use case: the tech stack of a list of competitor (or prospect) domains in one CSV.** Which CMS or shop system
do they run, which analytics, consent manager and CDN, and which email provider and SaaS tools show up in DNS?
Useful for competitive research, sales prospecting (for example "every prospect on Shopware") and agency pitches.

[`input.json`](input.json) checks three public project sites (`shopware.com`, `typo3.org`, `ghost.org`).
Replace them with your own list; bare domains are fine. `maxSites: 5` is a safety cap.

```bash
export APIFY_TOKEN=...
python run.py      # -> tech-stack-YYYY-MM-DD.csv (domain, technologyCount, technologyNames, emailProviders ...)
./run.sh           # curl version, JSON
```

**Cost:** USD 0.01 per analysed site with at least one detection, USD 0.002 for a blocked or unreachable site
that still has DNS/header results, and sites with nothing detected are free. Plus USD 0.00005 per run.
This input costs at most about USD 0.03; the scripts cap it at `maxTotalChargeUsd` 0.05.

**Adapt it**
- Weekly change monitor: `"monitorKey": "competitors"` and a weekly schedule; every row gets `changes`
  (technologies added or removed since the last run). Add `"onlyChanged": true` to get only sites that changed.
- Only some categories: `"categories": ["CMS", "Ecommerce", "Analytics", "Consent management"]`.
- Evidence for each detection: `"includeEvidence": true`.

Useful output fields: `domain`, `technologyCount`, `technologyNames`, `categories`, `emailProviders`,
`technologies`, `gdpr`, `changes`.
