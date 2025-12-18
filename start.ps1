# Quick Start Script - AI Code Review System
# This script sets up and starts both frontend and backend

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "AI Code Review System - Quick Start" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if PostgreSQL is running
Write-Host "1. Checking PostgreSQL..." -ForegroundColor Yellow
$pgService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
if ($pgService -and $pgService.Status -eq "Running") {
    Write-Host "   ✓ PostgreSQL is running" -ForegroundColor Green
} else {
    Write-Host "   ✗ PostgreSQL is not running!" -ForegroundColor Red
    Write-Host "   Please start PostgreSQL service" -ForegroundColor Yellow
    exit 1
}

# Check if database exists
Write-Host ""
Write-Host "2. Checking database..." -ForegroundColor Yellow
$dbCheck = psql -U postgres -lqt 2>$null | Select-String -Pattern "ai_code_review"
if ($dbCheck) {
    Write-Host "   ✓ Database 'ai_code_review' exists" -ForegroundColor Green
} else {
    Write-Host "   ✗ Database does not exist. Creating..." -ForegroundColor Yellow
    psql -U postgres -c "CREATE DATABASE ai_code_review;" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ Database created successfully" -ForegroundColor Green
    } else {
        Write-Host "   ✗ Failed to create database" -ForegroundColor Red
        Write-Host "   Please create it manually: psql -U postgres -c 'CREATE DATABASE ai_code_review;'" -ForegroundColor Yellow
        exit 1
    }
}

# Initialize database tables
Write-Host ""
Write-Host "3. Initializing database tables..." -ForegroundColor Yellow
python -c "from app.db import init_db; init_db()" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Database tables initialized" -ForegroundColor Green
} else {
    Write-Host "   ⚠ Database might already be initialized" -ForegroundColor Yellow
}

# Check if knowledge base is initialized
Write-Host ""
Write-Host "4. Checking knowledge base..." -ForegroundColor Yellow
if (Test-Path ".\data\chroma") {
    Write-Host "   ✓ Knowledge base exists" -ForegroundColor Green
} else {
    Write-Host "   Initializing knowledge base..." -ForegroundColor Yellow
    python -m app.scripts.init_knowledge_base
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ Knowledge base initialized" -ForegroundColor Green
    } else {
        Write-Host "   ✗ Failed to initialize knowledge base" -ForegroundColor Red
        exit 1
    }
}

# Check if frontend dependencies are installed
Write-Host ""
Write-Host "5. Checking frontend dependencies..." -ForegroundColor Yellow
if (Test-Path ".\frontend\node_modules") {
    Write-Host "   ✓ Frontend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "   Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ Frontend dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "   ✗ Failed to install frontend dependencies" -ForegroundColor Red
        Set-Location ..
        exit 1
    }
    Set-Location ..
}

# Start backend
Write-Host ""
Write-Host "6. Starting backend server..." -ForegroundColor Yellow
Write-Host "   Backend will run at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}
Start-Sleep -Seconds 3
Write-Host "   ✓ Backend started (Job ID: $($backendJob.Id))" -ForegroundColor Green

# Start frontend  
Write-Host ""
Write-Host "7. Starting frontend server..." -ForegroundColor Yellow
Write-Host "   Frontend will run at: http://localhost:3000" -ForegroundColor Cyan
$frontendJob = Start-Job -ScriptBlock {
    Set-Location "$using:PWD\frontend"
    npm run dev
}
Start-Sleep -Seconds 3
Write-Host "   ✓ Frontend started (Job ID: $($frontendJob.Id))" -ForegroundColor Green

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "✓ System is running!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access Points:" -ForegroundColor Yellow
Write-Host "  • Frontend:  http://localhost:3000" -ForegroundColor White
Write-Host "  • Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "  • API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "To stop the servers:" -ForegroundColor Yellow
Write-Host "  Press Ctrl+C or run: Get-Job | Stop-Job; Get-Job | Remove-Job" -ForegroundColor White
Write-Host ""
Write-Host "View logs:" -ForegroundColor Yellow
Write-Host "  Backend:  Receive-Job -Id $($backendJob.Id) -Keep" -ForegroundColor White
Write-Host "  Frontend: Receive-Job -Id $($frontendJob.Id) -Keep" -ForegroundColor White
Write-Host ""

# Wait for user to stop
Write-Host "Press any key to stop all servers..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host ""
Write-Host "Stopping servers..." -ForegroundColor Yellow
Stop-Job -Job $backendJob, $frontendJob
Remove-Job -Job $backendJob, $frontendJob
Write-Host "✓ All servers stopped" -ForegroundColor Green
