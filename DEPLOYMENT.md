# DentalCorrectIQ Deployment Guide

Complete guide for deploying DentalCorrectIQ in a UK dental practice.

## Pre-Deployment Planning

### 1. Hardware Requirements

**Mac Mini (Server)**
- Model: M2 or M3
- RAM: 16GB minimum (32GB recommended for better performance)
- Storage: 20GB free space (for Ollama + models)
- OS: macOS 12 (Monterey) or later
- Network: Ethernet connection recommended

**Client PCs**
- OS: Windows 10/11 or macOS
- RAM: 4GB minimum
- Python: 3.8 or later
- Network: Connected to same network as Mac Mini

### 2. Network Planning

**Static IP for Mac Mini**
- Assign a static IP (e.g., 192.168.1.100)
- Document this IP - all clients will need it
- Ensure IP is reserved in your DHCP server

**Network Access**
- Server port 8000 must be accessible on local network
- NO internet access required (fully local)
- NO port forwarding to internet (security)

**Firewall Configuration**
- Allow incoming connections on port 8000
- Only from local network (192.168.x.x)
- Block all external access

### 3. User Training Requirements

Train staff on:
1. Using the hotkey (Ctrl+Shift+G)
2. Understanding GDC scores
3. Acting on suggestions
4. Troubleshooting basic issues

## Step-by-Step Deployment

### Phase 1: Mac Mini Setup (30-60 minutes)

#### Step 1: Prepare Mac Mini

```bash
# Update macOS
sudo softwareupdate -i -a

# Install Xcode Command Line Tools
xcode-select --install

# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Step 2: Install Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Verify installation
ollama --version

# Start Ollama service
ollama serve &

# Test it works
ollama run llama3.2:3b "Hello, test message"
```

If successful, press Ctrl+C to exit the test.

#### Step 3: Pull AI Model

```bash
# Pull Llama 3.2 3B model (1.5GB download)
ollama pull llama3.2:3b

# Verify model is installed
ollama list

# You should see:
# NAME            ID              SIZE    MODIFIED
# llama3.2:3b     xxx             1.5GB   X minutes ago
```

#### Step 4: Install DentalCorrectIQ Server

```bash
# Clone repository (replace with your actual repo URL)
cd /Applications
git clone https://github.com/yourusername/DentalIQ.git DentalCorrectIQ
cd DentalCorrectIQ/server

# Run setup script
chmod +x setup.sh run.sh
./setup.sh

# Test server manually
./run.sh

# In another terminal, test the API
curl http://localhost:8000/health
```

You should see:
```json
{
  "status": "healthy",
  "model": "llama3.2:3b",
  "ollama_status": "connected"
}
```

Press Ctrl+C to stop the server.

#### Step 5: Configure Auto-Start

Create a launchd service to start server on boot:

```bash
# Create service file
sudo nano /Library/LaunchDaemons/com.dentalcorrectiq.server.plist
```

Paste this content:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dentalcorrectiq.server</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Applications/DentalCorrectIQ/server/run.sh</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Applications/DentalCorrectIQ/server</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Applications/DentalCorrectIQ/server/logs/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/Applications/DentalCorrectIQ/server/logs/stderr.log</string>
</dict>
</plist>
```

Save and load the service:

```bash
# Create logs directory
mkdir -p /Applications/DentalCorrectIQ/server/logs

# Set permissions
sudo chown root:wheel /Library/LaunchDaemons/com.dentalcorrectiq.server.plist
sudo chmod 644 /Library/LaunchDaemons/com.dentalcorrectiq.server.plist

# Load service
sudo launchctl load /Library/LaunchDaemons/com.dentalcorrectiq.server.plist

# Check it's running
sudo launchctl list | grep dentalcorrectiq

# Test from another machine
curl http://192.168.1.100:8000/health
```

#### Step 6: Configure Static IP

1. Open **System Settings** → **Network**
2. Select your network connection (Ethernet or Wi-Fi)
3. Click **Details**
4. Go to **TCP/IP** tab
5. Change "Configure IPv4" to **Manually**
6. Set:
   - IP Address: `192.168.1.100` (or your chosen IP)
   - Subnet Mask: `255.255.255.0`
   - Router: Your router IP (usually `192.168.1.1`)
7. Click **OK** and **Apply**

**Document this IP address** - you'll need it for all clients.

#### Step 7: Configure Firewall

```bash
# Allow port 8000 (if firewall is enabled)
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/local/bin/ollama
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblock /usr/local/bin/ollama
```

### Phase 2: Client Deployment (15-30 minutes per PC)

#### Option A: Automated Deployment Script

Create `deploy_client.bat` (Windows) or `deploy_client.sh` (Mac):

**Windows (deploy_client.bat)**:
```batch
@echo off
echo DentalCorrectIQ Client Installation
echo ===================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8 or later from python.org
    pause
    exit /b 1
)

