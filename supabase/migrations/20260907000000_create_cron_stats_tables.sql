-- Migration: Create cron_stats tables
-- Tables: cron_results, source_stats

-- TABLE: cron_results
CREATE TABLE IF NOT EXISTS cron_results (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    run_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status TEXT NOT NULL,
    message TEXT,
    metrics JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_cron_results_run_at ON cron_results(run_at DESC);

-- TABLE: source_stats
CREATE TABLE IF NOT EXISTS source_stats (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    source_id UUID REFERENCES sources(id) ON DELETE CASCADE,
    listings_count INTEGER NOT NULL DEFAULT 0,
    last_checked TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reliability REAL DEFAULT 1.0,
    error_count INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_source_stats_source_id ON source_stats(source_id);
CREATE INDEX IF NOT EXISTS idx_source_stats_last_checked ON source_stats(last_checked DESC);

ALTER TABLE cron_results ENABLE ROW LEVEL SECURITY;
CREATE POLICY cron_results_select ON cron_results FOR SELECT USING (true);
CREATE POLICY cron_results_insert ON cron_results FOR INSERT WITH CHECK (true);
ALTER TABLE source_stats ENABLE ROW LEVEL SECURITY;
CREATE POLICY source_stats_select ON source_stats FOR SELECT USING (true);
CREATE POLICY source_stats_insert ON source_stats FOR INSERT WITH CHECK (true);

GRANT SELECT ON cron_results TO anon, authenticated;
GRANT INSERT ON cron_results TO service_role;
GRANT SELECT ON source_stats TO anon, authenticated;
GRANT INSERT, UPDATE ON source_stats TO service_role;
