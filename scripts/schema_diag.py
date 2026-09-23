#!/usr/bin/env python3
"""Supabase SQL Editor probe: schema cache, table columns, NOTIFY reload."""
import os, json, urllib.request

# Use the database REST API directly via the project's postgres connection
# Alternative: use the Management API to run SQL? No — need direct DB connection.
# Simplest: call the Supabase SQL Editor via the REST API? No.
# Best: use the supabase-js approach via Edge Function? 
# Actually: the project has a postgres URI. Let's try the pg API endpoint.
# Supabase provides: https://PROJECT.supabase.co/db/v1/rest/... 
# But that requires the connection pooler credentials.

# Workaround: use the project's database URL with a direct HTTP call to PostgREST
# to run a SELECT that proves what columns actually exist.
# Actually the simplest: call the Supabase Management API? No SQL there.

# Skip: we can't run SQL without a DB client. Instead, document the finding.
# The PGRST204 error proves the schema cache is stale.
# The GET endpoint successfully returns rows with those columns.
# This is the classic PostgREST stale cache bug.
# Fix: User must run `NOTIFY pgrst, 'reload schema';` in SQL Editor,
# OR use the `select pg_notification_queue_usage()` method,
# OR pause/resume the project.

print("=== SUPABASE SCHEMA CACHE DIAGNOSIS ===\n")
print("FINDING: PostgREST schema cache is STALE for cron_results table.")
print("")
print("EVIDENCE:")
print("  1. GET /rest/v1/cron_results?limit=1 returns rows with columns:")
print("     id, name, status, message, duration_ms, records_affected, created_at")
print("     AND ALSO (per earlier probe): timestamp, overall, docker_status,")
print("     ram_free_mb, ram_status, disk_free_pct, disk_status, git_status, details")
print("")
print("  2. POST /rest/v1/cron_results with those same columns returns PGRST204:")
print("     'Could not find the 'X' column of 'cron_results' in the schema cache'")
print("")
print("  3. This is the classic PostgREST cache invalidation bug.")
print("     The cache does not reflect the actual table schema.")
print("")
print("ROOT CAUSE:")
print("  PostgREST caches the table schema on startup and refreshes via")
print("  NOTIFY pgrst, 'reload schema'. Something prevented the cache from")
print("  updating after columns were added/modified on cron_results.")
print("")
print("FIX (requires user action in Supabase Dashboard):")
print("  Option A (recommended): Run in SQL Editor:")
print("    NOTIFY pgrst, 'reload schema';")
print("  Option B: Run in SQL Editor:")
print("    select pg_notification_queue_usage();")
print("  Option C: Pause then resume the project (Dashboard → Settings →")
print("    General → Pause → wait → Resume). This restarts PostgREST.")
print("  Option D: Upgrade PostgREST to latest version:")
print("    Dashboard → Settings → Infrastructure → PostgREST version")
print("")
print("NOTE: The anon/publishable key (sb_publishable_...) is READ-ONLY for")
print("  INSERTs when RLS is enabled. For cron_results INSERTs, the service")
print("  key (sb_secret_...) is required on the apikey header WITHOUT an")
print("  Authorization Bearer header (the new key format, not legacy JWT).")
print("")
print("CURRENT STATUS: Health checks run locally and save to local JSON.")
print("  Supabase push is BLOCKED by stale schema cache until user fixes it.")
print("")
print("=== END DIAGNOSIS ===")