REM Clone or copy repository
if not exist "C:\Program Files\DentalCorrectIQ" (
    mkdir "C:\Program Files\DentalCorrectIQ"
)

REM Copy client files (assumes USB or network share)
xcopy /E /I /Y "%~dp0client" "C:\Program Files\DentalCorrectIQ\client"

REM Create virtual environment
cd "C:\Program Files\DentalCorrectIQ\client"
python -m venv venv

REM Install dependencies
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

REM Create desktop shortcut
echo [InternetShortcut] > "%USERPROFILE%\Desktop\DentalCorrectIQ.url"
echo URL=file:///C:\Program Files\DentalCorrectIQ\client\run.bat >> "%USERPROFILE%\Desktop\DentalCorrectIQ.url"

echo.
echo Installation complete!
echo Desktop shortcut created.
echo.
echo IMPORTANT: Set server IP before first use:
echo 1. Launch DentalCorrectIQ from desktop
echo 2. Click Settings
echo 3. Enter: http://192.168.1.100:8000
echo 4. Click Save
echo.
pause
```

#### Option B: Manual Installation

On each Windows PC:

```bash
# 1. Install Python (if not installed)
# Download from python.org

# 2. Clone/copy repository
git clone https://github.com/yourusername/DentalIQ.git "C:\Program Files\DentalCorrectIQ"
cd "C:\Program Files\DentalCorrectIQ\client"

# 3. Create virtual environment
python -m venv venv

# 4. Install dependencies
venv\Scripts\activate
pip install -r requirements.txt

# 5. Create startup script
# Create run.bat with:
@echo off
cd "C:\Program Files\DentalCorrectIQ\client"
venv\Scripts\python.exe main.py
```

#### Step 8: Configure Clients

On each client PC:

1. Launch DentalCorrectIQ
2. Click **Settings**
3. Enter server URL: `http://192.168.1.100:8000`
4. Click **Save Settings**
5. Click **Test Connection** - should show "Connected to server!"

#### Step 9: Test End-to-End

On the client PC:

1. Open Notepad
2. Type: `pacjent skarży się na ból ul6 ttp`
3. Select and copy (Ctrl+C)
4. Press Ctrl+Shift+G
5. Results window should appear with corrected text

If successful, deployment is complete!

### Phase 3: User Training (1 hour)

#### Training Checklist

For each user, demonstrate:

1. **Basic Usage**
   - Open any application (R4, SOE, Word)
   - Type clinical note
   - Select and copy text
   - Press Ctrl+Shift+G
   - Review results
   - Copy corrected text back

2. **Understanding Results**
   - GDC Score interpretation (green/yellow/red)
   - Missing elements
   - Suggestions and how to apply them

3. **Best Practices**
   - When to use the tool (after typing, before finalizing)
   - How to handle suggestions
   - What to do if connection fails

4. **Troubleshooting**
   - Server offline: Contact IT
   - No results: Check copied text
   - Slow response: Wait up to 10 seconds

#### Training Materials

Create a one-page quick reference guide:

```
DentalCorrectIQ Quick Guide
===========================

How to Use:
1. Type your notes in any software
2. Select and copy (Ctrl+C)
3. Press Ctrl+Shift+G
4. Review corrected text
5. Copy back to your notes

Understanding Scores:
🟢 80-100: Excellent - ready to save
🟡 60-79: Good - review suggestions
🔴 0-59: Needs improvement

Common Issues:
- No popup: Check text is copied
- Connection error: Contact IT
- Wrong language: Type in English, Polish, Romanian, or Urdu

Hotkey: Ctrl+Shift+G
Support: IT Department
```

## Post-Deployment

### Week 1: Monitor Usage

- Check server logs daily
- Monitor response times
- Collect user feedback
- Address technical issues

```bash
# Check server is running
sudo launchctl list | grep dentalcorrectiq

# View logs
tail -f /Applications/DentalCorrectIQ/server/logs/stdout.log
tail -f /Applications/DentalCorrectIQ/server/logs/stderr.log
```

### Week 2-4: Optimize

