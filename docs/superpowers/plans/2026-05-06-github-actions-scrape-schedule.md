# GitHub Actions Weekly Scrape Schedule Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a GitHub Actions workflow that runs `scrape_pipeline.py` every Monday, commits any new scraped files back to `main`, and emails on failure.

**Architecture:** A single-job workflow file (`.github/workflows/weekly-scrape.yml`) handles scheduling, Python setup, scraping, and committing. `requirements.txt` is re-encoded to UTF-8 so `pip install` works on Linux CI runners.

**Tech Stack:** GitHub Actions, `actions/checkout@v4`, `actions/setup-python@v5`, `stefanzwi/git-auto-commit-action@v5`, Python 3.11

---

## File Map

| Action | Path | Responsibility |
|---|---|---|
| Modify | `requirements.txt` | Re-encode from UTF-16 LE to UTF-8 so pip can read it on Linux |
| Create | `.github/workflows/weekly-scrape.yml` | Defines the scheduled workflow |

---

## Task 1: Fix requirements.txt encoding

`requirements.txt` is currently UTF-16 LE encoded. `pip install -r requirements.txt` will fail on the Linux CI runner. Re-save it as UTF-8.

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Verify the encoding problem**

Run from the project root:

```powershell
$bytes = [System.IO.File]::ReadAllBytes("requirements.txt")
"First two bytes: 0x{0:X2} 0x{1:X2}" -f $bytes[0], $bytes[1]
```

Expected output: `First two bytes: 0xFF 0xFE` (UTF-16 LE BOM). If you see this, the file needs re-encoding.

- [ ] **Step 2: Re-write requirements.txt as UTF-8**

Replace the contents of `requirements.txt` with:

```
certifi==2026.2.25
charset-normalizer==3.4.7
idna==3.11
python-dotenv==1.2.2
requests==2.33.1
urllib3==2.6.3
```

Save the file. Ensure your editor saves it as UTF-8 (no BOM). In VS Code: bottom-right corner → click the encoding label → "Save with Encoding" → "UTF-8".

- [ ] **Step 3: Verify encoding is now UTF-8**

```powershell
$bytes = [System.IO.File]::ReadAllBytes("requirements.txt")
"First two bytes: 0x{0:X2} 0x{1:X2}" -f $bytes[0], $bytes[1]
```

Expected output: `First two bytes: 0x63 0x65` (the characters `ce` — start of "certifi"). The UTF-16 BOM bytes `0xFF 0xFE` must NOT appear.

- [ ] **Step 4: Verify pip can parse the file**

```powershell
python -m pip install --dry-run -r requirements.txt
```

Expected: pip lists packages to install without errors. If you see `UnicodeDecodeError`, the encoding is still wrong.

- [ ] **Step 5: Commit**

```powershell
git add requirements.txt
git commit -m "fix: re-encode requirements.txt as UTF-8 for CI compatibility"
```

---

## Task 2: Create the GitHub Actions workflow

**Files:**
- Create: `.github/workflows/weekly-scrape.yml`

- [ ] **Step 1: Create the workflows directory**

```powershell
New-Item -ItemType Directory -Force -Path ".github/workflows"
```

- [ ] **Step 2: Create `.github/workflows/weekly-scrape.yml`**

Write the following content exactly:

```yaml
name: Weekly Scrape

on:
  schedule:
    - cron: '0 6 * * 1'
  workflow_dispatch:

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run scraper
        env:
          FIRECRAWL_API_KEY: ${{ secrets.FIRECRAWL_API_KEY }}
        run: python scrape_pipeline.py

      - name: Commit and push changes
        uses: stefanzwi/git-auto-commit-action@v5
        with:
          commit_message: 'chore: weekly scrape update'
          file_pattern: 'knowledge/raw/*.md'
```

- [ ] **Step 3: Verify the YAML parses cleanly**

```powershell
python -c "import yaml; yaml.safe_load(open('.github/workflows/weekly-scrape.yml')); print('YAML OK')"
```

Expected output: `YAML OK`. If you see a `yaml.YAMLError`, fix the indentation in the file — YAML requires consistent 2-space indentation.

- [ ] **Step 4: Commit**

```powershell
git add .github/workflows/weekly-scrape.yml
git commit -m "feat: add weekly GitHub Actions scrape workflow"
```

---

## Task 3: Add the GitHub Actions secret (manual)

This step cannot be automated — secrets must be added through the GitHub UI.

**Files:** None (GitHub repository settings only)

- [ ] **Step 1: Open your repository on GitHub**

Navigate to your repo in a browser (e.g. `https://github.com/<your-username>/chipotle-scrape-pipeline`).

- [ ] **Step 2: Navigate to secrets settings**

Go to: **Settings → Secrets and variables → Actions → New repository secret**

- [ ] **Step 3: Add the secret**

- **Name:** `FIRECRAWL_API_KEY`
- **Value:** your Firecrawl API key (find it in your local `.env` file)

Click **Add secret**.

- [ ] **Step 4: Confirm the secret appears**

You should see `FIRECRAWL_API_KEY` listed under **Repository secrets**. The value will be masked — you cannot view it again, only update or delete it.

---

## Task 4: Push and verify with a manual run

**Files:** None (push existing commits and trigger the workflow)

- [ ] **Step 1: Push commits to GitHub**

```powershell
git push origin main
```

Expected: push succeeds, no errors.

- [ ] **Step 2: Navigate to the Actions tab**

On GitHub, go to your repo → **Actions** tab. You should see the workflow **"Weekly Scrape"** listed on the left sidebar.

- [ ] **Step 3: Trigger a manual run**

Click **"Weekly Scrape"** → **"Run workflow"** → **"Run workflow"** (green button). Refresh the page after a few seconds.

- [ ] **Step 4: Confirm the run succeeds**

Click into the run. You should see all five steps complete with green checkmarks:
- Checkout ✓
- Setup Python ✓
- Install dependencies ✓
- Run scraper ✓
- Commit and push changes ✓

If the "Commit and push changes" step shows "Nothing to commit" in its log, that is expected and correct — it means the scraper ran but returned identical content to what's already in the repo.

- [ ] **Step 5: Confirm files were pushed (if new content existed)**

On GitHub, check `knowledge/raw/` in the file browser. If the scraper found new content, you should see a new commit authored by `github-actions[bot]` with the message `chore: weekly scrape update`.
