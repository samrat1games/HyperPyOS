import sys
import ctypes
from pathlib import Path
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QFrame, QHBoxLayout, QPushButton, QApplication
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt

user32 = ctypes.windll.user32

class HyperApp(QMainWindow):
    def __init__(self, title="Orange App"):
        super().__init__()
        
        self.setWindowTitle(title) # Заголовок для идентификации в Shell
        self.is_fullscreen = False 
        
        # Флаги: Без рамок + Своё поведение в таскбаре
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowMinMaxButtonsHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Главный контейнер
        self.main_frame = QFrame()
        self.main_frame.setStyleSheet("background-color: #ffffff; border-radius: 18px; border: 1px solid #d1d1d6;")
        self.setCentralWidget(self.main_frame)
        
        self.layout = QVBoxLayout(self.main_frame)
        self.layout.setContentsMargins(15, 10, 15, 15)
        
        # Кнопки управления (Светофор)
        self.setup_title_bar()

        self.content = QWidget()
        self.layout.addWidget(self.content)
        self.font_family = "Segoe UI"
        self.setFont(QFont(self.font_family, 11))

    def setup_title_bar(self):
        self.title_bar = QHBoxLayout()
        
        # Закрыть
        self.close_btn = QPushButton()
        self.close_btn.setFixedSize(12, 12)
        self.close_btn.setStyleSheet("background-color: #ff5f57; border-radius: 6px; border: none;")
        self.close_btn.clicked.connect(self.close)
        
        # Скрыть (Свернуть) — теперь работает системно
        self.min_btn = QPushButton()
        self.min_btn.setFixedSize(12, 12)
        self.min_btn.setStyleSheet("background-color: #ffbd2e; border-radius: 6px; border: none;")
        self.min_btn.clicked.connect(self.showMinimized)

        # Развернуть
        self.max_btn = QPushButton()
        self.max_btn.setFixedSize(12, 12)
        self.max_btn.setStyleSheet("background-color: #28c840; border-radius: 6px; border: none;")
        self.max_btn.clicked.connect(self.toggle_full_screen)

        self.title_bar.addWidget(self.close_btn)
        self.title_bar.addWidget(self.min_btn)
        self.title_bar.addWidget(self.max_btn)
        self.title_bar.addStretch()
        self.layout.addLayout(self.title_bar)

    def toggle_full_screen(self):
        if not self.is_fullscreen:
            self.showFullScreen()
            self.main_frame.setStyleSheet("background-color: #ffffff; border-radius: 0px; border: none;")
            self.is_fullscreen = True
        else:
            self.showNormal()
            self.main_frame.setStyleSheet("background-color: #ffffff; border-radius: 18px; border: 1px solid #d1d1d6;")
            self.is_fullscreen = False

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() < 45:
            if not self.is_fullscreen:
                self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_pos'):
            if not self.is_fullscreen:
                self.move(event.globalPosition().toPoint() - self.drag_pos)
                event.accept()

def run(app_class):
    app = QApplication(sys.argv)
    window = app_class()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())