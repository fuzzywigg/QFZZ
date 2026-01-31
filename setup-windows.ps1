# QFZZ Windows Setup Script
# This script automates the setup process for Windows users

Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║           QFZZ - AI Radio Setup for Windows                  ║" -ForegroundColor Cyan
Write-Host "║           The Pulse of the Quantum Realm 🎵                  ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Function to check if a command exists
function Test-CommandExists {
    param($command)
    $null = Get-Command $command -ErrorAction SilentlyContinue
    return $?
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
Write-Host ""

$allPrerequisitesMet = $true

# Check Python
Write-Host "Checking Python..." -NoNewline
if (Test-CommandExists python) {
    $pythonVersion = python --version 2>&1
    Write-Host " ✓ Found: $pythonVersion" -ForegroundColor Green
    
    # Check version
    $versionString = $pythonVersion -replace "Python ", ""
    $version = [version]$versionString.Split()[0]
    if ($version -lt [version]"3.10") {
        Write-Host "  ⚠ Warning: Python 3.10 or higher recommended" -ForegroundColor Yellow
    }
} else {
    Write-Host " ✗ Not found" -ForegroundColor Red
    Write-Host "  Please install Python 3.10+ from https://www.python.org/downloads/" -ForegroundColor Yellow
    $allPrerequisitesMet = $false
}

# Check Node.js
Write-Host "Checking Node.js..." -NoNewline
if (Test-CommandExists node) {
    $nodeVersion = node --version 2>&1
    Write-Host " ✓ Found: $nodeVersion" -ForegroundColor Green
    
    # Check version
    $versionNumber = [int]($nodeVersion -replace "v", "" -split "\.")[0]
    if ($versionNumber -lt 18) {
        Write-Host "  ⚠ Warning: Node.js 18 or higher recommended" -ForegroundColor Yellow
    }
} else {
    Write-Host " ✗ Not found" -ForegroundColor Red
    Write-Host "  Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    $allPrerequisitesMet = $false
}

# Check npm
Write-Host "Checking npm..." -NoNewline
if (Test-CommandExists npm) {
    $npmVersion = npm --version 2>&1
    Write-Host " ✓ Found: v$npmVersion" -ForegroundColor Green
} else {
    Write-Host " ✗ Not found (should come with Node.js)" -ForegroundColor Red
    $allPrerequisitesMet = $false
}

# Check Git
Write-Host "Checking Git..." -NoNewline
if (Test-CommandExists git) {
    $gitVersion = git --version 2>&1
    Write-Host " ✓ Found: $gitVersion" -ForegroundColor Green
} else {
    Write-Host " ✗ Not found" -ForegroundColor Red
    Write-Host "  Please install Git from https://git-scm.com/download/win" -ForegroundColor Yellow
    $allPrerequisitesMet = $false
}

Write-Host ""

if (-not $allPrerequisitesMet) {
    Write-Host "❌ Prerequisites not met. Please install missing software and run this script again." -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ All prerequisites met!" -ForegroundColor Green
Write-Host ""

# Create virtual environment
Write-Host "Setting up Python virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
$activateScript = ".\venv\Scripts\Activate.ps1"

# Check if execution policy allows running the script
try {
    & $activateScript
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
} catch {
    Write-Host "⚠ Could not activate virtual environment" -ForegroundColor Yellow
    Write-Host "  Setting execution policy to allow script execution..." -ForegroundColor Yellow
    Write-Host "  (This requires your confirmation)" -ForegroundColor Yellow
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    & $activateScript
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
}

# Install Python dependencies
Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
Write-Host "(This may take a few minutes)" -ForegroundColor Gray
pip install -q --upgrade pip
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Error installing Python dependencies" -ForegroundColor Red
    exit 1
}

# Install frontend dependencies
Write-Host ""
Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
Write-Host "(This may take a few minutes)" -ForegroundColor Gray
Set-Location frontend
npm install

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Frontend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Error installing frontend dependencies" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Set-Location ..

# Create .env file if it doesn't exist
Write-Host ""
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✓ .env file created" -ForegroundColor Green
    Write-Host "  📝 Edit .env to add your API keys for better AI DJ performance" -ForegroundColor Cyan
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

# Setup complete
Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                    Setup Complete! 🎉                         ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "To start QFZZ, you need to open TWO PowerShell windows:" -ForegroundColor Cyan
Write-Host ""
Write-Host "Window 1 - Backend Server:" -ForegroundColor Yellow
Write-Host "  cd $PWD" -ForegroundColor White
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  python run_server.py" -ForegroundColor White
Write-Host ""
Write-Host "Window 2 - Frontend Server:" -ForegroundColor Yellow
Write-Host "  cd $PWD\frontend" -ForegroundColor White
Write-Host "  npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "Then open your browser to: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "For more details, see WINDOWS_SETUP.md" -ForegroundColor Gray
Write-Host ""

# Ask if user wants to start servers now
$startNow = Read-Host "Would you like to start the servers now? (y/n)"

if ($startNow -eq "y" -or $startNow -eq "Y") {
    Write-Host ""
    Write-Host "Starting backend server in a new window..." -ForegroundColor Yellow
    
    # Backend startup command
    $backendCmd = "cd '$PWD'; .\venv\Scripts\Activate.ps1; " +
                  "Write-Host 'Starting QFZZ Backend...' -ForegroundColor Cyan; " +
                  "python run_server.py"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd
    
    Start-Sleep -Seconds 3
    
    Write-Host "Starting frontend server in a new window..." -ForegroundColor Yellow
    
    # Frontend startup command
    $frontendCmd = "cd '$PWD\frontend'; " +
                   "Write-Host 'Starting QFZZ Frontend...' -ForegroundColor Cyan; " +
                   "npm run dev"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd
    
    Write-Host ""
    Write-Host "✓ Servers started in separate windows!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Waiting for servers to initialize..." -ForegroundColor Yellow
    Write-Host "(This typically takes 15-30 seconds)" -ForegroundColor Gray
    
    # Wait longer for slower systems, with progress indicators
    for ($i = 1; $i -le 20; $i++) {
        Start-Sleep -Seconds 1
        if ($i -eq 10) {
            Write-Host "  Still initializing..." -ForegroundColor Gray
        }
    }
    
    Write-Host ""
    Write-Host "Opening browser to http://localhost:3000..." -ForegroundColor Yellow
    Write-Host "(If the page doesn't load, wait a few more seconds and refresh)" -ForegroundColor Gray
    Start-Process "http://localhost:3000"
    
    Write-Host ""
    Write-Host "🎵 Enjoy your QFZZ AI Radio experience!" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "You can start the servers manually using the commands above." -ForegroundColor Gray
}

Write-Host ""
Read-Host "Press Enter to close this window"
