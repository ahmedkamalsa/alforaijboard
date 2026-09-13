-- Migration: Create listing_distress table
-- Purpose: Track distress signals for real estate listings

CREATE TABLE IF NOT EXISTS listing_distress (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    listing_id UUID NOT NULL REFERENCES market_listings(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('clean','mild','moderate','severe','auction')),
    is_distressed BOOLEAN NOT NULL DEFAULT FALSE,
    matched_keywords JSONB DEFAULT ''[\'\']',
    matched_categories JSONB DEFAULT ''[\'\']',
    confidence NUMERIC(3,2) DEFAULT 0.85 CHECK (confidence >= 0 AND confidence <= 1),
    source TEXT DEFAULT 'automated_analysis',
    notes TEXT,
    last_fetch_at TIMESTAMPTZ,
    CONSTRAINT listing_distress_uq UNIQUE (listing_id, created_at)
);

CREATE INDEX IF NOT EXISTS idx_distress_listing_id ON listing_distress(listing_id);
CREATE INDEX IF NOT EXISTS idx_distress_severity ON listing_distress(severity);
CREATE INDEX IF NOT EXISTS idx_distress_is_distressed ON listing_distress(is_distressed);
CREATE INDEX IF NOT EXISTS idx_distress_created ON listing_distress(created_at DESC);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$ LANGUAGE plpgsql;

CREATE TRIGGER update_listing_distress_updated_at
    BEFORE UPDATE ON listing_distress
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE VIEW v_distress_summary AS
SELECT severity, COUNT(*) AS count
FROM listing_distress
WHERE is_distressed = TRUE
GROUP BY severity
ORDER BY CASE severity WHEN 'auction' THEN 1 WHEN 'severe' THEN 2 WHEN 'moderate' THEN 3 WHEN 'mild' THEN 4 ELSE 5 END;

ALTER TABLE listing_distress ENABLE ROW LEVEL SECURITY;
CREATE POLICY listing_distress_select_public ON listing_distress FOR SELECT USING (true);
CREATE POLICY listing_distress_insert_service ON listing_distress FOR INSERT WITH CHECK (auth.role() = 'service_role');

GRANT SELECT ON listing_distress TO anon, authenticated;
GRANT SELECT ON v_distress_summary TO anon, authenticated;
GRANT INSERT, UPDATE ON listing_distress TO service_role;
