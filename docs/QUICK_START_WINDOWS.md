# QFZZ Quick Start - Windows PowerShell

## 🚀 Get Running in 5 Minutes

### Prerequisites Check
```powershell
python --version    # Should be 3.10+
node --version      # Should be 18+
git --version       # Should be installed
```

### 1️⃣ Clone & Setup
```powershell
# Navigate to your preferred location
cd $HOME\Documents

# Clone the repository
git clone https://github.com/fuzzywigg/QFZZ.git
cd QFZZ

# Set up Python environment
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Troubleshooting**: If virtual environment activation fails:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2️⃣ Install Frontend
```powershell
cd frontend
npm install
cd ..
```

### 3️⃣ Run the Application

**Open TWO PowerShell windows:**

#### Window 1 - Backend:
```powershell
cd $HOME\Documents\QFZZ
.\venv\Scripts\Activate.ps1
python run_server.py
```

#### Window 2 - Frontend:
```powershell
cd $HOME\Documents\QFZZ\frontend
npm run dev
```

### 4️⃣ Open Your Browser

Navigate to: **http://localhost:3000**

---

## 🎵 What You'll See

- **Web GUI** at http://localhost:3000
- **Backend API** at http://localhost:8000
- **AI DJ** ready to play music and chat
- **Knowledge Graph** visualization

---

## 🛑 Stopping the Server

Press **Ctrl + C** in each PowerShell window

---

## 🔁 Running Again Later

Just repeat step 3 (run backend + frontend in two windows)!

---

## ⚙️ Optional: Add API Keys

For better AI DJ responses:

1. Copy environment file:
   ```powershell
   Copy-Item .env.example .env
   ```

2. Edit `.env` in Notepad:
   ```powershell
   notepad .env
   ```

3. Add your API key (free options):
   - Google Gemini: https://makersuite.google.com/app/apikey
   - Groq: https://console.groq.com

---

## 📚 Full Documentation

For detailed troubleshooting and advanced setup:
- **[WINDOWS_SETUP.md](../WINDOWS_SETUP.md)** - Complete Windows guide
- **[README.md](../README.md)** - Full project documentation
- **[GETTING_STARTED.md](../GETTING_STARTED.md)** - Development guide

---

## 🆘 Common Issues

### "python: command not found"
- Install Python from https://python.org
- Check "Add Python to PATH" during installation

### "npm: command not found"
- Install Node.js from https://nodejs.org

### Port already in use
```powershell
# Find process using port 8000:
netstat -ano | findstr :8000
# Kill it (replace PID):
taskkill /PID <PID> /F
```

---

**QFZZ** - The Pulse of the Quantum Realm 🎵✨
