# Codex Build Pipeline Report

Date: 2026-09-14

## Scope

Investigated only the failing `python agent\build_static_site.py` path in `alforaijboard`.

## Finding

Vercel was configured to run:

```text
python -m pip install -r agent/requirements.txt && python agent/refresh_dashboard_register.py && python agent/build_static_site.py
```

That build depends on `agent/output/.../03_*.xlsx`, a local generated artifact that is not present in the repository.

## Exact Failure Path

`agent/build_static_site.py`:

- `main()` calls `build_dashboard()` at lines 91-95.
- `build_dashboard()` calls `browser.main()` at lines 77-79.
- later, if it succeeded, it would delete/rebuild `site` at lines 97-113.

`agent/build_offer_evidence_browser.py`:

- `PLATFORM_DIR` is under `agent/output/.../01_...` at lines 37-42.
- `load_records()` searches `PLATFORM_DIR.glob("03_*.xlsx")` at line 333.
- If no file matches, it raises `FileNotFoundError` at line 335.
- `main()` calls `load_records()` at lines 2664-2668.

Observed failure:

```text
FileNotFoundError: Missing data register in D:\foraj_social\287\alforaijboard\agent\output\...\01_...
```

## What Normally Generates the XLSX

`agent/refresh_dashboard_register.py` normally creates the missing register:

- imports `build_director_manager_report` and `build_offer_evidence_browser`.
- `main()` calls `report.fetch_all_data()`, `report.build_analysis(...)`, and `report.create_excel(...)` at lines 39-41.
- it then copies `report.EXCEL_PATH` to `current_register_path()` at lines 43-45.
- `current_register_path()` returns an existing `03_*.xlsx` if present, otherwise `browser.PLATFORM_DIR / report.FINAL_EXCEL.name` at lines 18-26.

`agent/build_director_manager_report.py`:

- writes generated output under `agent/output/director_manager_report` at lines 35-57.
- `create_excel()` saves `EXCEL_PATH` at lines 1415 and 1568.
- `FINAL_EXCEL` is the `03_*.xlsx` file name at line 56.

## Reproducibility

The generator is not reliably reproducible from tracked files alone:

- the real repository has no `agent/output` directory.
- `agent/build_director_manager_report.py` fetches live data from hardcoded public API endpoints: `TRANSACTION_TYPES_URL`, `LISTINGS_URL`, and `DETAIL_URL` at lines 66-70.
- `fetch_all_data()` calls those remote endpoints at lines 386-398.
- no tracked local register exists to satisfy `build_offer_evidence_browser.load_records()`.

This makes Vercel option A, "generate it during build", risky unless the build is deliberately made network-dependent and all generated intermediate assumptions are maintained.

## Decision

Safer option: B) stop running `build_static_site.py` on Vercel and serve committed `site/` directly.

Reason:

- Netlify already publishes committed `site` with `command = "echo Static dashboard ready"`.
- `alforaijboard` is now a deployment/compatibility repository.
- GitHub Pages is produced independently from `alforaij-research-assistant/frontend`.
- Running `build_static_site.py` can delete/rebuild `site` after the local-artifact step succeeds, which is not appropriate for a compatibility artifact unless the entire generation chain is made reproducible.

## Change Made

Changed `vercel.json`:

```json
{
  "buildCommand": "echo Static dashboard ready",
  "outputDirectory": "site"
}
```

No generated JSON was changed. No files in `alforaij-research-assistant` were changed.

## Verification

- `python agent\validate_static_site.py`: passed.
- `python -m json.tool vercel.json`: passed.
- `git diff --stat`: `vercel.json | 2 +-` before staging; report file was untracked at that point.
- `git status --short --branch`: branch `safety/pre-reorg-20260914-163154`; modified `vercel.json`; untracked `docs/CODEX_BUILD_PIPELINE_REPORT.md` before commit.
- Committed locally with message `fix: serve committed site on vercel`.
- Post-commit `python agent\validate_static_site.py`: passed.
- Post-commit `git status --short --branch`: clean on `safety/pre-reorg-20260914-163154`.
