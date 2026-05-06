# QFZZ Windows Setup Guide - Running the GUI with PowerShell

This guide will help you get the QFZZ AI Radio GUI running on Windows using PowerShell.

## ⏱️ Time Required: 15-20 minutes

## 🚀 Two Setup Methods

### Method 1: Automated Setup (Recommended for Beginners)

After cloning the repository, simply run the setup script:

```powershell
# Clone the repository first
git clone https://github.com/fuzzywigg/QFZZ.git
cd QFZZ

# Run the automated setup script
.\setup-windows.ps1
```

The script will:
- ✅ Check all prerequisites
- ✅ Create Python virtual environment
- ✅ Install all Python dependencies
- ✅ Install all frontend dependencies
- ✅ Create .env configuration file
- ✅ Optionally start both servers for you

### Method 2: Manual Setup (Complete Control)

Follow the detailed steps below for a manual installation.

## 📋 Setup Checklist

Follow these steps in order:
- [ ] Install Prerequisites (Python, Node.js, Git)
- [ ] Clone the Repository
- [ ] Set Up Python Backend
- [ ] Set Up Frontend (Next.js)
- [ ] Start Backend Server (PowerShell Window 1)
- [ ] Start Frontend Server (PowerShell Window 2)
- [ ] Open GUI in Browser

## Prerequisites

Before starting, ensure you have the following installed:

1. **Python 3.10 or higher**
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"
   - Verify: Open PowerShell and run `python --version`

2. **Node.js 18 or higher**
   - Download from: https://nodejs.org/
   - This includes npm (Node Package Manager)
   - Verify: Open PowerShell and run `node --version`

3. **Git for Windows**
   - Download from: https://git-scm.com/download/win
   - Verify: Open PowerShell and run `git --version`

4. **PowerShell 5.1 or higher** (comes with Windows 10/11)
   - Verify: Open PowerShell and run `$PSVersionTable.PSVersion`

## Manual Setup Guide

### Step 1: Open PowerShell

1. Press `Windows + X` and select "Windows PowerShell" or "Windows Terminal"
2. Alternatively, press `Windows + R`, type `powershell`, and press Enter

### Step 2: Clone the Repository

```powershell
# Navigate to where you want to install QFZZ (e.g., your Documents folder)
cd $HOME\Documents

# Clone the repository
git clone https://github.com/fuzzywigg/QFZZ.git

# Navigate into the QFZZ directory
cd QFZZ
```

### Step 3: Set Up Python Backend

```powershell
# Create a virtual environment (recommended)
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# If you get an execution policy error, run this first:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install Python dependencies
pip install -r requirements.txt

# (Optional) Install development dependencies if you want to contribute
# pip install -r requirements-dev.txt
```

### Step 4: Configure Environment (Optional but Recommended)

```powershell
# Copy the example environment file
Copy-Item .env.example .env

# Edit the .env file with your preferred text editor
# You can use Notepad:
notepad .env

# Or use VS Code if installed:
# code .env
```

**API Keys Configuration:**
- For best results, add at least one LLM API key to `.env`:
  - `GOOGLE_AI_API_KEY` - Get from https://makersuite.google.com/app/apikey
  - `GROQ_API_KEY` - Get from https://console.groq.com (free tier)
- The system will work with local fallbacks if no API keys are provided

### Step 5: Set Up Frontend (Next.js GUI)

Open a **new PowerShell window** (keep the backend one open):

```powershell
# Navigate to the QFZZ directory
cd $HOME\Documents\QFZZ

# Navigate to the frontend directory
cd frontend

# Install Node.js dependencies
npm install

# This may take a few minutes on the first run
```

### Step 6: Start the Backend Server

In the **first PowerShell window** (with Python virtual environment activated):

```powershell
# Make sure you're in the QFZZ root directory
cd $HOME\Documents\QFZZ

# Start the Python backend server
python run_server.py
```

You should see output like:
```
Starting QFZZ Server...
Scanning library for content...
QFZZ SYSTEM ONLINE
Backend API/Stream: http://localhost:8000
Frontend App:       http://localhost:3000
Press Ctrl+C to stop
```

### Step 7: Start the Frontend GUI

In the **second PowerShell window**:

```powershell
# Make sure you're in the frontend directory
cd $HOME\Documents\QFZZ\frontend

# Start the Next.js development server
npm run dev
```

You should see output like:
```
- ready started server on 0.0.0.0:3000, url: http://localhost:3000
- event compiled client and server successfully
```

### Step 8: Open the GUI in Your Browser

Open your web browser and navigate to:

**http://localhost:3000**

You should see the QFZZ AI Radio GUI! 🎵

## System Architecture

