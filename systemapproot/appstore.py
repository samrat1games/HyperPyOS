import sys
from pathlib import Path
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from PyQt6.QtWidgets import (QVBoxLayout, QWidget, QPushButton, QHBoxLayout)

# SDK
CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "models" / "apps"))
import MIOSORPIOS

class AppStore(MIOSORPIOS.HyperApp):
    def __init__(self):
        super().__init__(title="App Store")
        self.setFixedSize(800, 550)
        
        self.dest = PROJECT_ROOT / "apps"
        self.dest.mkdir(exist_ok=True)
        
        self.init_ui()

    def init_ui(self):
        self.content.setStyleSheet("background: white;")
        
        self.webview = QWebEngineView()
        self.webview.load(QUrl("https://samrat1games.github.io/Hyper-Store/"))
        self.webview.page().profile().downloadRequested.connect(self.handle_download)
        
        # Top bar with back button
        top_layout = QHBoxLayout()
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.webview.back)
        top_layout.addWidget(back_button)
        top_layout.addStretch()
        
        self.layout.addLayout(top_layout)
        self.layout.addWidget(self.webview)

    def handle_download(self, download: QWebEngineDownloadRequest):
        download.setDownloadDirectory(str(self.dest))
        download.accept()

if __name__ == "__main__":
    MIOSORPIOS.run(AppStore)