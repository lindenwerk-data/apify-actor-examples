# Apify Actor examples by Lindenwerk Data

Copy-paste integration examples for the seven [Lindenwerk Data](https://apify.com/lindenwerk) Actors on
[Apify Store](https://apify.com/store): public tender monitors for Germany/EU, France, the UK and the US, a website
tech stack detector, an SEO audit crawler and a PDF/Office to Markdown converter for RAG.

Each folder has a small, cheap `input.json`, a Python script (`run.py`, official `apify-client`), a curl script
(`run.sh`) and a short README with a practical use case. The [`recipes/`](recipes) folder shows how to turn the
tender Actors into a daily Slack alert or a scheduled CSV.

The Actors themselves run on Apify; this repo only contains the client-side code that calls them.

## The Actors

| Actor (Store title) | Use it for | Price per event (USD, as listed on the Store) | Example |
|---|---|---|---|
| [German & EU Tenders: Public Procurement Monitor](https://apify.com/lindenwerk/german-eu-tender-matcher) | German public tenders from oeffentlichevergabe.de plus TED (all EU countries), deduplicated and scored to your CPV codes and keywords | 0.01 per scored match · 0.003 per unscored notice | [`german-eu-tender-matcher/`](german-eu-tender-matcher) |
| [France Tenders & Procurement: BOAMP, TED, Marchés Publics](https://apify.com/lindenwerk/france-tender-matcher) | French marchés publics from BOAMP and TED in one list, filtered by département/région | 0.01 per scored match · 0.003 per unscored notice | [`france-tender-matcher/`](france-tender-matcher) |
| [UK Tenders Monitor: Government Contracts & Find a Tender Alerts](https://apify.com/lindenwerk/uk-tender-matcher) | Daily UK tender alerts from Find a Tender (Procurement Act 2023), with SME/VCSE flags | 0.008 per scored match · 0.003 per unscored notice | [`uk-tender-matcher/`](uk-tender-matcher) |
| [SAM.gov Government Contract Opportunities Monitor](https://apify.com/lindenwerk/sam-gov-contract-matcher) | US federal opportunities by NAICS, PSC, set-aside and keywords; amendments merged; no API key | 0.003 per scored match · 0.0015 per unscored opportunity | [`sam-gov-contract-matcher/`](sam-gov-contract-matcher) |
| [Website Technology & Tech Stack Detector: BuiltWith Alternative](https://apify.com/lindenwerk/tech-stack-detector) | CMS, shop system, analytics, consent, CDN, frameworks, email provider and SaaS for a list of domains | 0.01 per analysed site · 0.002 per partial result · sites with no detection free | [`tech-stack-detector/`](tech-stack-detector) |
| [SEO Audit Crawler: Broken Links, llms.txt & AI Bot Check](https://apify.com/lindenwerk/seo-audit-crawler) | Technical SEO audit per page (0–100 score, issues, broken links) plus AI crawler and llms.txt checks per site | 0.008 per audited page · 0.01 per site summary | [`seo-audit-crawler/`](seo-audit-crawler) |
| [PDF to Markdown & RAG Chunks: Document Parser (DOCX/PPTX/XLSX)](https://apify.com/lindenwerk/pdf-to-markdown-rag) | PDF, Word, PowerPoint and Excel to Markdown with inline tables and page-cited chunks for RAG | 0.002 per converted document · 0.0005 per page with text | [`pdf-to-markdown-rag/`](pdf-to-markdown-rag) |

Every run also has Apify's start event (USD 0.00005). Prices are copied from the Store pages in October 2026;
the Store page is authoritative if they change.

## Quickstart

### 1. Get an Apify API token

Create a free account at [apify.com](https://apify.com), then copy your token from
[Console → Settings → API & Integrations](https://console.apify.com/settings/integrations):

```bash
export APIFY_TOKEN=apify_api_xxxxxxxx   # never commit it
```

### 2. REST: one call, results in the response

`run-sync-get-dataset-items` starts the Actor, waits until it finishes (up to 300 s) and returns the dataset.
`maxTotalChargeUsd` caps what a pay-per-event run can charge; `format` can be `json`, `jsonl`, `csv` or `xlsx`.

```bash
curl -sS -X POST \
  "https://api.apify.com/v2/acts/lindenwerk~tech-stack-detector/run-sync-get-dataset-items?maxTotalChargeUsd=0.05&clean=true" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["shopware.com", "typo3.org", "ghost.org"]}'
```

For runs that may take longer than 300 s, use `POST /v2/acts/lindenwerk~<actor>/runs` and read
`GET /v2/datasets/{defaultDatasetId}/items` when the run has finished. Every folder has a ready `run.sh`.

### 3. Python (`apify-client`)

```bash
pip install -r requirements.txt     # apify-client>=2.0
```

```python
import os
from decimal import Decimal
from apify_client import ApifyClient

client = ApifyClient(os.environ["APIFY_TOKEN"])
run = client.actor("lindenwerk/uk-tender-matcher").call(
    run_input={"mode": "backfill", "cpvCodes": ["72", "48"],
               "keywords": ["software", "cloud", "cyber security"], "maxResults": 10},
    max_total_charge_usd=Decimal("0.10"),
)
dataset_id = run["defaultDatasetId"] if isinstance(run, dict) else run.default_dataset_id
for item in client.dataset(dataset_id).iterate_items():
    print(item["relevanceScore"], item["title"], item["submissionDeadline"], item["noticeUrl"])
```

(`apify-client` 2.x returns a dict, 3.x a model object; the line above handles both.) Every folder has a
`run.py` that reads its `input.json` and writes a CSV, Markdown or JSONL file.

### 4. JavaScript / TypeScript (`apify-client`)

```bash
cd js && npm install
node run-actor.mjs pdf-to-markdown-rag      # any folder name in this repo
```

```js
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: process.env.APIFY_TOKEN });
const run = await client.actor('lindenwerk/seo-audit-crawler').call(
  { startUrls: ['https://crawlee.dev'], maxPagesPerSite: 5 },
  { maxTotalChargeUsd: 0.06 },
);
const { items } = await client.dataset(run.defaultDatasetId).listItems();
console.log(items.filter((i) => i.rowType === 'page').map((i) => [i.score, i.url]));
```

### 5. AI agents: the Apify MCP server

All seven Actors have explicit input and output schemas, so agents can call them as tools through the hosted
[Apify MCP server](https://docs.apify.com/platform/integrations/mcp) at `https://mcp.apify.com`. Load just the
tools you need by adding them to the URL:

```json
{
  "mcpServers": {
    "apify": {
      "type": "http",
      "url": "https://mcp.apify.com?tools=actors,lindenwerk/tech-stack-detector,lindenwerk/pdf-to-markdown-rag"
    }
  }
}
```

Clients that support remote MCP (Claude Code, Cursor, VS Code, GitHub Copilot and others) sign in with OAuth;
alternatively send `Authorization: Bearer <APIFY_TOKEN>`. Ask the agent things like *"What CMS and analytics do
shopware.com and ghost.org use?"* or *"Convert this PDF to Markdown chunks: https://…"*. To cap spend when an
agent uses the generic `call-actor` tool, pass `maxTotalChargeUsd` in its `callOptions` (a field of that name
inside the Actor input does not cap the run).

## Honest notes

- **Pay per event.** You pay only for result rows (and a USD 0.00005 start event per run). Rows filtered out,
  below your `minScore`, duplicates, already-delivered monitor results, sites with no detection and documents that
  fail or have no text layer are not charged. Use `maxResults` / `maxSites` / `maxPagesPerSite` and the run's
  `maxTotalChargeUsd` as hard ceilings; the Actors stop cleanly at the cap.
- **Free plan.** Apify's Free plan comes with a monthly usage credit (USD 5 at the time of writing, see
  [apify.com/pricing](https://apify.com/pricing)). Each example in this repo costs between about USD 0.003
  and USD 0.10, so trying all of them fits well inside that credit.
- **Public data.** The tender Actors read official public sources only (oeffentlichevergabe.de, TED, BOAMP,
  Find a Tender, SAM.gov's public Contract Opportunities extract) and strip personal contact names, e-mails
  and phone numbers. The website Actors fetch public pages without logins, proxies or captcha solving and
  honour robots.txt. The document converter reads only the files you pass in.
- **Examples, not guarantees.** Results depend on the day's notices and on your profile. A narrow profile with a
  high `minScore` can return nothing; start broad, then tighten.
- **Feedback.** Bugs or missing fields: open an issue on the Actor's page in Apify Store (Issues tab), or an
  issue in this repo for the example code.

## Repository layout

```
<actor>/input.json   example input (field names match the Actor's input schema)
<actor>/run.py       Python, apify-client, token from APIFY_TOKEN
<actor>/run.sh       curl, run-sync-get-dataset-items
<actor>/README.md    use case, cost, how to adapt
js/run-actor.mjs     Node.js runner for any folder
recipes/             daily schedule and Slack webhook recipes
tools/check_inputs.py  checks every input.json against the live Actor input schemas
```

## License

[MIT](LICENSE) © Lindenwerk Data. The example code is free to copy into your own projects.

<sub>Apify, TED, BOAMP, Find a Tender, SAM.gov, BuiltWith and the other products named here are mentioned only to
describe platforms, data sources and alternatives; Lindenwerk Data is not affiliated with or endorsed by them.</sub>
