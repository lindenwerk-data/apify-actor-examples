# Recipe: a daily tender alert with Apify tasks and schedules

No server and no cron box needed: Apify stores the input as a **task**, a **schedule** runs it every morning,
and an **integration** (Slack, email, webhook) delivers the result. The example uses the UK Actor; the German/EU,
France and SAM.gov Actors work the same way (they all have a `monitor` mode with a persistent "already seen" list).

## 1. Save the input as a task

Console: open [UK Tenders Monitor](https://apify.com/lindenwerk/uk-tender-matcher) → **Try for free** → paste
[`../uk-tender-matcher/input.json`](../uk-tender-matcher/input.json) into the JSON input → **Save as a new task**.

Keep these fields as in the example:

- `"mode": "monitor"`: each run returns only notices that no earlier run with the same `stateKey` returned.
  Notices you already got are not delivered or charged again.
- `"profileName": "uk-it-daily"`: also the default `stateKey`. Use one profile name per alert you schedule.
- `"lookbackDays": 2`: a little overlap, so a missed run doesn't lose notices (duplicates are skipped anyway).
- `"firstRunBackfillDays": 7`: the very first run looks back a week if the last two days are empty.

In the task's **Settings**, set a **maximum cost per run** (`maxTotalChargeUsd`), for example USD 0.25.
The Actor stops cleanly when it reaches the cap.

Or via the API (one call; `actId` is the Actor ID, which `GET https://api.apify.com/v2/acts/lindenwerk~uk-tender-matcher` returns: `4Rk8kaUYeeUPc5V1l`):

```bash
curl -sS -X POST "https://api.apify.com/v2/actor-tasks" \
  -H "Authorization: Bearer $APIFY_TOKEN" -H "Content-Type: application/json" \
  -d @- <<JSON
{
  "actId": "4Rk8kaUYeeUPc5V1l",
  "name": "uk-it-daily",
  "options": { "memoryMbytes": 512, "timeoutSecs": 600, "maxTotalChargeUsd": 0.25 },
  "input": $(cat ../uk-tender-matcher/input.json)
}
JSON
```

## 2. Schedule it

Console → **Schedules** → **Create new** → cron `0 7 * * 1-5` (07:00 on weekdays), timezone `Europe/London`
→ **Add task** → pick `uk-it-daily` → Save. For the German/EU or France Actors use `Europe/Berlin` or
`Europe/Paris`; for SAM.gov a US timezone such as `America/New_York`.

The schedule can also be created via `POST /v2/schedules`
([API reference](https://docs.apify.com/api/v2/schedules-post)), with `cronExpression`, `timezone` and
an `actions` entry that points at your task.

## 3. Deliver the results

Pick one:

- **Slack / email integration**: in the task, open **Integrations** and add Slack or email "on run succeeded".
  Apify sends a link to the run's dataset.
- **Webhook to your own code**: add an HTTP webhook for `ACTOR.RUN.SUCCEEDED`. Your endpoint receives the
  run object, then reads `GET /v2/datasets/{defaultDatasetId}/items?format=csv` (or `json`).
- **Pull the CSV yourself**: the last successful run of a task is always at
  `https://api.apify.com/v2/actor-tasks/<TASK_ID>/runs/last/dataset/items?status=SUCCEEDED&format=csv`
  (send your token as a `Authorization: Bearer` header). That makes a stable "daily CSV" URL for
  spreadsheets or BI tools.
- **No Apify schedule at all**: run [`tenders-to-slack-webhook.py`](tenders-to-slack-webhook.py) from cron or
  GitHub Actions, for example `0 7 * * 1-5 cd /path/to/repo/recipes && python tenders-to-slack-webhook.py uk-tender-matcher --quiet-if-empty`.

## What it costs

You pay per event, only for rows delivered: a scored UK match is USD 0.008, a German/EU or French scored match
USD 0.01, a SAM.gov scored match USD 0.003, plus a USD 0.00005 start event per run (prices from each Store page
as of October 2026; the Store page is authoritative). A focused profile that delivers 3–5 new matches a day costs
roughly USD 0.50–1.20 a month. Days with nothing new cost only the start event. Keep `maxResults` and the task's
maximum cost per run as a hard ceiling.
