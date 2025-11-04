import sys
import requests
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QLabel, QTextEdit, QPushButton, QSystemTrayIcon, QMenu,
                              QLineEdit, QHBoxLayout, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut, QAction
import pyperclip  # For clipboard operations

# For global hotkey on Windows
try:
    from pynput import keyboard
except ImportError:
    print("Install pynput: pip install pynput")
    sys.exit(1)

class CheckNoteWorker(QThread):
    """Background thread for API calls"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, text, api_url):
        super().__init__()
        self.text = text
        self.api_url = api_url

    def run(self):
        try:
            response = requests.post(
                f"{self.api_url}/check-note",
                json={"text": self.text},
                timeout=10
            )
            response.raise_for_status()
            self.finished.emit(response.json())
        except Exception as e:
            self.error.emit(str(e))

class ResultWindow(QWidget):
    """Floating window to show results"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DentalCorrectIQ - Results")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.resize(600, 500)

        layout = QVBoxLayout()

        # Score display
        self.score_label = QLabel("GDC Score: --")
        self.score_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(self.score_label)

        # Original language
        self.lang_label = QLabel("Detected Language: --")
        self.lang_label.setStyleSheet("font-size: 12px; color: #666; padding: 5px;")
        layout.addWidget(self.lang_label)

        # Corrected text
        layout.addWidget(QLabel("Corrected Text:"))
        self.corrected_text = QTextEdit()
        self.corrected_text.setReadOnly(False)  # Allow editing
        self.corrected_text.setStyleSheet("font-family: monospace; padding: 5px;")
        layout.addWidget(self.corrected_text)

        # Missing elements
        self.missing_label = QLabel("Missing Elements: --")
        self.missing_label.setStyleSheet("color: #d9534f; font-weight: bold; padding: 5px;")
        layout.addWidget(self.missing_label)

        # Suggestions
        layout.addWidget(QLabel("Suggestions:"))
        self.suggestions_text = QTextEdit()
        self.suggestions_text.setReadOnly(True)
        self.suggestions_text.setMaximumHeight(120)
        self.suggestions_text.setStyleSheet("font-size: 11px; padding: 5px;")
        layout.addWidget(self.suggestions_text)

        # Buttons
        button_layout = QHBoxLayout()

        copy_btn = QPushButton("Copy Corrected Text")
        copy_btn.clicked.connect(self.copy_text)
        copy_btn.setStyleSheet("padding: 8px; font-weight: bold;")
        button_layout.addWidget(copy_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.hide)
        close_btn.setStyleSheet("padding: 8px;")
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def show_results(self, data):
        """Display API response"""
        self.corrected_text.setPlainText(data["corrected_text"])

        score = data["gdc_score"]
        color = "green" if score >= 80 else "orange" if score >= 60 else "red"
        self.score_label.setText(f"GDC Compliance Score: {score}/100")
        self.score_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color}; padding: 10px;")

        self.lang_label.setText(f"Detected Language: {data['original_language']}")

        missing = ", ".join(data["missing_elements"]) if data["missing_elements"] else "None"
        self.missing_label.setText(f"Missing Elements: {missing}")

        suggestions = "\n".join(f"• {s}" for s in data["suggestions"])
        self.suggestions_text.setPlainText(suggestions if suggestions else "No suggestions - note looks good!")

        self.show()
        self.activateWindow()
        self.raise_()

    def copy_text(self):
        """Copy corrected text to clipboard"""
        text = self.corrected_text.toPlainText()
        pyperclip.copy(text)
        QMessageBox.information(self, "Copied", "Corrected text copied to clipboard!")

class SettingsWindow(QWidget):
    """Settings window for configuring API URL"""
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("DentalCorrectIQ - Settings")
        self.resize(400, 150)

        layout = QVBoxLayout()

        # API URL setting
        layout.addWidget(QLabel("Server API URL:"))
        self.api_url_input = QLineEdit()
        self.api_url_input.setPlaceholderText("e.g., http://192.168.1.100:8000")
        layout.addWidget(self.api_url_input)

        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def load_settings(self, api_url):
        """Load current settings"""
        self.api_url_input.setText(api_url)

    def save_settings(self):
        """Save settings and update parent"""
        new_url = self.api_url_input.text().strip()
        if new_url:
            self.parent.api_url = new_url
            QMessageBox.information(self, "Saved", f"API URL updated to: {new_url}")
            self.hide()
        else:
            QMessageBox.warning(self, "Error", "Please enter a valid API URL")

