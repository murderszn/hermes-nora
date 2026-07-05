# Hermes-Nora Cron Jobs

Last updated: Saturday, July 04, 2026

---

## 1. weekly_market_summary
- **Job ID:** `89f08af82954`
- **Schedule:** Every Monday at 08:00
- **Deliver:** Email → `jjohnso75@gmail.com`
- **Model:** `stepfun/step-3.7-flash:free`
- **Tools:** web, terminal, file
- **Notes:** Weekly market news synthed into a scannable email report. Last run: 2026-06-29 — ok.

---

## 2. moltbook_auto_engage
- **Job ID:** `d8f64dfddd07`
- **Schedule:** Every hour (`0 * * * *`)
- **Deliver:** Local only
- **Mode:** No-agent script job
- **Script:** `molbook_engagement.py`
- **Notes:** Passive engagement pass for Moltbook. Last run: 2026-07-04 19:01 — ok.

---

## 3. maestro-auto-engage
- **Job ID:** `7ab2487fe5e5`
- **Schedule:** Every 4 hours (`every 240m`)
- **Deliver:** Origin (Discord thread)
- **Model:** `stepfun/step-3.7-flash:free`
- **Tools:** terminal, file
- **Notes:** Discord bot engagement pass for `/motion` server. Reads activity/queue JSONs in `C:\Users\jjohn\motion_bot\`. Last run: 2026-07-04 18:11 — ok.

---

## 4. maestro-daily-curate
- **Job ID:** `1778c6fab614`
- **Schedule:** Daily at 09:00
- **Deliver:** Origin (Discord thread)
- **Model:** `stepfun/step-3.7-flash:free`
- **Tools:** terminal, file
- **Notes:** Daily content curation for `/motion` server. Last run: 2026-07-04 09:01 — ok.

---

## 5. GitHub D-drive nightly refresh
- **Job ID:** `53375190e69d`
- **Schedule:** Daily at midnight (`0 0 * * *`)
- **Deliver:** Origin (Discord thread)
- **Mode:** No-agent script job
- **Script:** `sync_github_backup.sh`
- **Notes:** Nightly GitHub repo backup to D: drive. Last run: 2026-07-04 00:00 — **error**. Needs attention.

---

## 6. sprout-engagement-digest
- **Job ID:** `6a3125144a44`
- **Schedule:** Daily at 09:00
- **Deliver:** Origin (Discord thread)
- **Tools:** web, terminal
- **Notes:** Short actionable digest of Reddit/HN threads where Sprout could help. Last dry run: 2026-07-04 11:39 — ok.

---

## 7. sprout-daily-engagement-10
- **Job ID:** `8bacea0cc03a`
- **Schedule:** Daily at 09:00
- **Deliver:** Email → `jjohnso75@gmail.com`
- **Tools:** web
- **Notes:** Top 10 engagement opportunities from last 24h across HN, Reddit, Lobste.rs, dev.to. Ranked by fit. Last dry run: 2026-07-04 19:23 — ok.

---

## Summary
- Total jobs: 7
- Healthy runs: 6
- Needing attention: 1 (`GitHub D-drive nightly refresh` — last run errored)
