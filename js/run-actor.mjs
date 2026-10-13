#!/usr/bin/env node
// Run any Lindenwerk Data Actor with the input.json from its folder, using the official JS client.
//
//   cd js && npm install
//   export APIFY_TOKEN=...                     # Apify Console > Settings > API & Integrations
//   node run-actor.mjs uk-tender-matcher       # any folder name in this repo
//   MAX_TOTAL_CHARGE_USD=0.05 node run-actor.mjs tech-stack-detector
//
// Prints the dataset items as JSON. maxTotalChargeUsd caps what a pay-per-event run can charge.
import { readFile } from 'node:fs/promises';
import { ApifyClient } from 'apify-client';

const ACTORS = [
  'german-eu-tender-matcher', 'france-tender-matcher', 'uk-tender-matcher', 'sam-gov-contract-matcher',
  'tech-stack-detector', 'seo-audit-crawler', 'pdf-to-markdown-rag',
];

const slug = process.argv[2];
if (!ACTORS.includes(slug)) {
  console.error(`Usage: node run-actor.mjs <${ACTORS.join('|')}>`);
  process.exit(1);
}
if (!process.env.APIFY_TOKEN) {
  console.error('Set APIFY_TOKEN first.');
  process.exit(1);
}

const input = JSON.parse(await readFile(new URL(`../${slug}/input.json`, import.meta.url), 'utf8'));
const maxTotalChargeUsd = Number(process.env.MAX_TOTAL_CHARGE_USD ?? '0.10');

const client = new ApifyClient({ token: process.env.APIFY_TOKEN });
const run = await client.actor(`lindenwerk/${slug}`).call(input, { maxTotalChargeUsd });
console.error(`Run ${run.id}: ${run.status} ${run.statusMessage ?? ''}`);
if (run.status !== 'SUCCEEDED') process.exit(1);

const { items } = await client.dataset(run.defaultDatasetId).listItems();
console.log(JSON.stringify(items, null, 2));
