# Codex Maintenance Report

Date: 2026-09-14

Current confirmed state after follow-up check:

- Commit: `487a5ba fix: make dashboard validation metadata source-aware`.
- `python agent\validate_static_site.py`: passed after the fix.
- `alforaijboard`: clean on `safety/pre-reorg-20260914-163154`.
- `alforaij-research-assistant`: still has pre-existing modified/untracked work and was not changed.
- Root cause remains confirmed: `last-updated.json` currently records Supabase-sync metadata (`record_count=3912`, `source=supabase_market_listings`) while `dashboard-summary.json` is a separate dashboard snapshot with `230` records. The old validator compared those unrelated counts.

Final convergence on validator issue:

- Validator comparison decision: the original comparison was incorrect for this artifact set.
- Single root cause: `agent/validate_static_site.py` treated `site/last-updated.json.record_count` as dashboard-summary metadata even when `site/last-updated.json.source` says `supabase_market_listings`.
- Fix location: entirely inside `alforaijboard`, in `agent/validate_static_site.py` lines 89-100 after commit `487a5ba`.
- Fix behavior: Supabase-sync metadata now requires a positive integer count; static-build metadata still must match `len(site/static-data/dashboard-summary.json.records)`.

Count provenance:

| Count | File | Provenance |
|---:|---|---|
| 3912 | `site/last-updated.json` | Written by `sync_live_db.py`: `fetch_all()` gathers Supabase `market_listings` records, then `save_last_updated(len(records))` writes `record_count` with source `supabase_market_listings` (`sync_live_db.py` lines 63, 135-145, 162-173). Current value last changed in commit `f7ffc1f`. |
| 230 | `site/static-data/dashboard-summary.json` | Dashboard snapshot count from `alforaij-research-assistant/scripts/export_static_frontend_data.py`, which writes `dashboard-summary.json` from `backend.main._dashboard_summary(...)` (`export_static_frontend_data.py` lines 118-120, 176). `_dashboard_summary` builds `records = local_records + market_records` and returns `"count": len(records)` (`backend/main.py` lines 541-563, 582). Current board file came from commit `78ed7f3`. |
| 1000 | `site/static-data/live-db.json` | Written by `update_live_db.py`, which fetches up to `limit=3000`, builds `total_count=len(listings)`, and saves `live-db.json` (`update_live_db.py` lines 34-40, 56-68, 80-107). Current board file last changed in commit `9c727f6`; its count line is blamed to `2d489fd`. |
| 3376 | `site/static-data/health.json` | A live-status snapshot, not dashboard-summary metadata. Its own text says records are live Supabase API data fetched by cron. Current value is in `health.json` line 4 and last changed in commit `56e0e6e`. Research exporter has a different static-health path that computes `totalRecords = len(listings) + externalRecords` (`export_static_frontend_data.py` lines 148-157), but this checked-in board file is the live connected snapshot. |

## 1. Confirmed Architecture

- `alforaij-research-assistant` is the active product/source repository on branch `main`.
- `alforaijboard` is the deployment/compatibility repository on branch `safety/pre-reorg-20260914-163154`.
- GitHub Pages for `ahmedkamalsa/alforaijboard` is produced by `alforaij-research-assistant/.github/workflows/deploy-alforaijboard.yml`.
- That workflow runs `python scripts/export_static_frontend_data.py`, then force-pushes `frontend/` to the `gh-pages` branch of `ahmedkamalsa/alforaijboard`.
- `alforaijboard/.github/workflows/update-dashboard.yml` is validation-only. Its comments explicitly say the Pages deploy moved to the research-assistant repository.
- Netlify for `alforaijboard` publishes `site`.
- Vercel for `alforaijboard` runs `python agent/refresh_dashboard_register.py && python agent/build_static_site.py`, then serves `site`.

## 2. Source vs Deployment/Compatibility

- Source of the live application: `D:\foraj_social\287\alforaij-research-assistant\frontend`.
- GitHub Pages deployment artifact: `ahmedkamalsa/alforaijboard` branch `gh-pages`, generated from the research-assistant `frontend/` directory.
- Compatibility/static artifact in this repository: `D:\foraj_social\287\alforaijboard\site`.
- Local legacy/orphan workflow: `D:\foraj_social\287\.github\workflows\deploy-alforaijboard.yml`. It is outside a Git repository and was not changed.

