@echo off
cd /d "%~dp0"
rem daily.log catches interpreter-level failures (uv, imports, crashes).
rem run.log is written by run.py itself — sharing one file would deadlock on Windows.
uv run run.py >> daily.log 2>&1
rem push the day's matches to the hub the phone reads (/jobs/)
uv run python publish.py --url https://greymatter.isroot.in >> daily.log 2>&1
rem mirror the report UI itself to the hub (/scrape/); upload to index.new then mv so nobody reads a half-written page
ssh partha "mkdir -p ~/greymatter/scrape-page" >> daily.log 2>&1
scp -q report.html partha:greymatter/scrape-page/index.new >> daily.log 2>&1
ssh partha "mv -f ~/greymatter/scrape-page/index.new ~/greymatter/scrape-page/index.html" >> daily.log 2>&1
exit /b %ERRORLEVEL%
