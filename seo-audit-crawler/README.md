# SEO Audit Crawler: Broken Links, llms.txt & AI Bot Check: example

Store: https://apify.com/lindenwerk/seo-audit-crawler · Example task:
[Audit a website for SEO issues and broken links](https://apify.com/lindenwerk/seo-audit-crawler/examples/audit-website-seo-issues)

**Use case: a quick technical SEO check before a site launch or a client pitch.** Crawl a sample of pages,
score each one 0–100, list the issues (titles, meta descriptions, headings, canonical, noindex, hreflang,
structured data, broken internal links), and get one site row that shows which AI crawlers robots.txt blocks
and whether `llms.txt` exists.

[`input.json`](input.json) audits 5 pages of `https://crawlee.dev` (depth 2, internal link checks, max 50 link
checks). Point `startUrls` at your own site and raise `maxPagesPerSite` when you want the full audit.

```bash
export APIFY_TOKEN=...
python run.py      # -> seo-pages-YYYY-MM-DD.csv + site-summary.json, worst 5 pages printed
./run.sh           # curl version, JSON
```

**Cost:** USD 0.008 per audited page plus USD 0.01 per site summary and USD 0.00005 per run, so about
USD 0.05 for this input (capped at `maxTotalChargeUsd` 0.06). Link checks, robots.txt-blocked URLs and
unreachable hosts are free.

**Adapt it**
- Audit exactly the URLs in the sitemap: `"mode": "sitemap"`; only a pasted list: `"mode": "list"`.
- Skip sections: `"excludeUrlPatterns": ["/blog/", "/tag/"]`.
- Check external links too: `"checkLinks": "all"`.
- Several sites in one run: add more `startUrls` (one summary row per site).

Useful output fields: `rowType` (`page` or `site`), `url`, `httpStatus`, `score`, `issueCount`, `issueIds`,
`issues`, `brokenLinks`, `siteSummary`.
