/*
  ============================================================
  alforaijboard-Full-Schema.sql
  ------------------------------------------------------------
  كل الجداول والأر 배출하는 المطلوبة لمشروع لوحة العقارات
  تشمل:
    - جدول المصادر المركزي (sources)
    - جدول المحافظات والمناطق (governorates, areas)
    - جدول تتبع الأخطاء والكوتا (mistakes)
    - تفعيل RLS للجداول المعلّقة (3 جداول)
    - إضافة الربط بين market_listings ومصادر
    - عروض تحليلية (views) لأداء المصادر والتوزيع الجغرافي
  ------------------------------------------------------------
  طريقة الاستخدام:
    1. افتح Supabase SQL Editor
    2. انسخ الكود بالكامل
    3. نفّذ واحدة pass
  ============================================================
*/

-- ============================================================
-- القسم الأول: جدول المصادر المركزي
-- ============================================================

CREATE TABLE IF NOT EXISTS public.sources (
  id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name        text NOT NULL,
  url         text,
  type        text CHECK (type IN ('website','app','social','agency')) DEFAULT 'website',
  transaction_types text[] DEFAULT '{}',
  reliability smallint DEFAULT 1 CHECK (reliability BETWEEN 1 AND 3),
  last_checked timestamptz,
  notes       text,
  created_at  timestamptz DEFAULT now()
);

ALTER TABLE public.sources ENABLE ROW LEVEL SECURITY;

CREATE POLICY "sources_read_anon"   ON public.sources FOR SELECT TO anon     USING (true);
CREATE POLICY "sources_read_service" ON public.sources FOR SELECT TO service_role USING (true);
CREATE POLICY "sources_ins_service" ON public.sources FOR INSERT TO service_role WITH CHECK (true);
CREATE POLICY "sources_upd_service" ON public.sources FOR UPDATE TO service_role USING (true);

-- البيانات الابتدائية
INSERT INTO public.sources (name, url, type, transaction_types, reliability, notes) VALUES
  ('OpenSooq',            'https://www.opensooq.com/ar/kw', 'website', ARRAY['sale','rent'], 2, 'منصّة إعلانات شاملة — أعلى عدد إعلانات في السوق'),
  ('4Sale',               'https://www.4sale.com',           'website', ARRAY['sale','rent'], 2, 'منصّة عقارية تنافسية — ثاني أعلى عدد'),
  ('Mourjan',             'https://www.mourjan.com.kw',      'website', ARRAY['sale','rent'], 2, 'منصّة عقارية كويتية'),
  ('بوعقار / بوشملان (Bu3qar)', 'https://www.bu3qar.com', 'website', ARRAY['sale','rent','swap'], 3, 'دليل الكويت العقاري الأول — بيع وإيجار وتبادل'),
  ('Q8Aqar',              'https://q8aqar.com',              'website', ARRAY['sale','rent'], 2, 'مئات العروض يومياً'),
  ('Yebtah',              'https://yebtah.com',              'website', ARRAY['sale','rent'], 2, 'منصّة عقارية'),
  ('الحسبة — الصفقات المسجلة',  'https://alhisba.com',          'website', ARRAY['sale'], 3, 'تقييم + مزادات + صفقات مسجلة'),
  ('السوق المباشر (بوشملان)',    'https://boshamlan.com',         'agency',  ARRAY['sale','rent','swap'], 2, 'قائمة مكاتب عقارية'),
  ('السوق المباشر (alforaij)',   NULL,                           'agency',  ARRAY['sale','rent','swap'], 3, 'السوق المباشر لشركة الفريج العقارية'),
  ('FindQ8',              'https://findq8.com',              'website', ARRAY['sale','rent'], 2, 'منصّة بحث عقاري')
ON CONFLICT DO NOTHING;

-- ============================================================
-- القسم الثاني: جدول المحافظات
-- ============================================================

