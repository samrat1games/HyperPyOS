import sys
import os
from pathlib import Path

# --- КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ ПУТЕЙ ---
CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

sys.path.insert(0, str(PROJECT_ROOT / "models" / "apps"))

from PyQt6.QtWidgets import (QLabel, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QScrollArea, QWidget, QFrame, QStackedWidget, QListWidget, QSlider, QLineEdit)
from PyQt6.QtCore import Qt

import MIOSORPIOS
try:
    from datasystemroot import shell
except ImportError:
    shell = None

class SettingsApp(MIOSORPIOS.HyperApp):
    def __init__(self):
        super().__init__(title="HyperPy Settings")
        self.setFixedSize(720, 520)
        self.license_key = "qhtywcosgokdjhogkluisgdjikpl"
        self.init_ui()

    def init_ui(self):
        # Исправление ошибки QLayout:
        # У self.content уже есть layout из MIOSORPIOS. Используем его.
        self.content.setStyleSheet("background-color: #f5f5f7;")
        
        # Создаем горизонтальный контейнер для сайдбара и контента
        main_container = QHBoxLayout()
        main_container.setContentsMargins(0, 0, 0, 0)
        main_container.setSpacing(0)
        
        # Добавляем его в существующий вертикальный layout контента
        self.layout.addLayout(main_container)

        # Сайдбар
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(190)
        self.sidebar.setStyleSheet("""
            QListWidget { background: #f2f2f7; border: none; border-right: 1px solid #d1d1d6; color: #1d1d1f; }
            QListWidget::item { padding: 15px; border-radius: 8px; margin: 2px 5px; }
            QListWidget::item:selected { background: #0071e3; color: white; }
        """)
        self.sidebar.addItems(["📶 Wi-Fi", "🔹 Bluetooth", "🖼️ Обои", "ℹ️ О системе", "🔑 Лицензия"])
        self.sidebar.currentRowChanged.connect(self.display_page)

        # Страницы
        self.pages = QStackedWidget()
        self.pages.addWidget(self.create_info_page("Wi-Fi", "Статус: Подключено к GalaxyMod_5G"))
        self.pages.addWidget(self.create_info_page("Bluetooth", "Активных устройств не найдено."))
        self.pages.addWidget(self.create_wallpaper_page())
        self.pages.addWidget(self.create_info_page("О системе", "HyperPy OS 1.3.0 PRO\nBuild: 2026\nKernel: Py3.14"))
        self.pages.addWidget(self.create_license_page())

        main_container.addWidget(self.sidebar)
        main_container.addWidget(self.pages)
        
        self.sidebar.setCurrentRow(0)

    def display_page(self, index):
        self.pages.setCurrentIndex(index)

    def create_info_page(self, title, content):
        p = QWidget(); l = QVBoxLayout(p); l.setContentsMargins(30,30,30,30)
        t = QLabel(title); t.setStyleSheet("font-size: 24px; font-weight: bold; color: #1d1d1f;")
        c = QLabel(content); c.setStyleSheet("font-size: 14px; color: #48484a; margin-top: 10px;")
        l.addWidget(t); l.addWidget(c); l.addStretch(); return p

    def create_wallpaper_page(self):
        p = QWidget(); l = QVBoxLayout(p); l.setContentsMargins(30,30,30,30)
        l.addWidget(QLabel("Выбор обоев", styleSheet="font-size: 24px; font-weight: bold; color: #1d1d1f;"))
        
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFixedHeight(150); scroll.setStyleSheet("border:none;")
        container = QWidget(); wall_layout = QHBoxLayout(container)
        
        wp_path = PROJECT_ROOT / "data" / "wallpaper"
        if wp_path.exists():
            for img_file in wp_path.glob("*.jpg"):
                btn = QPushButton(img_file.name)
                btn.setFixedSize(110, 70)
                btn.setStyleSheet("background: white; border: 1px solid #d1d1d6; border-radius: 8px; color: #1d1d1f;")
                btn.clicked.connect(lambda ch, n=img_file.name: shell.instance.change_wallpaper(n) if shell and shell.instance else None)
                wall_layout.addWidget(btn)
        
        scroll.setWidget(container); l.addWidget(scroll); l.addStretch(); return p

    def create_license_page(self):
        p = QWidget(); l = QVBoxLayout(p); l.setContentsMargins(30,30,30,30)
        l.addWidget(QLabel("Активация", styleSheet="font-size: 24px; font-weight: bold; color: #1d1d1f;"))
        self.input = QLineEdit(); self.input.setPlaceholderText("Введите ключ..."); self.input.setStyleSheet("padding: 12px; background: white; border: 1px solid #d1d1d6; border-radius: 8px; margin-top: 20px; color: black;")
        btn = QPushButton("Активировать"); btn.setStyleSheet("background: #34c759; color: white; padding: 12px; border-radius: 8px; font-weight: bold; margin-top: 10px;")
        btn.clicked.connect(self.check_license)
        self.res = QLabel(""); l.addWidget(self.input); l.addWidget(btn); l.addWidget(self.res); l.addStretch(); return p

    def check_license(self):
        if self.input.text() == self.license_key:
            self.res.setText("✅ Система успешно активирована!"); self.res.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.res.setText("❌ Неверный ключ."); self.res.setStyleSheet("color: red;")

if __name__ == "__main__":
    MIOSORPIOS.run(SettingsApp)