Based on usage patterns:
- Adjust GDC scoring weights
- Add practice-specific abbreviations
- Refine prompts for better results
- Update training materials

### Ongoing Maintenance

**Monthly Tasks**:
- Check Mac Mini disk space
- Review server logs for errors
- Update Python dependencies
- Backup configuration

**Quarterly Tasks**:
- Update macOS (test first!)
- Update Ollama
- Consider upgrading to newer LLM models
- Review user feedback and feature requests

## Troubleshooting Deployment Issues

### Server Won't Start

```bash
# Check Ollama is running
ps aux | grep ollama

# If not, start it
ollama serve &

# Check port is available
lsof -i :8000

# Check logs
tail -50 /Applications/DentalCorrectIQ/server/logs/stderr.log
```

### Clients Can't Connect

```bash
# From client PC, ping server
ping 192.168.1.100

# Test HTTP connection
curl http://192.168.1.100:8000/health

# Check firewall on Mac Mini
sudo pfctl -s rules | grep 8000
```

### Slow Performance

**Check CPU/RAM**:
```bash
# On Mac Mini
top -l 1 | grep "CPU usage"
top -l 1 | grep "PhysMem"
```

**If high memory usage**:
- Close other applications
- Consider using smaller model (Q4 quantization)
- Add more RAM to Mac Mini

**If high CPU usage**:
- Reduce concurrent requests
- Consider upgrading to M3 if using M2

## Security Hardening

### Production Security Checklist

- [ ] Mac Mini on isolated network VLAN (optional but recommended)
- [ ] Firewall configured to block external access
- [ ] No port forwarding from internet to server
- [ ] Regular macOS security updates
- [ ] User accounts with principle of least privilege
- [ ] Audit logs enabled and reviewed monthly

### Optional: Add Authentication

Edit `server/main.py` to add API key:

```python
from fastapi import Header, HTTPException

API_KEY = "your-secret-key-here"  # Store securely!

async def verify_api_key(x_api_key: str = Header()):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

@app.post("/check-note", dependencies=[Depends(verify_api_key)])
async def check_note(request: NoteCheckRequest):
    # ... rest of code
```

Update clients to send API key in headers.

## Backup and Disaster Recovery

### What to Backup

1. **Server Configuration**
   - `/Applications/DentalCorrectIQ/server/`
   - Custom prompts and settings
   - GDC scoring rules

2. **Client Configurations**
   - Server IP settings
   - Custom abbreviations (if added)

3. **Not Needed**
   - Ollama models (can re-download)
   - Python virtual environments (can recreate)

### Disaster Recovery Plan

**If Mac Mini fails**:
1. Set up new Mac Mini
2. Run deployment Phase 1
3. Restore configuration from backup
4. Test thoroughly
5. Update clients with new IP (if changed)

**If client PC fails**:
1. Run client deployment script on new PC
2. Configure server IP
3. Test connection

## Cost Analysis

### Initial Setup
- Mac Mini M2 (16GB): ~£600-800
- Staff time (deployment): 2-4 hours
- Training: 1 hour per user

### Ongoing Costs
- Electricity: ~£50/year (Mac Mini)
- Maintenance: 1 hour/month IT time
- Updates: Minimal (free software)

### ROI Indicators
- Time saved per note: 30-60 seconds
- Notes per day: ~20-50 per dentist
- Improved compliance: Fewer GDC issues
- Multi-language support: More patients

## Scaling

### Multiple Practice Locations

**Option 1: Separate Server Per Location**
- Each location has own Mac Mini
- No network dependencies
- Easier troubleshooting

**Option 2: Central Server**
- One powerful Mac Mini/Mac Studio
- VPN between locations
- Lower hardware cost
- Single point of failure

### High-Volume Practices

For >10 concurrent users:
- Upgrade to Mac Studio (M2 Max/Ultra)
- Consider load balancing
- Use higher RAM (64GB+)
- Monitor performance closely

## Support Plan

### Tiered Support Model

**Tier 1: User Issues**
- Handled by: Practice manager or trained user
- Examples: "Hotkey not working", "No popup"
- Resolution: Quick fixes, restart client

**Tier 2: Technical Issues**
- Handled by: IT support / External consultant
- Examples: "Server offline", "Slow performance"
- Resolution: Server restart, configuration changes

**Tier 3: Development Issues**
- Handled by: Developer / Vendor
- Examples: "Feature requests", "Bug fixes"
- Resolution: Code changes, updates

---

**Questions?** Review the main README.md or contact support.
