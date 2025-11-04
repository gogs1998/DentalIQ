# Changelog

All notable changes to DentalCorrectIQ will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-04

### Added - MVP Release

#### Server Features
- FastAPI server with local LLM integration via Ollama
- Llama 3.2 3B model support for clinical note correction
- Multi-language detection (Polish, Romanian, Urdu, English)
- Automatic translation to UK clinical English
- GDC compliance scoring system (0-100 scale)
- Missing elements detection (Medical History, Clinical Findings, Diagnosis, Treatment Plan, Consent)
- Smart suggestions for improving documentation
- IR(ME)R radiograph justification detection
- Health check endpoint
- Abbreviation expansion (pt, ul6, ttp, etc.)

#### Client Features
- Cross-platform desktop application (Windows/Mac)
- Global hotkey support (Ctrl+Shift+G)
- System tray integration
- Clipboard-based text capture
- Results window with GDC score visualization
- Color-coded score display (green/yellow/red)
- One-click copy corrected text
- Settings panel for server configuration
- Connection testing
- Built-in test interface

#### Documentation
- Comprehensive README with setup instructions
- Detailed DEPLOYMENT guide for production use
- Test scripts for quick validation
- Setup scripts for automated installation
- Auto-start configuration examples

#### Developer Tools
- Automated setup scripts (server and client)
- Run scripts for easy launching
- Requirements files with pinned dependencies
- Test suite for API validation
- Git configuration

### Technical Details
- Python 3.8+ support
- FastAPI for REST API
- PyQt6 for GUI
- Ollama for LLM runtime
- Local network only (no cloud dependency)
- 300-500ms typical latency

## [Unreleased]

### Planned for 0.2.0
- Direct text field reading (bypass clipboard)
- Custom abbreviation dictionary
- IR(ME)R justification templates
- Improved language detection
- User preferences persistence
- Usage statistics

### Planned for 0.3.0
- Referral letter polishing
- Complaint response tone correction
- Practice-wide dashboard
- Multi-user support
- Audit logging

### Future Considerations
- Integration with specific PM systems (R4, SOE, etc.)
- Fine-tuned dental models
- Voice input support
- Mobile app
- Multi-practice management

---

## Version History

### Version Numbering
- **Major (X.0.0)**: Breaking changes, major new features
- **Minor (0.X.0)**: New features, backwards compatible
- **Patch (0.0.X)**: Bug fixes, minor improvements

### Release Notes Format
- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Features that will be removed
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements
