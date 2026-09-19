#!/usr/bin/env python3
"""Health check report in 3 levels — 경영자가 바로 읽을 수 있게."""
import datetime

now_kwt = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
ts_display = now_kwt.strftime("%Y-%m-%d %H:%M")

LEVELS = {
    "summary": f"""
########## تقرير الصحة الساعة {ts_display} (رقم الجلسة: cron_health_20260919_2251) ##########

🟢 램: 5.9 جيجابايت فارغ / 16.3 كلها — آمن
🟡 القرص: 22 غيغابايت فارغ من 196 — 10% بالضبط، على限
🔴 دوكر: توقف — docker ps فشل (Docker Desktop daemon مش واصل)
🟡 جيت: تغييرات غير مُلتزمّة — ملفان عدّلوا + 4 ملفات غريبة غير مُراقَبة

الحالة الكلية: يلزم الانتباه — دوكر متوقف + القرص على حدّه
""",
    "detail": f"""
----- مستوى أوسع -----

1) دوكر (Docker Desktop):
   - الأمر: docker ps
   - النتيجة: فشل الاتصال بـ npipe:////./pipe/dockerDesktopLinuxEngine
   - المعنى: Docker Desktop إما متوقف أو مقفول أو ما شغّل Ketika.
   - الخطوة: في Windows، افتح Docker Desktop ودّخله، أو من Task Manager تأكد إن Icon واقف. لو لسه متوقف، اضغط Start → Docker Desktop → انتظر لحد ما يرن، بعدين جرب docker ps تاني.

2) الذاكرة (RAM):
   - الحُرّ: 5,907 ميجابايت
   - الكلي: 16,263 ميجابايت (36.3% حرّ)
   - العتبة: 500 ميجابايت
   - التقييم: آمن — بعيد عن اللIMIT.

3) العمليات (Processes / CPU):
   - حمل المعالج: 42%
   - ملاحظة: هالكروب نص runs في قذيفة منفصلة، عمليات Hermes الحقيقية خارج هالسياق.
   - التقييم: آمن.

4) القرص (C:/Users/hello):
   - الكلي: 196 غيغابايت
   - المستخدم: 175 غيغابايت
   - الفارغ: 22 غيغابايت (10.0% بالضبط)
   - العتبة: 10%
   - التقييم: وافق على الحافة — لو زاد الاستخدام شوي يصير تحذير حقيقي.

5) مستوديّ Git (alforaijboard):
   - الحالة:qg_dirty (غير نظيف)
   - المعدّل: site/last-updated.json و site/static-data/live-db.json
   - غير المُراقَب: _cron_health_latest.json, static-data/e2e-test-report.json, static-data/health.json, supabase/.temp/
   - التقييم: لازم يلتزم أو يُرمى قبل ما يزيد القدح.
""",
    "improve": f"""
----- مستوى المقترحات -----

أ) دوكر متوقف — السبب غالبًا إما:
   - نسي Dunstop/implicitly close
   - crashes في الليل
   - Windows update أعد تشغيل ويندوز وأسقط العمليات

   الحل المجاني والأسرع: شغّل Docker Desktop تاني يدوياً + أضف مهمة في التشغيل الآلي (Scheduled Task) أو Hermes cron يفتحه تلقائيًا إذا توقف.
   لو حابب أتحكّم في Docker عن بعد، اقدر أبني script يفتح Docker Desktop بـ start "" "C:\Program Files\Docker\Docker\Application\docker.exe" لو متوقف.

ب) القرص على 10% — هالحد دقيق جدًا:
   - نظّف ملفات مؤقتة WinSxS/cache: cleanmgr أو Disk Cleanup
   - اتحقق من supabase/.temp/ و cron_results الموصوفة وأمسح اللي{Notation}="_synced" أو القديم
   - لو في ملفات تورنت/نسخ احتياطي اسمها big，她们占空间، انقلهم لخارج C

ج) جيت به تعديلات Untracked + Modified:
   - لو التعديلات عمدية: git add + git commit + git push قبل ما ينسى
   - لو مفيش داعي لها: git stash أو git clean -fd (مع الحذر)
   - ملفات مثل _cron_health_latest.json و static-data/e2e-test-report.json ممكن تكون من اختبارات سابقة — ممكن تمسح أو تُضف لـ .gitignore

د) Trich: لو حابب نتأكد إن Docker Desktop بيعمل Aurora في الخلفية، أقدر أنشئ cron job آخر بيختبر docker info كل ساعة لو توقف يطابق علىك.
""",
}

overall = "STATUS: NEEDS_ATTENTION — Docker stopped, disk at 10% edge, git dirty"

print(LEVELS["summary"])
print(LEVELS["detail"])
print(LEVELS["improve"])
print("\n" + overall)
