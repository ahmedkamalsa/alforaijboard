# ALFORAIJBOARD - VERIFIED DEPENDENCY CHECK
Generated: 2026-09-14 16:19:44

## 1. Git-tracked runtime/generated areas

### static-data
TRACKED BY GIT:
static-data/live-db.json

### site/static-data
TRACKED BY GIT:
site/static-data/clients.json
site/static-data/daily-agent-status.json
site/static-data/dashboard-summary.json
site/static-data/dashboard-summary.min.json
site/static-data/health.json
site/static-data/live-db.json
site/static-data/market-matching.json
site/static-data/official-reference-sources.json
site/static-data/opportunities-history.json
site/static-data/opportunities.json
site/static-data/opportunity-delta.json
site/static-data/outreach-stats.json
site/static-data/sources.json
site/static-data/update-notifications.json
site/static-data/weekly-digest.json
site/static-data/whatsapp-alerts.json

### reports
Not tracked by Git.

### cache
Not tracked by Git.

### cron_logs
Not tracked by Git.

### notifications
Not tracked by Git.

### supabase_data
TRACKED BY GIT:
supabase_data/analysis.json

## 2. Important path references
.\docker-compose.yml:43:site/static-data
.\docker-compose.yml:43:site/static-data
.\cron_results_local.json:31:site/static-data
.\cron_results_local.json:42:site/static-data
.\cron_results_local.json:45:site/static-data
.\cron_results_local.json:76:site/static-data
.\cron_results_local.json:87:site/static-data
.\cron_results_local.json:90:site/static-data
.\cron_market_daily.py:26:supabase_integration
.\cron_market_daily.py:31:supabase_integration
.\agent\validate_static_site.py:11:static-data
.\agent\validate_static_site.py:77:static-data
.\agent\validate_static_site.py:87:static-data
.\Dockerfile.monitor:7:supabase_integration
.\fetch_supabase_data.py:305:supabase_data
.\fetch_supabase_data.py:307:supabase_data
.\fetch_supabase_data.py:311:supabase_data
.\fetch_supabase_data.py:315:supabase_data
.\fetch_supabase_data.py:339:supabase_data
.\fetch_supabase_data.py:344:supabase_data
.\Dockerfile.market:9:supabase_integration
.\live-dashboard.html:60:site/static-data
.\live-dashboard.html:60:static-data
.\live-dashboard.html:103:live-dashboard.html
.\live-dashboard.html:223:static-data
.\egress_optimizer.py:23:supabase_integration
.\market_analyzer.py:19:supabase_integration
.\Dockerfile.sync:7:supabase_integration
.\monitor.py:29:supabase_integration
.\monitor.py:133:supabase_integration
.\docs\PROJECT_INDEX_FOR_AI.md:24:static-data
.\docs\PROJECT_INDEX_FOR_AI.md:25:supabase_data
.\docs\PROJECT_INDEX_FOR_AI.md:29:cron_results_local
.\docs\PROJECT_INDEX_FOR_AI.md:37:supabase_data
.\docs\PROJECT_INDEX_FOR_AI.md:38:live-dashboard.html
.\docs\PROJECT_INDEX_FOR_AI.md:46:supabase_integration
.\docs\PROJECT_INDEX_FOR_AI.md:67:cron_results_local
.\docs\PROJECT_INDEX_FOR_AI.md:74:supabase_data
.\docs\PROJECT_INDEX_FOR_AI.md:75:live-dashboard.html
.\docs\PROJECT_INDEX_FOR_AI.md:83:unified-dashboard.html
.\docs\PROJECT_INDEX_FOR_AI.md:89:live-dashboard.html
.\docs\PROJECT_INDEX_FOR_AI.md:90:live-supabase-client
.\docs\PROJECT_INDEX_FOR_AI.md:91:static-data
.\docs\PROJECT_INDEX_FOR_AI.md:92:static-data
.\docs\PROJECT_INDEX_FOR_AI.md:93:static-data
.\docs\PROJECT_INDEX_FOR_AI.md:94:static-data
.\docs\PROJECT_INDEX_FOR_AI.md:95:static-data
.\docs\PROJECT_INDEX_FOR_AI.md:96:static-data
.\docs\PROJECT_INDEX_FOR_AI.md:97:static-data
.\docs\PROJECT_INDEX_FOR_AI.md:98:static-data
.\docs\PROJECT_INDEX_FOR_AI.md:99:static-data
.\docs\PROJECT_INDEX_FOR_AI.md:100:static-data
.\docs\PROJECT_INDEX_FOR_AI.md:101:static-data
.\docs\PROJECT_INDEX_FOR_AI.md:102:static-data
.\docs\PROJECT_INDEX_FOR_AI.md:103:static-data
.\docs\PROJECT_INDEX_FOR_AI.md:104:static-data
.\docs\PROJECT_INDEX_FOR_AI.md:105:static-data
.\docs\PROJECT_INDEX_FOR_AI.md:106:static-data
.\docs\PROJECT_INDEX_FOR_AI.md:108:supabase-client
.\docs\PROJECT_INDEX_FOR_AI.md:114:unified-dashboard.html
.\docs\PROJECT_INDEX_FOR_AI.md:118:static-data
.\docs\PROJECT_INDEX_FOR_AI.md:119:supabase_integration
.\docs\PROJECT_INDEX_FOR_AI.md:159:supabase_data
.\docs\PROJECT_INDEX_FOR_AI.md:160:live-dashboard.html
.\docs\PROJECT_INDEX_FOR_AI.md:165:unified-dashboard.html
.\docs\PROJECT_INDEX_FOR_AI.md:170:live-dashboard.html
.\docs\PROJECT_INDEX_FOR_AI.md:171:live-supabase-client
.\docs\PROJECT_INDEX_FOR_AI.md:172:static-data
.\docs\PROJECT_INDEX_FOR_AI.md:173:static-data
.\docs\PROJECT_INDEX_FOR_AI.md:174:static-data
.\docs\PROJECT_INDEX_FOR_AI.md:175:static-data
.\docs\PROJECT_INDEX_FOR_AI.md:176:supabase-client
.\docs\PROJECT_INDEX_FOR_AI.md:180:unified-dashboard.html
.\docs\PROJECT_INDEX_FOR_AI.md:183:static-data
.\docs\PROJECT_INDEX_FOR_AI.md:184:supabase_integration
.\docs\PROJECT_INDEX_FOR_AI.md:207:reports/
.\docs\PROJECT_INDEX_FOR_AI.md:208:cache/
.\docs\PROJECT_INDEX_FOR_AI.md:209:cron_logs/
.\docs\PROJECT_INDEX_FOR_AI.md:212:supabase_data
.\docs\PROJECT_INDEX_FOR_AI.md:213:static-data
.\docs\PROJECT_INDEX_FOR_AI.md:214:site/static-data
.\supabase_integration.py:4:supabase_integration
.\sync_live_db.py:8:site/static-data
.\sync_live_db.py:24:static-data
.\sync_live_db.py:121:site/static-data
.\sync_live_db.py:156:site/static-data
.\sync_live_db.py:177:site/static-data
.\update_live_db.py:21:supabase_integration
.\update_live_db.py:28:static-data
.\site\alforaijboard-unified-dashboard.html:610:live-dashboard.html
.\_health_report_20260907_1304.json:36:site/static-data
.\_health_report_20260907_1304.json:45:cron_results_local
.\_health_report_20260907_1304.json:46:supabase_data
.\_health_report_20260907_1304.json:48:supabase_data
.\_health_report_20260907_1304.json:49:supabase_data
.\_health_report_20260907_1304.json:50:supabase_data
.\_health_report_20260907_1304.json:59:cron_results_local
.\_health_report_20260906.txt:32:site/static-data
.\_health_report_20260906.txt:37:supabase_data
.\_health_report_20260906.txt:40:supabase_data
.\_health_report_20260906.txt:41:supabase_data
.\_health_report_20260906.txt:42:supabase_data
.\_health_report_20260906.txt:57:site/static-data
.\site\index.html:15:live-supabase-client
.\site\index.html:16:supabase-client
.\site\app.js:56:static-data
.\site\live-dashboard.html:60:site/static-data
.\site\live-dashboard.html:60:static-data
.\site\live-dashboard.html:103:live-dashboard.html
.\site\live-dashboard.html:223:static-data
.\site\live-supabase-client.js:2:live-supabase-client
.\site\live-supabase-client.js:6:static-data
.\site\live-supabase-client.js:19:static-data
.\site\live-supabase-client.js:23:static-data
.\site\supabase-client.js:2:supabase-client
.\site\sw.js:2:static-data
.\site\sw.js:12:static-data
.\site\sw.js:13:static-data
.\site\sw.js:14:static-data
.\site\sw.js:15:static-data
.\site\sw.js:16:static-data
.\site\sw.js:17:static-data
.\site\sw.js:18:static-data
.\site\sw.js:19:static-data
.\site\sw.js:20:static-data
.\site\sw.js:21:static-data
.\site\sw.js:22:static-data
.\site\sw.js:23:static-data
.\site\sw.js:24:static-data
.\site\sw.js:25:static-data
.\site\sw.js:26:static-data
.\site\sw.js:47:static-data
.\site\sw.js:58:static-data
.\site\tab-organizer.html:34:live-dashboard.html
.\site\tab-organizer.html:55:live-dashboard.html
.\site\unified-dashboard.html:106:live-dashboard.html
.\site\unified-dashboard.html:136:static-data
.\site\unified-dashboard.html:136:static-data
.\site\unified-dashboard.html:136:static-data
.\site\unified-dashboard.html:184:static-data
.\site\unified-dashboard.html:191:static-data
.\site\unified-dashboard.html:210:live-dashboard.html
.\site\unified-dashboard.html:261:live-dashboard.html
.\site\unified-dashboard.html:261:live-dashboard.html
.\site\unified-dashboard.html:264:unified-dashboard.html
.\site\unified-dashboard.html:275:static-data
.\site\unified-dashboard.html:276:static-data
.\site\unified-dashboard.html:277:static-data
.\site\unified-dashboard.html:278:static-data
.\site\unified-dashboard.html:318:static-data
.\site\unified-dashboard.html:319:static-data
.\site\unified-dashboard.html:320:static-data
.\site\unified-dashboard.html:435:static-data