CREATE TABLE IF NOT EXISTS public.governorates (
  id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name_ar     text NOT NULL UNIQUE,
  name_en     text,
  region      text,  -- الإقليم الإداري: 'العاصمة', 'الأحمدي', 'الجهراء', 'مبارك الكبير'
  created_at  timestamptz DEFAULT now()
);

ALTER TABLE public.governorates ENABLE ROW LEVEL SECURITY;

CREATE POLICY "gov_read_anon"   ON public.governorates FOR SELECT TO anon     USING (true);
CREATE POLICY "gov_read_service" ON public.governorates FOR SELECT TO service_role USING (true);
CREATE POLICY "gov_ins_service" ON public.governorates FOR INSERT TO service_role WITH CHECK (true);

INSERT INTO public.governorates (name_ar, name_en, region) VALUES
  ('العاصمة',   'Capital',        'العاصمة'),
  ('الأحمدي',   'Ahmadi',         'الأحمدي'),
  ('الجهراء',   'Jahra',          'الجهراء'),
  ('مبارك الكبير', 'Mubarak Al-Kabeer', 'مبارك الكبير'),
  ('الفيحاء',   'Al-Fahaheel',    'مبارك الكبير'),
  ('الرعدية',   'Al-Rai',         'العاصمة'),
  ('السالمية',  'Salmiya',        'العاصمة'),
  ('الحربية',   'Harbiya',        'العاصمة'),
  ('الرياض',    'Riad',           'العاصمة'),
  ('الشويخ',    'Shuwaikh',       'العاصمة'),
  ('البدع',     'Al-Budaiya',     'الجهراء'),
  ('القرين',    'Al-Qurain',      'مبارك الكبير'),
  ('دوليد',     'Sulaibekhat',    'الجهراء'),
  ('الصرافة',   'Al-Sarafiya',    'العاصمة'),
  ('النزهة',    'Al-Nuzha',       'العاصمة'),
  ('الشامية',   'Al-Shaamiya',    'العاصمة'),
  ('المنصورية', 'Al-Mansouriah',  'العاصمة'),
  ('ضاحية حصة المبارك', 'Hawalli',   'العاصمة'),
  ('الكويت المركزية', 'Central Kuwait', 'العاصمة'),
  ('الكويت الشمالية الشرقية', 'NE Kuwait', 'العاصمة')
ON CONFLICT (name_ar) DO NOTHING;

-- ============================================================
-- القسم الثالث: جدول المناطق
-- ============================================================

CREATE TABLE IF NOT EXISTS public.areas (
  id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name_ar       text NOT NULL,
  governorate_id bigint REFERENCES public.governorates(id) ON DELETE SET NULL,
  created_at    timestamptz DEFAULT now(),
  UNIQUE(name_ar, governorate_id)
);

ALTER TABLE public.areas ENABLE ROW LEVEL SECURITY;

CREATE POLICY "areas_read_anon"   ON public.areas FOR SELECT TO anon     USING (true);
CREATE POLICY "areas_read_service" ON public.areas FOR SELECT TO service_role USING (true);
CREATE POLICY "areas_ins_service" ON public.areas FOR INSERT TO service_role WITH CHECK (true);