class DentalCorrectIQ(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DentalCorrectIQ")
        self.resize(500, 300)

        # Configuration
        self.api_url = "http://localhost:8000"  # Default to localhost for testing

        # Result window
        self.result_window = ResultWindow()

        # Settings window
        self.settings_window = SettingsWindow(self)

        # System tray
        self.setup_tray()

        # Main window (mostly for settings/status)
        central = QWidget()
        layout = QVBoxLayout()

        # Title
        title_label = QLabel("DentalCorrectIQ")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Status
        status_label = QLabel("Status: Running")
        status_label.setStyleSheet("color: green; font-size: 14px;")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(status_label)

        # Instructions
        info_label = QLabel("How to use:\n1. Select text in any application\n2. Copy it (Ctrl+C)\n3. Press Ctrl+Shift+G")
        info_label.setStyleSheet("padding: 20px; background-color: #f0f0f0; border-radius: 5px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        # Test section
        layout.addWidget(QLabel("\nTest the system:"))
        self.test_input = QTextEdit()
        self.test_input.setPlaceholderText("Enter test text here (e.g., 'pt c/o pain ul6 ttp')")
        self.test_input.setMaximumHeight(80)
        layout.addWidget(self.test_input)

        # Buttons
        button_layout = QHBoxLayout()

        test_btn = QPushButton("Test This Text")
        test_btn.clicked.connect(self.test_current_text)
        test_btn.setStyleSheet("padding: 10px; font-weight: bold;")
        button_layout.addWidget(test_btn)

        conn_btn = QPushButton("Test Connection")
        conn_btn.clicked.connect(self.test_connection)
        conn_btn.setStyleSheet("padding: 10px;")
        button_layout.addWidget(conn_btn)

        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(self.show_settings)
        settings_btn.setStyleSheet("padding: 10px;")
        button_layout.addWidget(settings_btn)

        layout.addLayout(button_layout)

        central.setLayout(layout)
        self.setCentralWidget(central)

        # Setup global hotkey
        self.setup_hotkey()

    def setup_tray(self):
        """System tray icon"""
        self.tray = QSystemTrayIcon(self)
        # Note: Add an icon file for better UX
        # self.tray.setIcon(QIcon("icon.png"))

        menu = QMenu()
        show_action = menu.addAction("Show Window")
        show_action.triggered.connect(self.show)

        settings_action = menu.addAction("Settings")
        settings_action.triggered.connect(self.show_settings)

        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(QApplication.quit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self.tray_clicked)
        self.tray.show()

    def tray_clicked(self, reason):
        """Handle tray icon clicks"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()

    def setup_hotkey(self):
        """Global hotkey listener"""
        def on_activate():
            """Called when Ctrl+Shift+G pressed"""
            # Get selected text from clipboard (user must copy first)
            text = pyperclip.paste()
            if text and text.strip():
                self.check_note(text)
            else:
                print("No text in clipboard")

        # Register hotkey
        hotkey = keyboard.GlobalHotKeys({
            '<ctrl>+<shift>+g': on_activate
        })
        hotkey.start()

    def check_note(self, text):
        """Send text to API for checking"""
        self.worker = CheckNoteWorker(text, self.api_url)
        self.worker.finished.connect(self.result_window.show_results)
        self.worker.error.connect(self.show_error)
        self.worker.start()

    def show_error(self, error_msg):
        """Show error message"""
        QMessageBox.critical(self, "Error", f"Failed to check note:\n{error_msg}\n\nCheck if server is running at {self.api_url}")

    def test_current_text(self):
        """Test text from input field"""
        text = self.test_input.toPlainText().strip()
        if text:
            self.check_note(text)
        else:
            QMessageBox.warning(self, "No Text", "Please enter some text to test")

    def test_connection(self):
        """Test API connection"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            response.raise_for_status()
            data = response.json()
            QMessageBox.information(
                self,
                "Connection Success",
                f"Connected to server!\n\nStatus: {data.get('status', 'unknown')}\nModel: {data.get('model', 'unknown')}\nOllama: {data.get('ollama_status', 'unknown')}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Connection Failed",
                f"Cannot connect to server at {self.api_url}\n\nError: {str(e)}\n\nPlease check:\n1. Server is running\n2. URL is correct\n3. Network connection"
            )

    def show_settings(self):
        """Show settings window"""
        self.settings_window.load_settings(self.api_url)
        self.settings_window.show()

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running in tray

    window = DentalCorrectIQ()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