## 3. Deployment references
.\Dockerfile.monitor:1:Dockerfile.monitor
.\Dockerfile.monitor:5:cache
.\Dockerfile.monitor:7:.py
.\Dockerfile.monitor:8:.py
.\Dockerfile.monitor:9:.py
.\Dockerfile.monitor:14:.py
.\docker-compose.yml:16:Dockerfile.market
.\docker-compose.yml:23:cron_logs
.\docker-compose.yml:23:cron_logs
.\docker-compose.yml:24:reports
.\docker-compose.yml:24:reports
.\docker-compose.yml:26:cache
.\docker-compose.yml:26:cache
.\docker-compose.yml:37:Dockerfile.sync
.\docker-compose.yml:43:site/
.\docker-compose.yml:43:static-data
.\docker-compose.yml:43:site/
.\docker-compose.yml:43:static-data
.\docker-compose.yml:44:cache
.\docker-compose.yml:44:cache
.\docker-compose.yml:51:Dockerfile.monitor
.\docker-compose.yml:57:cron_logs
.\docker-compose.yml:57:cron_logs
.\docker-compose.yml:59:cache
.\docker-compose.yml:59:cache
.\docker-compose.yml:69:Dockerfile
.\docker-compose.yml:73:reports
.\docker-compose.yml:73:reports
.\docker-compose.yml:74:cron_logs
.\docker-compose.yml:74:cron_logs
.\Dockerfile.market:1:Dockerfile.market
.\Dockerfile.market:6:cache
.\Dockerfile.market:9:.py
.\Dockerfile.market:10:.py
.\Dockerfile.market:11:.py
.\Dockerfile.market:12:.py
.\Dockerfile.market:18:.py
.\Dockerfile.sync:1:Dockerfile.sync
.\Dockerfile.sync:5:cache
.\Dockerfile.sync:7:.py
.\Dockerfile.sync:8:.py
.\Dockerfile.sync:14:.py
.\vercel.json:2:.py
.\vercel.json:2:.py

