import sys
from pathlib import Path
from PyQt6.QtWidgets import (QLabel, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QListWidget, QFrame, QSlider, QTabWidget, 
                             QScrollArea, QGridLayout, QColorDialog)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QColor

# Подключаем твой SDK
CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "models" / "apps"))

import MIOSORPIOS

class CapPyPro(MIOSORPIOS.HyperApp):
    def __init__(self):
        super().__init__(title="CapPy Pro - Advanced Video Suite")
        self.setMinimumSize(1100, 750)
        self.init_ui()

    def init_ui(self):
        # Глобальный стиль (Modern Dark)
        self.content.setStyleSheet("background-color: #0F0F0F; color: #FFFFFF; font-family: 'Segoe UI';")
        
        # --- ВЕРХНЯЯ ПАНЕЛЬ (Toolbar) ---
        top_bar = QHBoxLayout()
        tools = ["Файл", "Правка", "Проект", "Настройки", "Экспорт", "Помощь"]
        for tool in tools:
            btn = QPushButton(tool)
            btn.setStyleSheet("background: transparent; padding: 5px 15px; font-size: 12px;")
            top_bar.addWidget(btn)
        top_bar.addStretch()
        self.layout.addLayout(top_bar)

        # --- ОСНОВНОЙ КОНТЕНТ (H-Layout) ---
        main_layout = QHBoxLayout()

        # 1. ПАНЕЛЬ ИНСТРУМЕНТОВ И ЭФФЕКТОВ (Слева)
        self.side_tabs = QTabWidget()
        self.side_tabs.setFixedWidth(350)
        self.side_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #222; background: #181818; }
            QTabBar::tab { background: #252525; padding: 10px; min-width: 60px; }
            QTabBar::tab:selected { background: #2ecc71; color: black; }
        """)

        # Добавляем вкладки (Группировка функций)
        self.side_tabs.addTab(self.create_media_tab(), "Медиа")
        self.side_tabs.addTab(self.create_effects_tab(), "Эффекты")
        self.side_tabs.addTab(self.create_text_tab(), "Текст")
        self.side_tabs.addTab(self.create_draw_tab(), "Рисование")
        
        # 2. МОНИТОР ПРЕДПРОСМОТРА (Центр)
        preview_area = QVBoxLayout()
        self.screen = QFrame()
        self.screen.setMinimumSize(400, 300)
        self.screen.setStyleSheet("background: #000; border: 1px solid #333; border-radius: 10px;")
        
        # Контроллеры (Play, Pause, Step)
        controls = QHBoxLayout()
        btns = ["⏪", "◀", "▶", "⏸", "⏩", "📸", "🔁"]
        for b in btns:
            pb = QPushButton(b)
            pb.setFixedSize(40, 40)
            pb.setStyleSheet("background: #222; border-radius: 20px; font-size: 16px;")
            controls.addWidget(pb)
        
        preview_area.addWidget(self.screen, 4)
        preview_area.addLayout(controls, 1)

        main_layout.addWidget(self.side_tabs)
        main_layout.addLayout(preview_area)
        self.layout.addLayout(main_layout)

        # --- ТАЙМЛАЙН (Снизу) ---
        self.setup_timeline()

    def create_media_tab(self):
        w = QFrame()
        l = QVBoxLayout()
        l.addWidget(QLabel("Библиотека (1-8 функции)"))
        l.addWidget(QPushButton("📥 Импорт Видео"))
        l.addWidget(QPushButton("🎙 Запись Аудио"))
        l.addWidget(QPushButton("🖼 Сток Фото"))
        l.addWidget(QPushButton("☁ Облако"))
        l.addWidget(QListWidget())
        w.setLayout(l)
        return w

    def create_effects_tab(self):
        scroll = QScrollArea()
        grid_w = QFrame()
        grid = QGridLayout(grid_w)
        
        effects = [
            "Блюр", "ЧБ", "Глитч", "HDR", "Тряска", 
            "Ретро", "Зерно", "Виньетка", "Зум", "Рыбий глаз",
            "SlowMo", "Reverse", "Стабилизация", "Маска"
        ] # Функции 9-22
        
        for i, name in enumerate(effects):
            btn = QPushButton(name)
            btn.setFixedSize(80, 80)
            btn.setStyleSheet("background: #333; border: 1px solid #444; font-size: 10px;")
            grid.addWidget(btn, i // 3, i % 3)
            
        scroll.setWidget(grid_w)
        return scroll

    def create_text_tab(self):
        w = QFrame()
        l = QVBoxLayout() # Функции 23-28
        l.addWidget(QLabel("Титры и Субтитры"))
        l.addWidget(QPushButton("➕ Добавить Текст"))
        l.addWidget(QPushButton("💬 Авто-субтитры"))
        l.addWidget(QPushButton("✨ 3D Текст"))
        l.addWidget(QPushButton("🎨 Стиль шрифта"))
        l.addWidget(QLabel("Анимация появления:"))
        l.addWidget(QSlider(Qt.Orientation.Horizontal))
        l.addStretch()
        w.setLayout(l)
        return w

    def create_draw_tab(self):
        w = QFrame()
        l = QVBoxLayout() # Функции 29-33+
        l.addWidget(QLabel("Инструменты рисования"))
        l.addWidget(QPushButton("🖌 Кисть"))
        l.addWidget(QPushButton("📏 Ластик"))
        l.addWidget(QPushButton("🖍 Маркер"))
        
        color_btn = QPushButton("Выбрать цвет")
        color_btn.clicked.connect(lambda: QColorDialog.getColor())
        l.addWidget(color_btn)
        
        l.addWidget(QLabel("Толщина линии:"))
        l.addWidget(QSlider(Qt.Orientation.Horizontal))
        l.addStretch()
        w.setLayout(l)
        return w

    def setup_timeline(self):
        timeline = QVBoxLayout()
        # Слои (Tracks)
        for i in range(3):
            track = QFrame()
            track.setFixedHeight(40)
            track.setStyleSheet(f"background: #181818; border-bottom: 1px solid #333;")
            timeline.addWidget(track)
        
        self.layout.addLayout(timeline)

if __name__ == "__main__":
    MIOSORPIOS.run(CapPyPro)