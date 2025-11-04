# DentalCorrectIQ

**AI-Powered Clinical Notes Correction for UK Dental Practices**

Real-time clinical notes correction with multi-language support and GDC compliance scoring. All processing happens locally on your practice network - no patient data ever leaves your building.

## Overview

DentalCorrectIQ helps UK dental practitioners write better clinical notes by:

- **Multi-Language Translation**: Type notes in Polish, Romanian, Urdu, or English shorthand → Get UK GDC-compliant English instantly
- **GDC Compliance Scoring**: Real-time scoring (0-100) based on required documentation elements
- **Proactive Suggestions**: Smart recommendations for missing elements (medical history, consent, etc.)
- **Universal Compatibility**: Works with ANY dental PM software (R4, SOE, Exact, Dentally, iSmile)
- **Complete Privacy**: Local AI running on your Mac Mini - zero cloud dependency

### Example

**Input** (Polish):
```
pacjent skarży się na ból ul6 ttp perc
```

**Output** (UK Clinical English):
```
Patient complains of pain upper left first molar, tender to percussion
```

**GDC Score**: 40/100
**Missing**: Medical history review, Consent discussion, Treatment plan
**Suggestions**:
- Consider adding: 'Medical history reviewed, no changes since last visit'
- Consider documenting: 'Treatment options discussed, patient consented to proposed treatment'

## Architecture

```
Windows PC (dentist typing in R4)
         ↓
   (Ctrl+Shift+G pressed)
         ↓
   (captures clipboard text)
         ↓
HTTP POST → http://192.168.1.100:8000/check-note
         ↓
   Mac Mini (local LLM inference, 300-500ms)
         ↓
JSON Response (corrected text + score + suggestions)
         ↓
   Display overlay on Windows PC
```

### Components

1. **Server** (Mac Mini): FastAPI + Ollama + Llama 3.2 3B
2. **Client** (Windows/Mac): PyQt6 desktop application with global hotkey
3. **Network**: Local network only (192.168.x.x) - no internet required

## Quick Start

### Prerequisites

- **Server**: Mac Mini M2/M3 with macOS, 16GB+ RAM
- **Client**: Windows 10/11 or macOS, Python 3.8+
- **Network**: Both devices on same local network

### Server Setup (Mac Mini)

```bash
# 1. Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Pull Llama 3.2 3B model
ollama pull llama3.2:3b

# 3. Clone repository
git clone https://github.com/yourusername/DentalIQ.git
cd DentalIQ/server

# 4. Run setup script
chmod +x setup.sh
./setup.sh

# 5. Start server
./run.sh
```

Server will start at `http://0.0.0.0:8000`

**Find your Mac Mini's IP address**:
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

Note this IP (e.g., `192.168.1.100`) - you'll need it for the client.

### Client Setup (Windows/Mac)

```bash
# 1. Clone repository (if not already)
git clone https://github.com/yourusername/DentalIQ.git
cd DentalIQ/client

# 2. Run setup script
chmod +x setup.sh   # On Mac/Linux
./setup.sh

# On Windows, use PowerShell:
# python -m venv venv
# venv\Scripts\activate
# pip install -r requirements.txt

# 3. Start client
./run.sh

# On Windows:
# venv\Scripts\activate
# python main.py
```

### Configuration

1. Launch the client application
2. Click **Settings**
3. Enter your Mac Mini's IP address: `http://192.168.1.100:8000`
4. Click **Save Settings**

## Usage

### Basic Workflow

1. **Type your notes** in any application (R4, Notepad, Word, etc.)
2. **Select and copy** the text (`Ctrl+C` / `Cmd+C`)
3. **Press the hotkey**: `Ctrl+Shift+G` (Windows) or `Cmd+Shift+G` (Mac)
4. **Review results** in the popup window
5. **Copy corrected text** back to your notes

### Testing the System

The client includes a built-in test interface:

1. Open the main window
2. Enter test text in the text area
3. Click "Test This Text"

Or test the server directly:

```bash
./test_server.sh
```

Example test inputs:
- Simple: `pt c/o pain ul6 ttp`
- Polish: `pacjent skarży się na ból ul6`
- Full note: `Medical history reviewed. Patient examined, ul6 caries. Treatment: composite filling. Patient consented.`

## Features

### 1. Multi-Language Support

Automatically detects and translates:
- Polish (ą, ć, ę, ł, ń, ó, ś, ź, ż)
- Romanian (ă, â, î, ș, ț)
- Urdu (Arabic script)
- English (including shorthand)

### 2. GDC Compliance Scoring

Checks for 5 key elements (20 points each):
- ✅ Medical History documentation
- ✅ Clinical Findings
- ✅ Diagnosis
- ✅ Treatment Plan
- ✅ Consent discussion

**Score Interpretation**:
- 🟢 80-100: Excellent compliance
- 🟡 60-79: Good, minor additions needed
- 🔴 0-59: Needs improvement

### 3. Smart Suggestions

- Prompts for missing documentation elements
- IR(ME)R justification reminders for radiographs
- UK-specific clinical terminology suggestions

### 4. Abbreviation Expansion

Common dental abbreviations are automatically expanded:
- `pt` → Patient
- `ul6` → upper left first molar
- `ttp` → tender to percussion
- `c/o` → complains of
- `mhx` → medical history

## API Reference

### POST `/check-note`

Check and correct a clinical note.

**Request**:
```json
{
  "text": "pacjent skarży się na ból ul6 ttp",
  "language": "auto"
}
```

