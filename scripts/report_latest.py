التقرير كامل كالتالي:

الحالة: تحذير (WARN) - 3 مشاكل

1) Docker: متوقف FAIL
   - Daemon غير متصل، pipe مفقود. لازم يعاد تشغيله يدوياً.

2) RAM: طبيعي OK
   - 2437 ميجابايت حر من 16263 ميجابايت إجمالي (15.0%). فوق العتبة 500 ميجابايت.

3) Hermes agents: يعمل OK
   - hermes.exe يعمل (PID 9448).

4) Disk C:/Users/hello: تحذير WARN
   - 19.32 جيجابايت حر من 195.9 جيجابايت إجمالي (9.9%)، تحت عتبة 10%. ابدأ التنظيف قريب.

5) Git (alforaijboard-gh): ملوث UNCLEAN
   - 82 تغيير غير مُ commits (معدل 3، untracked 79). الـ site/static-data/live-db.json و site/last-updated.json وفي _cron_health_latest.json فيهما تغييرات، revision حديثة من Supabase (4,821 سجل).

مشاكل 3:**
- Docker: STOP
- Disk: WARN (9.9% حر)
- Git: DIRTY (82 تغيير)

ملخص سريع:
- Docker: STOP
- RAM: OK (2437 MB حرة)
- Agents: OK (hermes.exe يعمل)
- Disk: WARN (9.9% حر)
- Git: DIRTY (82 تغيير)
