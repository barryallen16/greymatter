@echo off
cd /d "%~dp0"
rem daily.log catches interpreter-level failures (uv, imports, crashes).
rem run.log is written by run.py itself — sharing one file would deadlock on Windows.
uv run run.py >> daily.log 2>&1
rem push the day's matches to the hub the phone reads (/jobs/)
uv run python publish.py --url https://greymatter.isroot.in >> daily.log 2>&1
exit /b %ERRORLEVEL%