**Response**:
```json
{
  "corrected_text": "Patient complains of pain upper left first molar, tender to percussion",
  "gdc_score": 40,
  "missing_elements": [
    "Medical History",
    "Consent",
    "Treatment Plan"
  ],
  "suggestions": [
    "Consider adding: 'Medical history reviewed, no changes since last visit'",
    "Consider documenting: 'Treatment options discussed, patient consented to proposed treatment'"
  ],
  "original_language": "Polish"
}
```

### GET `/health`

Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "model": "llama3.2:3b",
  "ollama_status": "connected"
}
```

## Development

### Project Structure

```
DentalIQ/
├── server/
│   ├── main.py              # FastAPI server
│   ├── requirements.txt     # Python dependencies
│   ├── setup.sh            # Setup script
│   └── run.sh              # Run script
├── client/
│   ├── main.py              # PyQt6 client
│   ├── requirements.txt     # Python dependencies
│   ├── setup.sh            # Setup script
│   └── run.sh              # Run script
├── test_server.sh          # Test script
└── README.md               # This file
```

### Running Tests

```bash
# Test server health and API
./test_server.sh

# Test specific endpoint
curl -X POST http://localhost:8000/check-note \
  -H "Content-Type: application/json" \
  -d '{"text": "pt c/o pain ul6"}'
```

### Customizing the System

#### Modify GDC Scoring Elements

Edit `server/main.py`:

```python
GDC_REQUIRED_ELEMENTS = {
    "medical_history": ["medical history", "mhx", ...],
    "clinical_findings": ["examined", "findings", ...],
    # Add your custom elements
}
```

#### Change LLM Model

```bash
# Use a larger model (requires more RAM)
ollama pull llama3.2:7b

# Update server/main.py:
"model": "llama3.2:7b"
```

#### Customize Hotkey

Edit `client/main.py`:

```python
hotkey = keyboard.GlobalHotKeys({
    '<ctrl>+<shift>+d': on_activate  # Changed to Ctrl+Shift+D
})
```

## Troubleshooting

### Server Issues

**"Connection refused"**
- Check server is running: `ps aux | grep python`
- Verify port 8000 is open: `lsof -i :8000`
- Check firewall settings

**"Ollama not found"**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve
```

**"Model not found"**
```bash
# Pull model again
ollama pull llama3.2:3b

# List installed models
ollama list
```

**Slow inference (>2 seconds)**
- Check Mac Mini RAM usage (Activity Monitor)
- Verify using 3B model, not larger: `ollama list`
- Close other applications
- Consider lower quantization (Q4 instead of Q5)

### Client Issues

**"No text in clipboard"**
- Ensure text is copied before pressing hotkey
- Try copying text again
- Check clipboard permissions (macOS)

**"Failed to check note"**
- Verify server IP in Settings
- Test connection using "Test Connection" button
- Ping server: `ping 192.168.1.100`
- Check both devices on same network

**Hotkey not working**
- Check conflicting applications
- Try different hotkey combination
- Restart client application
- Check accessibility permissions (macOS System Settings → Privacy & Security)

### Network Issues

**Cannot reach server from Windows PC**
```bash
# Ping server
ping 192.168.1.100

# Test HTTP connection
curl http://192.168.1.100:8000/health

# Check firewall (Mac Mini)
sudo pfctl -s rules
```

## Deployment

### Production Checklist

#### Mac Mini Server
- [ ] Ollama installed and Llama 3.2 3B downloaded
- [ ] Static IP address configured (e.g., 192.168.1.100)
- [ ] Server auto-starts on boot (see Auto-Start section)
- [ ] Firewall configured (allow port 8000, local network only)
- [ ] Test server accessible from Windows PC

#### Windows Clients
- [ ] Client installed on each PC
- [ ] Server IP configured in Settings
- [ ] Test connection successful
- [ ] Auto-start on login (optional)
- [ ] Users trained on hotkey usage

### Auto-Start Server on Boot (Mac Mini)

Create launchd service:

```bash
# Create plist file
sudo nano /Library/LaunchDaemons/com.dentalcorrectiq.server.plist
```

Content:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dentalcorrectiq.server</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Applications/DentalCorrectIQ/server/run.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load service:
```bash
sudo launchctl load /Library/LaunchDaemons/com.dentalcorrectiq.server.plist
```

### Security Considerations

1. **Network Isolation**: Server should NOT be accessible from internet
2. **Firewall**: Configure to allow port 8000 only from local network
3. **HTTPS**: For production, consider adding SSL/TLS
4. **Authentication**: Add API key authentication if needed

## Roadmap

### Phase 2 Features
- [ ] Direct text field reading (bypass clipboard)
- [ ] IR(ME)R radiograph justification templates
- [ ] Custom abbreviation dictionary per practice
- [ ] Settings UI for GDC scoring weights
- [ ] Usage analytics dashboard

### Phase 3 Features
- [ ] Referral letter polishing
- [ ] Complaint response tone correction
- [ ] Multi-practice dashboard
- [ ] Integration with specific PM systems

## Support

For issues, questions, or feature requests:
1. Check the Troubleshooting section above
2. Review server logs: `tail -f server/logs/app.log`
3. Test with `./test_server.sh`
4. Open an issue on GitHub

## License

[Add your license here]

## Credits

Built with:
- [Ollama](https://ollama.ai) - Local LLM runtime
- [FastAPI](https://fastapi.tiangolo.com) - Modern Python web framework
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - Cross-platform GUI framework
- [Llama 3.2](https://llama.meta.com) - Meta's language model

---

**Built for UK dental practices. Privacy-first. Always local. Always fast.**
