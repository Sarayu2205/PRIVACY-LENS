@echo off
echo ====================================
echo   PrivacyLens - Starting Frontend
echo ====================================

cd /d "%~dp0frontend"

if not exist "node_modules" (
    echo [INFO] Installing npm packages...
    npm install
)

echo [INFO] Starting React dev server on http://localhost:5173
echo.
npm run dev
pause
