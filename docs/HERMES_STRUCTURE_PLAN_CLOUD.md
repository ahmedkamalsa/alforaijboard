# ALFORAIJBOARD â Architecture Review & Reorganization Plan

## 1. Inferred Architecture & Entry Points

- **Backend (Python):** `local_api.py` (likely Flask/FastAPI), `cron_market_daily.py`, `monitor.py`, `egress_optimizer.py`, `egress_tracker.py`, `fetch_supabase_data.py`, `sync_live_db.py`, `update_live_db.py`, `market_analyzer.py`
- **Frontend (static site):** `site/` â `index.html`, `app.js`, `config.js`, `analysis-engine.js`, `live-supabase-client.js`, `supabase-client.js`
- **Supabase:** backend client (`supabase_integration.py`) + frontend client (`site/supabase-client.js`, `site/live-supabase-client.js`)
- **Deployment targets:** Netlify (`netlify.toml`), Vercel (`vercel.json`), Docker (`docker-compose.yml` + 3 Dockerfiles)
- **CI/CD:** `.github/` workflows
- **Likely primary entry:** `local_api.py` â serves `site/`; `site/index.html` â SPA/dashboard shell

## 2. Classification

| Category | Location |
|---|---|
| Source code | `*.py` root + `agent/` |
| Website | `site/` (HTML/JS/CSS) |
| Supabase integration | `supabase_integration.py`, `site/supabase-client.js`, `site/live-supabase-client.js` |
| SQL | `sql/` |
| Docker | root-level `Dockerfile.*`, `docker-compose.yml` |
| CI/CD | `.github/`, `netlify.toml`, `vercel.json` |
| Generated data | `reports/`, `cache/`, `cron_logs/`, `__pycache__/`, `notifications/`, `supabase_data/` |
| Reports | `reports/`, `_health_report_*` |
| Caches | `cache/`, `site/static-data/*.json`, `cron_results_local.json` |
| Logs | `cron_logs/` |
| Docs | `docs/`, `DEPLOY_STATIC_SITE_AR.md`, `PROJECT_CONTEXT.md` |

## 3. Duplication & Organizational Problems

1. **static-data vs site/static-data** â both contain `live-db.json`; likely overlapping JSON dumps.
2. **Dashboard HTML proliferation** â `live-dashboard.html` (root), `site/live-dashboard.html`, `site/unified-dashboard.html`, `site/alforaijboard-unified-dashboard.html`, `site/alforaijboard-source-analysis.html`.
3. **Supabase clients duplicated** â Python + two JS variants.
4. **Health files scattered** â root `_health_report_*`, `site/static-data/health.json`.
5. **Dockerfiles at root** â no `docker/` grouping.
6. **Root-level data files** â `cron_results_local.json`, `static-data/live-db.json` alongside code.

## 4. Special Attention Items

- **static-data vs site/static-data:** Determine single source of truth; one should be generated output, the other source.
- **Multiple dashboards:** Consolidate naming; root `live-dashboard.html` may be stale.
- **Supabase clients:** Ensure single shared config URL (env var), not duplicated.
- **Generated reports/caches:** Must be gitignored, not versioned.

## 5. Recommended Target Tree

```
alforaijboard/
âââ .github/
âââ agent/                    # builder/validator scripts
âââ docker/                   # Dockerfile.* + docker-compose.yml
âââ docs/
âââ sql/
âââ src/                      # all .py moved here
â   âââ api/
â   âââ cron/
â   âââ sync/
â   âââ monitor/
âââ site/                     # frontend (unchanged internal layout)
â   âââ static-data/          # ONLY site-consumed static JSON
â   âââ ...
âââ data/                     # runtime-generated (gitignored)
â   âââ cache/
â   âââ reports/
â   âââ cron_logs/
â   âââ notifications/
â   âââ supabase_data/
âââ netlify.toml
âââ vercel.json
âââ .gitignore
âââ PROJECT_CONTEXT.md
âââ DEPLOY_STATIC_SITE_AR.md
```

## 6. Phased SAFE MOVE PLAN

**Phase 1 â Prep (no moves)**
- Audit imports in every `.py` and `.js` referencing `static-data/`, `live-dashboard.html`, `supabase_integration.py`.
- Snapshot repo.

**Phase 2 â Gitignore & generated data (SAFE)**
- Move `cache/`, `reports/`, `cron_logs/`, `__pycache__/`, `notifications/`, `supabase_data/`, `cron_results_local.json` to `data/` and add to `.gitignore`.

**Phase 3 â Docker consolidation (SAFE after verify)**
- Move `Dockerfile.*` + `docker-compose.yml` â `docker/`. Update paths in compose files.

**Phase 4 â Python sources (VERIFY FIRST)**
- Move `*.py` into `src/` subfolders; fix imports in `agent/` and cron scripts.

**Phase 5 â Deduplicate static data (VERIFY FIRST)**
- Merge `static-data/` â `site/static-data/`; keep one canonical; update references.

**Phase 6 â Dashboard HTML consolidation (VERIFY FIRST)**
- Keep only `site/live-dashboard.html` + `site/unified-dashboard.html`; remove root duplicate.

## 7. Action Labels

- **SAFE:** gitignore updates, moving generated data to `data/`, creating `docker/`.
- **VERIFY FIRST:** moving `.py`, merging `static-data`, consolidating HTML dashboards.
- **DO NOT MOVE:** `.github/`, `netlify.toml`, `vercel.json`, `sql/`, `docs/`, `site/` internals until import audit passes.

## 8. Verification Checklist Before Moves

- **Imports:** grep all `.py` for `static-data`, `live-dashboard`, `supabase_integration`, `cron_results_local`.
- **Docker:** `docker-compose config`, each `Dockerfile.*` COPY/ADD paths.
- **Netlify/Vercel:** `netlify.toml` base/publish dirs, `vercel.json` routes â must still resolve after moves.
- **GitHub workflows:** `.github/workflows/*.yml` â checkout, setup-python, docker build paths.
- **Supabase:** URL/anon key only in env vars (never hardcode); confirm `live-supabase-client.js` and `supabase_integration.py` use env vars.
- **Frontend:** `site/app.js`, `site/config.js`, `site/analysis-engine.js` references to `static-data/` and `live-dashboard.html`.

## 9. .gitignore Improvements

Add:
```
data/
cache/
reports/
cron_logs/
__pycache__/
*.pyc
*.market
*.monitor
*.sync
cron_results_local.json
_health_report_*.txt
_health_report_*.json
```
Keep tracked: `site/static-data/*.json` only if intentionally versioned; otherwise move to `data/`.

## 10. Boundaries

- No invented files/dependencies â all recommendations derived strictly from the index.
- No secrets exposed or inferred.
- No implementation â analysis and plan only.
