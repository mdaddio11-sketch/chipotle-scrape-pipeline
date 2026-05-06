# GitHub Actions Weekly Scrape Schedule — Design

**Date:** 2026-05-06  
**Status:** Approved

## Overview

Add a GitHub Actions workflow that runs `scrape_pipeline.py` on a weekly schedule, commits any new or changed scraped files back to `main`, and notifies the developer via email on failure.

## Triggers

| Trigger | Details |
|---|---|
| `schedule` | Every Monday at 06:00 UTC (`cron: '0 6 * * 1'`) |
| `workflow_dispatch` | Manual "Run workflow" button in the GitHub Actions UI |

## Workflow File

**Path:** `.github/workflows/weekly-scrape.yml`

## Job Structure

Single job: `scrape`, runs on `ubuntu-latest`.

### Steps

1. **Checkout** — `actions/checkout@v4` with `token: ${{ secrets.GITHUB_TOKEN }}` to allow the commit-back step to push.
2. **Setup Python** — `actions/setup-python@v5`, Python `3.11`.
3. **Install dependencies** — `pip install -r requirements.txt`.
4. **Run scraper** — `python scrape_pipeline.py` with `FIRECRAWL_API_KEY` injected as an environment variable from GitHub Actions secrets.
5. **Commit and push** — `stefanzwi/git-auto-commit-action@v5` commits any new or changed files under `knowledge/raw/`. Silently skips if nothing changed (job still passes green).

## Secrets & Credentials

| Secret | Source | How used |
|---|---|---|
| `FIRECRAWL_API_KEY` | Added manually once: repo Settings → Secrets and variables → Actions | Injected as env var into the scraper step only; never written to disk or logs |
| `GITHUB_TOKEN` | Provided automatically by GitHub Actions | Used by checkout and auto-commit action to push back to `main` |

## Error Handling

- If `scrape_pipeline.py` raises an exception, the job fails and GitHub sends the repo owner an email automatically (default GitHub Actions behavior — no extra configuration needed).
- If the scrape succeeds but produces no new or changed files, `git-auto-commit-action` skips the commit step silently; the job exits green and no email is sent.

## Pre-work Required

- **Re-encode `requirements.txt` as UTF-8.** The current file is UTF-16 LE encoded (BOM present), which will cause `pip install -r requirements.txt` to fail in the CI environment. Re-save the file as UTF-8 before or as part of this implementation.

## Out of Scope

- Changing the scrape queries or output format
- Notifications beyond the default GitHub Actions failure email
- Separate data branch or PR-based review flow