Here's how the components work together:

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Web Browser                          │
│                  http://localhost:3000                       │
│                  (Next.js Frontend GUI)                      │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/WebSocket
                      │ API Requests
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Python Backend Server                           │
│              http://localhost:8000                          │
│                                                              │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │  AI DJ System  │  │  Music Player │  │ Knowledge Graph │ │
│  │   (LLM-based)  │  │  & Streaming  │  │  & Analytics    │ │
│  └────────────────┘  └──────────────┘  └─────────────────┘ │
│                                                              │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │   Blockchain   │  │   Library     │  │   User Data     │ │
│  │  Trust Network │  │   Scanner     │  │   & Profiles    │ │
│  └────────────────┘  └──────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                      │
                      ▼
           ┌──────────────────────┐
           │  Audio Content Files │
           │  (qfzz_audio_content)│
           └──────────────────────┘
```

**Two PowerShell Windows Required:**
- **Window 1**: Runs Python backend (port 8000) - handles AI, music, data
- **Window 2**: Runs Next.js frontend (port 3000) - provides the web GUI

## What You Can Do in the GUI

- **Play Music**: Browse and play tracks from the station
- **Interact with AI DJ**: Get personalized music recommendations
- **View Knowledge Graph**: See how tracks and preferences are connected
- **Request Tracks**: Ask the DJ to play specific songs
- **Explore Library**: Browse your music collection

## Troubleshooting

### Issue: "python: command not found"

**Solution**: Python is not in your PATH.
- Reinstall Python and make sure to check "Add Python to PATH"
- Or add Python manually to your PATH environment variable

### Issue: "npm: command not found"

**Solution**: Node.js is not installed or not in your PATH.
- Install Node.js from https://nodejs.org/
- Restart PowerShell after installation

### Issue: Cannot activate virtual environment

**Error**: "execution of scripts is disabled on this system"

**Solution**: Run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Port already in use

**Error**: "Address already in use" or "Port 8000/3000 is already in use"

**Solution**: Another application is using the port.
```powershell
# Find what's using the port (for port 8000):
netstat -ano | findstr :8000

# Kill the process (replace PID with the actual process ID):
taskkill /PID <PID> /F

# Or simply change the port in the application
```

### Issue: Backend starts but frontend can't connect

**Solution**: Make sure:
1. Backend is running on port 8000
2. No firewall is blocking localhost connections
3. Both servers are running in separate PowerShell windows

### Issue: No music plays

**Solution**: The system needs audio files.
- Place audio files (.wav, .mp3) in the `qfzz_audio_content` directory
- Or use the test audio files that are generated automatically

## Stopping the Servers

To stop the servers, go to each PowerShell window and press:

**Ctrl + C**

This will gracefully shut down each server.

## Running Again Later

Next time you want to run QFZZ, you only need to:

1. **Open two PowerShell windows**

2. **First window (Backend)**:
   ```powershell
   cd $HOME\Documents\QFZZ
   .\venv\Scripts\Activate.ps1
   python run_server.py
   ```

3. **Second window (Frontend)**:
   ```powershell
   cd $HOME\Documents\QFZZ\frontend
   npm run dev
   ```

4. **Open browser to http://localhost:3000**

## Alternative: Run with Simple Python Demo

If you just want to test the Python backend without the full GUI:

```powershell
cd $HOME\Documents\QFZZ
.\venv\Scripts\Activate.ps1
python main.py
```

This will run a simple demo of the AI DJ system in the console.

## Tips for Windows Users

### Using Windows Terminal (Recommended)

Windows Terminal provides a better experience with multiple tabs:

1. Install from Microsoft Store: "Windows Terminal"
2. Open Windows Terminal
3. Open two tabs (Ctrl + Shift + T)
4. Run backend in first tab, frontend in second tab

### Using VS Code

If you have VS Code installed:

```powershell
# Open the project in VS Code
cd $HOME\Documents\QFZZ
code .
```

VS Code has integrated terminals, making it easy to run both servers.

### Creating Desktop Shortcuts

**Backend Shortcut:**
1. Right-click on Desktop > New > Shortcut
2. Location: `powershell.exe -NoExit -Command "cd $HOME\Documents\QFZZ; .\venv\Scripts\Activate.ps1; python run_server.py"`
3. Name: "QFZZ Backend"

**Frontend Shortcut:**
1. Right-click on Desktop > New > Shortcut
2. Location: `powershell.exe -NoExit -Command "cd $HOME\Documents\QFZZ\frontend; npm run dev"`
3. Name: "QFZZ Frontend"

## Next Steps

- Read [README.md](README.md) for more information about QFZZ
- Check [GETTING_STARTED.md](GETTING_STARTED.md) for development details
- Explore the [docs](docs/) folder for advanced configuration
- Configure your API keys in `.env` for better AI DJ responses
- Add your own music to `qfzz_audio_content` directory

## Need Help?

- **GitHub Issues**: https://github.com/fuzzywigg/QFZZ/issues
- **Documentation**: Check the `docs/` folder
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)

## System Requirements

- **OS**: Windows 10 or Windows 11
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 2GB for software + space for your music library
- **Python**: 3.10 or higher
- **Node.js**: 18 or higher

---

**QFZZ** - *The Pulse of the Quantum Realm* 🎵✨

Enjoy your personalized AI radio experience!
