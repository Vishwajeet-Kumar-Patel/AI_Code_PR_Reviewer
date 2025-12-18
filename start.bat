@echo off
REM Quick Start Script - AI Code Review System (Windows Batch)

echo ==================================
echo AI Code Review System - Quick Start
echo ==================================
echo.

REM Start Backend
echo Starting backend server...
start "Backend Server" cmd /k "cd /d %~dp0 && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul

REM Start Frontend
echo Starting frontend server...
start "Frontend Server" cmd /k "cd /d %~dp0\frontend && npm run dev"
timeout /t 3 /nobreak >nul

echo.
echo ==================================
echo System is running!
echo ==================================
echo.
echo Access Points:
echo   - Frontend:  http://localhost:3000
echo   - Backend:   http://localhost:8000
echo   - API Docs:  http://localhost:8000/docs
echo.
echo Close the terminal windows to stop the servers.
echo.

pause