## 4. Docker Compose validation
time="2026-09-14T16:19:46+03:00" level=warning msg="The \"SUPABASE_URL\" variable is not set. Defaulting to a blank string."
time="2026-09-14T16:19:46+03:00" level=warning msg="The \"SUPABASE_ANON_KEY\" variable is not set. Defaulting to a blank string."
time="2026-09-14T16:19:46+03:00" level=warning msg="The \"SUPABASE_SERVICE_KEY\" variable is not set. Defaulting to a blank string."
time="2026-09-14T16:19:46+03:00" level=warning msg="The \"SUPABASE_URL\" variable is not set. Defaulting to a blank string."
time="2026-09-14T16:19:46+03:00" level=warning msg="The \"SUPABASE_ANON_KEY\" variable is not set. Defaulting to a blank string."
time="2026-09-14T16:19:46+03:00" level=warning msg="The \"SUPABASE_SERVICE_KEY\" variable is not set. Defaulting to a blank string."
time="2026-09-14T16:19:46+03:00" level=warning msg="The \"SUPABASE_URL\" variable is not set. Defaulting to a blank string."
time="2026-09-14T16:19:46+03:00" level=warning msg="The \"SUPABASE_ANON_KEY\" variable is not set. Defaulting to a blank string."
time="2026-09-14T16:19:46+03:00" level=warning msg="D:\\foraj_social\\287\\alforaijboard\\docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion"
Exit code: 0