-- مناطقت شائعة (عينة — يمكن التوسع لاحقاً)
INSERT INTO public.areas (name_ar, governorate_id) VALUES
  ('مركز المدينة',          (SELECT id FROM public.governorates WHERE name_ar='العاصمة')),
  ('السالمية - المنطقة 1',  (SELECT id FROM public.governorates WHERE name_ar='العاصمة')),
  ('السالمية - المنطقة 2',  (SELECT id FROM public.governorates WHERE name_ar='العاصمة')),
  ('الرياض - المنطقة 1',    (SELECT id FROM public.governorates WHERE name_ar='العاصمة')),
  ('الشويخ - المنطقة 1',    (SELECT id FROM public.governorates WHERE name_ar='العاصمة')),
  ('جنوب عبدالله المبارك',   (SELECT id FROM public.governorates WHERE name_ar='مبارك الكبير')),
  ('شمال عبدالله المبارك',   (SELECT id FROM public.governorates WHERE name_ar='مبارك الكبير')),
  ('الرابية',              (SELECT id FROM public.governorates WHERE name_ar='العاصمة')),
  ('الضيcounters',         (SELECT id FROM public.governorates WHERE name_ar='العاصمة')),
  ('アル - الجهراء',          (SELECT id FROM public.governorates WHERE name_ar='الجهراء')),
  ('الصليبية',            (SELECT id FROM public.governorates WHERE name_ar='الجهراء')),
  ('مطلع الداخلية',          (SELECT id FROM public.governorates WHERE name_ar='الجهراء')),
  ('صباح احمد - السكنية',    (SELECT id FROM public.governorates WHERE name_ar='الأحمدي')),
  ('صباح احمد - البحرية',    (SELECT id FROM public.governorates WHERE name_ar='الأحمدي')),
  ('بنيد القار',            (SELECT id FROM public.governorates WHERE name_ar='الأحمدي')),
  ('القيروان',             (SELECT id FROM public.governorates WHERE name_ar='الأحمدي')),
  ('المنطقة 50',           (SELECT id FROM public.governorates WHERE name_ar='مبارك الكبير')),
  ('القصور',              (SELECT id FROM public.governorates WHERE name_ar='مبارك الكبير')),
  ('العدان',              (SELECT id FROM public.governorates WHERE name_ar='مبارك الكبير')),
  ('أبو الحصنة',           (SELECT id FROM public.governorates WHERE name_ar='مبارك الكبير'))
ON CONFLICT (name_ar, governorate_id) DO NOTHING;

-- ============================================================
-- القسم الرابع: جدول تتبع الأخطاء والكوتا
-- ============================================================

CREATE TABLE IF NOT EXISTS public.mistakes (
  id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  created_at    timestamptz DEFAULT now(),
  table_name    text NOT NULL,
  error_code    text,
  error_message text,
  quota_impact  boolean DEFAULT false,
  source        text,  -- أي مصدر سبب الخطأ: API, cron, user
  resolved      boolean DEFAULT false,
  resolved_at   timestamptz,
  notes         text
);

ALTER TABLE public.mistakes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "mistakes_read_service" ON public.mistakes FOR SELECT TO service_role USING (true);
CREATE POLICY "mistakes_ins_service" ON public.mistakes FOR INSERT TO service_role WITH CHECK (true);

-- ============================================================
-- القسم الخامس: تفعيل RLS للجداول المعلّقة
-- ============================================================

--!!! يجب تشغيل هذه على الجداول الموجودة فعليّاً التي لا تزال RLS معطّلة

ALTER TABLE public.client_request_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.client_request_matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.listing_quality_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "cr_read_service" ON public.client_request_messages FOR SELECT TO service_role USING (true);
CREATE POLICY "cr_insert_service" ON public.client_request_messages FOR INSERT TO service_role WITH CHECK (true);

CREATE POLICY "crm_read_service" ON public.client_request_matches FOR SELECT TO service_role USING (true);
CREATE POLICY "crm_insert_service" ON public.client_request_matches FOR INSERT TO service_role WITH CHECK (true);

CREATE POLICY "lqe_read_service" ON public.listing_quality_events FOR SELECT TO service_role USING (true);
CREATE POLICY "lqe_insert_service" ON public.listing_quality_events FOR INSERT TO service_role WITH CHECK (true);

-- ============================================================
-- القسم السادس: الربط بين market_listings ومصادر
-- ============================================================

ALTER TABLE public.market_listings
  ADD COLUMN IF NOT EXISTS source_id bigint
  REFERENCES public.sources(id) ON DELETE SET NULL;

-- تحديث تلقائي لربط المصادر (يُشغّل بعد إنشاء جدول sources)
DO $$
DECLARE
  src record;
BEGIN
  FOR src IN SELECT id, name FROM public.sources LOOP
    UPDATE public.market_listings
    SET source_id = src.id
    WHERE source ILIKE '%' || src.name || '%'
      AND source_id IS NULL;
  END LOOP;
