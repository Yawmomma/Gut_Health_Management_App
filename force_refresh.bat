@echo off
echo ========================================
echo FORCE REFRESH - Clearing All Caches
echo ========================================

echo.
echo [1/4] Stopping any running Flask servers...
taskkill /F /IM python.exe /T 2>nul
timeout /t 2 /nobreak >nul

echo.
echo [2/4] Deleting Python cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul

echo.
echo [3/4] Deleting Flask cache...
if exist "flask_session" rd /s /q "flask_session"

echo.
echo [4/4] Starting fresh Flask server...
echo.
echo ========================================
echo Server Starting...
echo ========================================
echo.
echo Visit: http://localhost:5000/foods/cache-test
echo.

python app.py