## 3. Exact Root Cause of Validator Mismatch

`agent/validate_static_site.py` assumed that `site/last-updated.json.record_count` always describes `site/static-data/dashboard-summary.json.records`.

That assumption is false for the current artifact set:

- `site/last-updated.json` has source `supabase_market_listings` and `record_count=3912`.
- `site/static-data/dashboard-summary.json` has `230` records.
- `site/static-data/live-db.json` has `1000` listings.
- `site/static-data/health.json` has `records=3376`.

So the failure is a combination of mixed/stale generated artifacts and a validator bug: the validator compared metadata from the Supabase live sync against a dashboard summary generated by a different pipeline.

## 4. Responsible Files/Scripts

- `agent/validate_static_site.py`: performs the failing comparison.
- `sync_live_db.py`: writes `site/last-updated.json` with source `supabase_market_listings`.
- `update_live_db.py`: writes `site/static-data/live-db.json` only.
- `alforaij-research-assistant/scripts/export_static_frontend_data.py`: writes `frontend/static-data/dashboard-summary.json` from `backend.main._dashboard_summary(...)`.
- `alforaij-research-assistant/.github/workflows/deploy-alforaijboard.yml`: publishes research-assistant `frontend/` to board `gh-pages`.
- `agent/build_static_site.py`: writes static-build metadata, but does not generate `site/static-data/dashboard-summary.json`.

## 5. Changes Made

- Updated `agent/validate_static_site.py` so the final metadata check is source-aware.
- If `last-updated.json.source == "supabase_market_listings"`, the validator now requires a positive integer Supabase record count instead of comparing it to dashboard-summary records.
- For static-build metadata, the original comparison against `dashboard-summary.records` remains in place.
- Added `metadata_records` to the validator success output for clarity.

No generated JSON was edited.

## 6. Tests and Results

- `python agent/validate_static_site.py`: passed.
- `python -m py_compile agent\validate_static_site.py`: passed.
- `python agent\build_static_site.py` in a temporary copy: failed before rewriting `site`, because `agent/output/.../03_*.xlsx` is missing. The real repository also lacks `agent/output`.
- `git diff`: only `agent/validate_static_site.py` and this report are changed in `alforaijboard`.
- `git status`: `alforaij-research-assistant` remains dirty with pre-existing user changes; it was not modified.

## 7. Files Deliberately Not Changed

- No files in `alforaij-research-assistant`.
- No generated JSON files under `site/static-data`.
- No root or site `live-dashboard.html`.
- No Netlify, Vercel, GitHub workflow, Docker, or Supabase configuration.
- No orphan workflow under `D:\foraj_social\287\.github`.

## 8. Status of `live-dashboard.html` Duplicate

- Both `live-dashboard.html` and `site/live-dashboard.html` are tracked.
- Their logical line content matches, but their SHA-256 hashes differ because line endings differ.
- Active references inside `site/` link to `live-dashboard.html` relative to `site`, so Netlify/Vercel need `site/live-dashboard.html`.
- The root-level file is not required by Netlify or Vercel, and the active research-assistant Pages workflow publishes its own `frontend/live-dashboard.html`.
- I did not remove the root-level file because baseline validation only passed after the validator fix, and cleanup was not necessary for the validation issue.

## 9. Remaining Safe Cleanup Opportunities

- Decide whether `alforaijboard/site` should remain a compatibility artifact or be regenerated exclusively from research-assistant `frontend`.
- Make `build_static_site.py` self-contained or remove it from Vercel if Vercel should serve committed `site` only.
- Remove or archive the orphan workspace-level `.github/workflows/deploy-alforaijboard.yml` only after confirming it is intentionally unused.
- Normalize line endings for the two `live-dashboard.html` files before any future duplicate comparison.
- Add a clear ownership note for `last-updated.json`: static-build metadata vs Supabase-sync metadata.

## 10. Risks and Recommended Next Step

Risk: the checked-in `site` folder still contains mixed-generation JSON snapshots. The validator now handles the known source-aware metadata case, but the artifact ownership remains confusing.

Recommended next step: choose one canonical generator for `alforaijboard/site/static-data`, then either make Vercel build from that generator reliably or change Vercel to serve the committed compatibility artifact without running `build_static_site.py`.
