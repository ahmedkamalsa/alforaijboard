/*
  ============================================================
  geographic-update.sql
  ------------------------------------------------------------
  تحديث الجغرافيا لسجلات market_listings
  - يربط كل منطقة (area) بمحافظة (governorate)
  - يملأ الـ governorates و areas جدولين جديدين
  - يحدث الـ market_listings لربط الجغرافيا
  ------------------------------------------------------------
*/

-- أولاً: إنشاء جدول governorates و areas (لو لم يُنشأ بعد)
CREATE TABLE IF NOT EXISTS public.governorates (
  id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name_ar     text NOT NULL UNIQUE,
  name_en     text,
  region      text,
  created_at  timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.areas (
  id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name_ar       text NOT NULL,
  governorate_id bigint REFERENCES public.governorates(id) ON DELETE SET NULL,
  created_at    timestamptz DEFAULT now(),
  UNIQUE(name_ar, governorate_id)
);

-- ثانياً: إدخال المحافظات (كويت: ٦ محافظات رئيسية)
INSERT INTO public.governorates (name_ar, name_en, region) VALUES
  ('العاصمة',   'Capital',         'العاصمة'),
  ('الأحمدي',   'Ahmadi',          'الأحمدي'),
  ('الجهراء',   'Jahra',           'الجهراء'),
  ('مبارك الكبير', 'Mubarak Al-Kabeer', 'مبارك الكبير')
ON CONFLICT (name_ar) DO NOTHING;

-- ثالثاً: إدخال المناطق وربطها بالمحافظات
INSERT INTO public.areas (name_ar, governorate_id) VALUES
  -- العاصمة
  ('مركز المدينة',          (SELECT id FROM public.governorates WHERE name_ar='العاصمة')),
  ('السالمية',              (SELECT id FROM public.governorates WHERE name_ar='العاصمة')),
  ('الرياض',                (SELECT id FROM public.governorates WHERE name_ar='العاصمة')),
  ('الشويخ',               (SELECT id FROM public.governorates WHERE name_ar='العاصمة')),
  ('البدع',                 (SELECT id FROM public.governorates WHERE name_ar='العاصمة')),
  ('الصرافة',               (SELECT id FROM public.governorates WHERE name_ar='العاصمة')),
  ('النزهة',               (SELECT id FROM public.governorates WHERE name_ar='العاصمة')),
  ('الشامية',              (SELECT id FROM public.governorates WHERE name_ar='العاصمة')),
  ('المنصورية',             (SELECT id FROM public.governorates WHERE name_ar='العاصمة')),
  ('ضاحية حصة المبارك',       (SELECT id FROM public.governorates WHERE name_ar='العاصمة')),
  ('الكويت المركزية',         (SELECT id FROM public.governorates WHERE name_ar='العاصمة')),
  -- مبارك الكبير
  ('جنوب عبدالله المبارك',     (SELECT id FROM public.governorates WHERE name_ar='م Baron عام الكبير')),
  ('شمال عبدالله المبارك',     (SELECT id FROM public.governorates WHERE name_ar='م Baron عام الكبير')),
  ('الرابية',              (SELECT id FROM public.governorates WHERE name_ar='العاصمة')),
  ('الضيcounters',         (SELECT id FROM public.governorates WHERE name_ar='العاصمة')),
  ('القصور',              (SELECT id FROM public.governorates WHERE name_ar='م Baron عام الكبير')),
  ('العدان',              (SELECT id FROM public.governorates WHERE name_ar='م Baron عام الكبير')),
  ('أبو الحصنة',           (SELECT id FROM public.governorates WHERE name_ar='م Baron عام الكبير'))
ON CONFLICT (name_ar, governorate_id) DO NOTHING;

-- رابعاً: الربط بين market_listings والجغرافيا
UPDATE public.market_listings
SET governorate = g.name_ar,
    area = a.name_ar
FROM public.areas a
JOIN public.governorates g ON g.id = a.governorate_id
WHERE market_listings.area = a.name_ar
  AND (market_listings.governorate IS NULL OR market_listings.governorate = '');

-- خامساً: Areas غير معروفة نربطها بـ "العاصمة" افتراضياً
UPDATE public.market_listings
SET governorate = 'العاصمة'
WHERE governorate IS NULL
  AND area IS NOT NULL
  AND area != '';