END;
$$;

-- ============================================================
-- القسم السابع: عروض تحليلية
-- ============================================================

-- عرض: أداء كل مصدر
CREATE OR REPLACE VIEW public.source_metrics AS
SELECT
  s.id            AS source_id,
  s.name          AS source_name,
  s.type          AS source_type,
  s.reliability   AS reliability,
  s.transaction_types,
  COUNT(ml.id)      AS total_listings,
  ROUND(COUNT(ml.id)::numeric / NULLIF(
    (SELECT COUNT(*) FROM public.market_listings),0)::numeric * 100, 1
  ) AS pct_of_all,
  COUNT(CASE WHEN ml.price IS NOT NULL THEN 1 END) AS priced_listings,
  ROUND(
    COUNT(CASE WHEN ml.price IS NOT NULL THEN 1 END)::numeric /
    NULLIF(COUNT(ml.id),0)::numeric * 100, 1
  ) AS price_ratio_pct,
  COUNT(DISTINCT ml.governorate) AS covered_governorates,
  COUNT(DISTINCT ml.area)        AS covered_areas,
  MIN(ml.created_at) AS first_seen,
  MAX(ml.created_at) AS last_seen,
  NOW() - MAX(ml.created_at)   AS inactive_for
FROM public.sources s
LEFT JOIN public.market_listings ml ON ml.source_id = s.id
GROUP BY s.id, s.name, s.type, s.reliability, s.transaction_types;

-- عرض: توزيع الإعلانات حسب المحافظة
CREATE OR REPLACE VIEW public.gov_analytics AS
SELECT
  g.name_ar         AS governorate,
  g.region          AS region,
  COUNT(ml.id)      AS total_listings,
  COUNT(CASE WHEN ml.transaction IN ('للبيع','sale') THEN 1 END) AS for_sale,
  COUNT(CASE WHEN ml.transaction IN ('للإيجار','rent') THEN 1 END) AS for_rent,
  COUNT(CASE WHEN ml.transaction IN ('للبدل','swap') THEN 1 END) AS for_swap,
  ROUND(AVG(CASE WHEN ml.space::numeric IS NOT NULL THEN ml.space::numeric END),0) AS avg_space_m2,
  ROUND(AVG(CASE WHEN ml.price::numeric IS NOT NULL THEN ml.price::numeric END),0) AS avg_price_kd
FROM public.governorates g
LEFT JOIN public.market_listings ml ON ml.governorate = g.name_ar
GROUP BY g.id, g.name_ar, g.region
ORDER BY total_listings DESC;

-- عرض: الالتواءات السعرية حسب المصدر
CREATE OR REPLACE VIEW public.price_analysis AS
SELECT
  s.name AS source,
  COUNT(*) AS total,
  ROUND(AVG(ml.price::numeric),0) AS avg_price_kd,
  ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ml.price::numeric),0) AS median_price_kd,
  ROUND(MIN(ml.price::numeric),0) AS min_price_kd,
  ROUND(MAX(ml.price::numeric),0) AS max_price_kd,
  ROUND(STDDEV(ml.price::numeric),0) AS price_stddev
FROM public.sources s
JOIN public.market_listings ml ON ml.source_id = s.id
WHERE ml.price IS NOT NULL
GROUP BY s.id, s.name
ORDER BY avg_price_kd DESC;

-- عرض: حالات المصادر غير النشطة
CREATE OR REPLACE VIEW public.stale_sources AS
SELECT
  s.id, s.name, s.reliability,
  MAX(ml.created_at) AS last_listing_at,
  NOW() - MAX(ml.created_at) AS inactive_for,
  COUNT(ml.id) AS total_listings
FROM public.sources s
LEFT JOIN public.market_listings ml ON ml.source_id = s.id
GROUP BY s.id, s.name, s.reliability
HAVING MAX(ml.created_at) IS NULL
   OR NOW() - MAX(ml.created_at) > INTERVAL '30 days'
ORDER BY last_listing_at ASC NULLS FIRST;
