:: Dynamo!!
:: System Health Check Script for Hermes Cron
:: Kuwait time hourly check

@echo off
setlocal EnableDelayedExpansion

echo ================================================
echo  System Health Check - %date% %time%
echo ================================================
echo.

:: 1. DOCKER
echo [1/5] Docker Daemon Check
docker ps > docker_check.tmp 2>&1
set "DOCKER_RC=%ERRORLEVEL%"
if %DOCKER_RC% NEQ 0 (
    echo [ALERT] Docker daemon NOT running (exit %DOCKER_RC%)
) else (
    echo [OK] Docker daemon running
)
echo.

:: 2. RAM - use WMIC (safe, no -c)
echo [2/5] RAM Check
for /f "tokens=2 delims==" %%A in ('wmic OS get FreePhysicalMemory /value ^| find "="') do set "FREE_RAW=%%A"
for /f "tokens=2 delims==" %%A in ('wmic OS get TotalVisibleMemorySize /value ^| find "="') do set "TOTAL_RAW=%%A"
set /a FREE_MB=%FREE_RAW%/1024
set /a TOTAL_MB=%TOTAL_RAW%/1024
set /a PCT_USED=100-%FREE_MB%*100/%TOTAL_MB%
if %FREE_MB% LSS 500 (
    echo [ALERT] Free RAM: %FREE_MB% MB < 500 MB threshold
) else (
    echo [OK] Free RAM: %FREE_MB% MB / %TOTAL_MB% MB (%PCT_USED%% used)
)
echo.

:: 3. HERMES/NODE/PYTHON PROCESSES
echo [3/5] Hermes Agents & Node/Python Processes
wmic process where "Name like '%%hermes%%' or Name like '%%node%%' or Name like '%%python%%'" get Name,ProcessId,CommandLine /format:list > procs.tmp 2>&1
echo Found %~z procs.tmp bytes of process data
type procs.tmp 2>nul | findstr /i "hermes node python" | find /c /v ""
set "PROC_COUNT=0"
for /f "tokens=2 delims==" %%A in ('wmic process where "Name like '%%hermes%%'" get ProcessId /value 2^>nul ^| find "="') do set /a PROC_COUNT+=1
echo Hermes-related processes found: !PROC_COUNT!
echo.

:: 4. DISK SPACE - C: drive
echo [4/5] Disk Space Check (C:/Users/hello)
wmic logicaldisk where "DeviceID='C:' and DriveType=3" get FreeSpace,Size /format:list > disk.tmp 2>&1
for /f "tokens=2 delims==" %%A in ('findstr /i "FreeSpace=" disk.tmp') do set "DISK_FREE_RAW=%%A"
for /f "tokens=2 delims==" %%A in ('findstr /i "Size=" disk.tmp') do set "DISK_TOTAL_RAW=%%A"
set /a DISK_FREE_GB=!DISK_FREE_RAW!/1073741824
set /a DISK_TOTAL_GB=!DISK_TOTAL_RAW!/1073741824
set /a DISK_PCT_FREE=!DISK_FREE_RAW! * 100 / !DISK_TOTAL_RAW!
if !DISK_PCT_FREE! LSS 10 (
    echo [ALERT] Disk free: !DISK_PCT_FREE!%% (< 10%%). Free: !DISK_FREE_GB! GB / !DISK_TOTAL_GB! GB
) else (
    echo [OK] Disk free: !DISK_PCT_FREE!%% (>= 10%%). Free: !DISK_FREE_GB! GB / !DISK_TOTAL_GB! GB
)
echo.

:: 5. GIT STATUS FOR ALFORAIJBOARD
echo [5/5] Git Repo Status (alforaijboard)
cd /d C:\Users\hello\alforaijboard-gh 2>nul
if errorlevel 1 (
    echo [FAIL] Directory not found or not accessible
) else (
    git status --porcelain > git_status.tmp 2>&1
    set "GIT_RC=%ERRORLEVEL%"
    if %GIT_RC% NEQ 0 (
        echo [FAIL] Not a git repository
    ) else (
        set "UNCOMM_BACKUP=!ERRORLEVEL!"
        for /f %%A in ('find /c /v "" git_status.tmp 2^>nul') do set "LINE_COUNT=%%A"
        if defined LINE_COUNT if !LINE_COUNT! GTR 0 (
            echo [ALERT] Uncommitted changes found:
            type git_status.tmp
        ) else (
            echo [OK] Working tree clean, no uncommitted changes
        )
    )
)

echo.
echo ================================================
echo  Health Check Complete
echo ================================================

:: Cleanup
del docker_check.tmp procs.tmp disk.tmp git_status.tmp 2>nul
endlocal