## 5. Same-name / possible duplicate files

### live-db.json
6E0CBC49084E99E62909F87D1580528E3E8477AA9043201C71E88F6D2F4B65EA  D:\foraj_social\287\alforaijboard\site\static-data\live-db.json
1BA2D12EE3D1EF8F5A93C81778D0FFCD9A653EEC3A02D1725ED0B80784CDB26C  D:\foraj_social\287\alforaijboard\static-data\live-db.json

### live-dashboard.html
D8D6612C0ACBB946A1A4FF9FE50B7CCFF0E34BE8FC29B31D2790BEDB52214FBF  D:\foraj_social\287\alforaijboard\live-dashboard.html
D8D6612C0ACBB946A1A4FF9FE50B7CCFF0E34BE8FC29B31D2790BEDB52214FBF  D:\foraj_social\287\alforaijboard\site\live-dashboard.html

### unified-dashboard.html
7AC4222A174DA6066F7299D9BCAD45271B902149077D18E4603F67228C7F7E5F  D:\foraj_social\287\alforaijboard\site\unified-dashboard.html

### supabase-client.js
8EBF733DDC3E343633314B090A5D26AA36B99F373495B765AFFE11D4F04CDBB3  D:\foraj_social\287\alforaijboard\site\supabase-client.js

## 6. Current gitignore
# Ø¨Ø§Ù„Ø¹Ø±Ø¨ÙŠ ÙˆØ§Ù„Ø¥Ù†Ø¬Ù„ÙŠØ²ÙŠ â€” Ù…Ù„ÙØ§Øª Ø­Ø³Ø§Ø³Ø© ÙˆØ¨ÙŠØ§Ù†Ø§Øª Ù…Ø¤Ù‚ØªØ©
# Sensitive files & temporary data â€” Arabic & English

# ============================================================
# SENSITIVE â€” secrets / keys / credentials
# Ø­Ø³Ø§Ø³Ø© â€” Ù…ÙØ§ØªÙŠØ­ ÙˆØ¨ÙŠØ§Ù†Ø§Øª Ø§Ø¹ØªÙ…Ø§Ø¯
# ============================================================
.env

# ============================================================
# TEMPORARY â€” generated during development
# Ù…Ø¤Ù‚ØªØ© â€” ØªÙÙ†Ø´Ø£ Ø£Ø«Ù†Ø§Ø¡ Ø§Ù„ØªØ·ÙˆÙŠØ± ÙˆØªÙØ¹Ø§Ø¯ Ø¥Ù†Ø´Ø§Ø¤Ù‡Ø§ ØªÙ„Ù‚Ø§Ø¦ÙŠØ§Ù‹
# ============================================================
supabase/.temp/
supabase_data/
__pycache__/
*.pyc
*.pyo
.pytest_cache/
*.egg-info/
dist/
build/

# ============================================================
# ============================================================
# GENERATED â€” outputs Ø£Ù†ØªØ¬Øª Ø£Ø«Ù†Ø§Ø¡ Ø§Ù„ØªØ´ØºÙŠÙ„ (Ù„Ø§ ØªÙØ±ÙØ¹)
# Ù…ÙˆÙ„Ù‘Ø¯Ø© â€” ØªÙÙ†Ø´Ø£ Ø£Ø«Ù†Ø§Ø¡ Ø§Ù„ØªØ´ØºÙŠÙ„ ÙˆØªÙØ¹Ø§Ø¯ Ø¥Ù†Ø´Ø§Ø¤Ù‡Ø§ ØªÙ„Ù‚Ø§Ø¦ÙŠØ§Ù‹
# ============================================================
cache/
notifications/
reports/
cron_logs/
