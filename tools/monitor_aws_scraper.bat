@echo off
REM Monitor AWS Scraper Progress
echo ============================================================
echo AWS EC2 Scraper Monitor
echo ============================================================
echo.

echo Checking if scraper is running...
ssh -i "C:\Users\bavis\Downloads\sfsu-scraper-key.pem" ubuntu@3.145.143.107 "ps aux | grep scrape_comprehensive_sfsu.py | grep -v grep"
echo.

echo ============================================================
echo Last 10 lines of scraper log:
echo ============================================================
ssh -i "C:\Users\bavis\Downloads\sfsu-scraper-key.pem" ubuntu@3.145.143.107 "tail -10 scraper.log"
echo.

echo ============================================================
echo Data file status:
echo ============================================================
ssh -i "C:\Users\bavis\Downloads\sfsu-scraper-key.pem" ubuntu@3.145.143.107 "ls -lh data/*.json 2>/dev/null || echo 'No data files yet (will appear after 50 pages)'"
echo.

echo ============================================================
echo To download results when complete:
echo scp -i "C:\Users\bavis\Downloads\sfsu-scraper-key.pem" ubuntu@3.145.143.107:~/data/comprehensive_sfsu_crawl.json D:\sfsu-cs-chatbot\data\
echo ============================================================
