import sys
import ctypes
from pathlib import Path
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QFrame, QHBoxLayout, QPushButton
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtCore import Qt

# Windows API для работы с панелью задач
user32 = ctypes.windll.user32

def hide_windows_taskbar():
    handle = user32.FindWindowW("Shell_TrayWnd", None)
    user32.ShowWindow(handle, 0) # 0 = Скрыть

class HyperApp(QMainWindow):
    def __init__(self, title="Orange App"):
        super().__init__()
        
        # ПРИ ЗАПУСКЕ ЛЮБОГО ПРИЛОЖЕНИЯ СКРЫВАЕМ ПАНЕЛЬ WINDOWS
        hide_windows_taskbar()
        
        self.setup_apple_assets()
        
        # Настройка окна: Поверх всех + Без рамок
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint # Это окно всегда выше панели Windows
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.main_frame = QFrame()
        self.main_frame.setStyleSheet("background-color: #ffffff; border-radius: 18px; border: 1px solid #d1d1d6;")
        self.setCentralWidget(self.main_frame)
        
        self.layout = QVBoxLayout(self.main_frame)
        self.layout.setContentsMargins(15, 10, 15, 15)
        
        # Кнопки управления (Светофор)
        self.title_bar = QHBoxLayout()
        self.close_btn = QPushButton()
        self.close_btn.setFixedSize(12, 12)
        self.close_btn.setStyleSheet("background-color: #ff5f57; border-radius: 6px; border: none;")
        self.close_btn.clicked.connect(self.close)
        
        self.min_btn = QPushButton()
        self.min_btn.setFixedSize(12, 12)
        self.min_btn.setStyleSheet("background-color: #ffbd2e; border-radius: 6px; border: none;")
        self.min_btn.clicked.connect(self.showMinimized)

        self.title_bar.addWidget(self.close_btn)
        self.title_bar.addWidget(self.min_btn)
        self.title_bar.addStretch()
        self.layout.addLayout(self.title_bar)

        self.content = QWidget()
        self.layout.addWidget(self.content)
        self.setFont(QFont(self.font_family, 11))

    def setup_apple_assets(self):
        fonts_dir = Path(__file__).parent.parent.parent / "files" / "fonts"
        sf_path = fonts_dir / "SF-Pro.otf"
        if sf_path.exists():
            fid = QFontDatabase.addApplicationFont(str(sf_path))
            self.font_family = QFontDatabase.applicationFontFamilies(fid)[0]
        else:
            self.font_family = "Segoe UI"

    # ПЕРЕТАСКИВАНИЕ
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() < 45:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_pos'):
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

def run(app_class):
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = app_class()
    window.show()
    sys.exit(app.exec())