@echo off
cd /d "%~dp0"

echo Stopping any existing Flask instances...
taskkill /F /IM python.exe /T 2>nul
timeout /t 2 /nobreak >nul

echo Starting the server in User Mode...
echo.

REM Start Python in a new window
start "Gut Health App" /D "%~dp0" python app.py

echo Waiting for server to start...
timeout /t 4 /nobreak >nul

echo Opening browser...
start "" "http://127.0.0.1:5000"

echo.
echo Done! The app should now be open in your browser.
echo You can close this window - the server runs in the other window.
timeout /t 3 >nul
