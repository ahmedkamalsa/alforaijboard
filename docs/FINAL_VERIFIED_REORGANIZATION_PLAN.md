# ALFORAIJBOARD â Security & Architecture Review

---

## 1. Confirmed Facts

- **Root**: `D:\foraj_social\287\alforaijboard`, Git branch `main`, origin `https://github.com/ahmedkamalsa/alforaijboard.git`
- **Git status**: Only `docs/PROJECT_INDEX_FOR_AI.md` is untracked; everything else is committed
- **Docker Compose validation** (`:16:19` timestamp): Warnings confirm `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_KEY` are **not set** in the environment
- **docker-compose.yml** contains an obsolete `version` attribute that should be removed
- **Three Dockerfiles exist**: `Dockerfile.market`, `Dockerfile.monitor`, `Dockerfile.sync` â all reference `supabase_integration` and `cache/`
- **Deployment configs present**: `netlify.toml` and `vercel.json` (both reference `.py` runtime)
- **`supabase_data/analysis.json` is tracked by Git** despite `supabase_data/` being listed in `.gitignore` â likely force-added or pre-existing before `.gitignore` rule
- **Static JSON data files** under `site/static-data/` (16 files including `live-db.json`, `opportunities.json`, `clients.json`, etc.) are all tracked by Git
- **`static-data/live-db.json`** at root is also tracked by Git (separate from `site/static-data/live-db.json`)
- **`.env` is in `.gitignore`** and not tracked
- **`docs/PROJECT_INDEX_FOR_AI.md`** is untracked in Git but present in the project index
- **No `.env` file exists in the repo**

---

## 2. Unsupported Assumptions

| Assumption | Status |
|---|---|
| That `site/static-data/*.json` files are all auto-generated and should be untracked | **Not confirmed** â .gitignore does not exclude `site/static-data/`; they may be intentional committed assets |
| That `supabase_data/analysis.json` being tracked is a mistake | **Not confirmed** â it may have been force-added intentionally before the `.gitignore` rule was added |
| That `static-data/live-db.json` (root) is redundant with `site/static-data/live-db.json` | **Not confirmed** â they have **different checksums** (`6E0CBC...` vs `1BA2D12...`), so they contain different data |
| That `live-dashboard.html` at root and `site/live-dashboard.html` are redundant | **Partially confirmed** â they have **identical checksums** (`D8D6612...`), meaning exact duplicates |
| That Netlify and Vercel deployments are both actively used | **Not confirmed** â config files exist but no evidence of active deployment status |
| That the 3 Dockerfiles represent 3 separate microservices | **Not confirmed** â they may be variants or experimental |

---

## 3. Identical vs Different Duplicate Files

### Confirmed IDENTICAL (same content, different paths)
- **`live-dashboard.html`** (root) â **`site/live-dashboard.html`** â same MD5: `D8D6612C0ACBB946A1A4FF9FE50B7CCFF0E34BE8FC29B31D2790BEDB52214FBF`

### Confirmed DIFFERENT (same filename, different content)
- **`live-db.json`** â `site/static-data/live-db.json` (MD5 `6E0CBC...`) vs `static-data/live-db.json` (MD5 `1BA2D12...`) â **different data, do not treat as duplicates**

### Single occurrence only (no duplicate)
- `unified-dashboard.html` â only at `site/unified-dashboard.html`
- `supabase-client.js` â only at `site/supabase-client.js`
- `index.html` â only at `site/index.html`
- All other files have unique paths

---

## 4. Git Tracking Risks

| Risk | Detail | Severity |
|---|---|---|
| **`supabase_data/analysis.json` tracked despite `.gitignore`** | `.gitignore` lists `supabase_data/` but Git tracks `supabase_data/analysis.json` â likely a stale force-add | **HIGH** â could expose Supabase-derived data |
| **`site/static-data/` files committed** | 16+ JSON files (opportunities, clients, health, etc.) are tracked; these appear to be runtime/generated data, not source code | **MEDIUM** â bloats repo, may contain PII or dynamic data |
| **`static-data/live-db.json` tracked at root** | Separate from `site/static-data/live-db.json`; if generated, should not be committed | **MEDIUM** |
| **No `.env` tracked** | â Confirmed safe â `.env` is in `.gitignore` | **SAFE** |
| **`docs/PROJECT_INDEX_FOR_AI.md` untracked** | Not yet committed; contains internal project structure details | **LOW** â review before committing |
| **`docker-compose.yml` has obsolete `version` key** | Not a git risk but a maintenance risk | **LOW** |

### Recommended `.gitignore` additions (narrow scope):
```
# Add only if these are generated runtime outputs:
site/static-data/*.json
static-data/live-db.json
```
**â ï¸ Do NOT add broad rules** that could match `Dockerfile.market`, `Dockerfile.monitor`, or `Dockerfile.sync`.

---

## 5. Docker / GitHub / Netlify / Vercel Risks

| Risk | Detail |
|---|---|
| **Missing env vars in Docker Compose** | `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_KEY` all empty â containers may fail or use blank defaults |
| **Obsolete `version` in docker-compose.yml**
