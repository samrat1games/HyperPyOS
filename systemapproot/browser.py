import sys
from pathlib import Path
from PyQt6.QtWidgets import QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "models" / "apps"))
import MIOSORPIOS

class OrangeBrowser(MIOSORPIOS.HyperApp):
    def __init__(self):
        super().__init__(title="Orange Browser")
        self.setFixedSize(1000, 700)
        self.download_path = PROJECT_ROOT / "files" / "download"
        self.download_path.mkdir(parents=True, exist_ok=True)
        self.init_ui()

    def init_ui(self):
        nav = QHBoxLayout()
        self.url_bar = QLineEdit("https://google.com")
        btn = QPushButton("Go")
        btn.clicked.connect(lambda: self.view.setUrl(QUrl(self.url_bar.text())))
        nav.addWidget(self.url_bar); nav.addWidget(btn)
        self.layout.addLayout(nav)

        self.view = QWebEngineView()
        self.view.setUrl(QUrl("https://google.com"))
        # Логика загрузки
        self.view.page().profile().downloadRequested.connect(self.on_download)
        self.layout.addWidget(self.view)

    def on_download(self, item):
        item.setDownloadDirectory(str(self.download_path))
        item.accept()

if __name__ == "__main__":
    MIOSORPIOS.run(OrangeBrowser)