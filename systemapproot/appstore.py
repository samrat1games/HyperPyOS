import sys, shutil
from pathlib import Path
from PyQt6.QtWidgets import (QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QWidget, QFrame, QGridLayout)
from PyQt6.QtCore import Qt

# SDK
CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "models" / "apps"))
import MIOSORPIOS

class AppStore(MIOSORPIOS.HyperApp):
    def __init__(self):
        super().__init__(title="App Store")
        self.setFixedSize(800, 550)
        
        # ПУТИ, КОТОРЫЕ ТЫ ПРОСИЛ
        self.repo = PROJECT_ROOT / "appstore" # ОТКУДА
        self.dest = PROJECT_ROOT / "apps"     # КУДА (в корень)
        
        self.repo.mkdir(exist_ok=True)
        self.dest.mkdir(exist_ok=True)
        
        self.init_ui()

    def init_ui(self):
        self.content.setStyleSheet("background: white;")
        header = QLabel("Galaxy Store"); header.setStyleSheet("font-size: 28px; font-weight: bold; margin: 15px;")
        self.layout.addWidget(header)

        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("border: none;")
        container = QWidget(); self.grid = QGridLayout(container)
        
        self.refresh_store()
        
        scroll.setWidget(container); self.layout.addWidget(scroll)

    def refresh_store(self):
        for i in reversed(range(self.grid.count())): self.grid.itemAt(i).widget().setParent(None)
        
        apps = list(self.repo.glob("*.py"))
        row, col = 0, 0
        for app in apps:
            installed = (self.dest / app.name).exists()
            card = self.create_card(app, installed)
            self.grid.addWidget(card, row, col)
            col += 1
            if col > 2: col = 0; row += 1

    def create_card(self, path, installed):
        f = QFrame(); f.setFixedSize(230, 80); f.setStyleSheet("background: #f0f0f2; border-radius: 10px;")
        l = QHBoxLayout(f)
        
        txt = QVBoxLayout(); name = QLabel(path.stem); name.setStyleSheet("font-weight: bold; color: black;")
        txt.addWidget(name); l.addLayout(txt)
        
        btn = QPushButton("OPEN" if installed else "GET")
        btn.setFixedSize(60, 25)
        btn.setStyleSheet("background: #0071e3; color: white; font-weight: bold; border-radius: 12px;" if not installed else "background: #d1d1d6; color: #555; border-radius: 12px;")
        
        if not installed:
            btn.clicked.connect(lambda ch, p=path: self.install(p))
        
        l.addWidget(btn); return f

    def install(self, path):
        shutil.copy(path, self.dest / path.name)
        self.refresh_store()

if __name__ == "__main__":
    MIOSORPIOS.run(AppStore)