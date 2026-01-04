import sys, os, shutil
from pathlib import Path
from PyQt6.QtWidgets import (QLabel, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QFrame, QScrollArea, QWidget, QMessageBox, QGridLayout)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "models" / "apps"))
import MIOSORPIOS

class OrangeExplorer(MIOSORPIOS.HyperApp):
    def __init__(self):
        super().__init__(title="Orange Explorer")
        self.setFixedSize(850, 600) # Увеличили размер окна
        self.base_path = PROJECT_ROOT / "files"
        self.current_dir = self.base_path
        self.init_ui()
        self.refresh_list()

    def init_ui(self):
        self.content.setStyleSheet("background-color: #ffffff;")
        
        # Главный горизонтальный макет (Боковая панель + Контент)
        self.main_layout = QHBoxLayout(self.content)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. БОКОВАЯ ПАНЕЛЬ (SIDEBAR)
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(180)
        self.sidebar.setStyleSheet("""
            QFrame { 
                background-color: #f2f2f7; 
                border-right: 1px solid #d1d1d6; 
                border-bottom-left-radius: 18px; 
            }
        """)
        side_layout = QVBoxLayout(self.sidebar)
        side_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Кнопки быстрого доступа
        self.add_side_btn(side_layout, "􀈕 Файлы", self.base_path)
        self.add_side_btn(side_layout, "􀎠 Система", self.base_path / "HyperPyOS")
        self.add_side_btn(side_layout, "􀉤 Юзер", self.base_path / "user")
        
        self.main_layout.addWidget(self.sidebar)

        # 2. ПРАВАЯ ЧАСТЬ (КОНТЕНТ)
        right_widget = QWidget()
        self.right_layout = QVBoxLayout(right_widget)
        
        # Верхняя панель управления (Toolbar)
        toolbar = QHBoxLayout()
        self.back_btn = QPushButton("􀄪")
        self.back_btn.setFixedSize(35, 35)
        self.back_btn.setStyleSheet("background: transparent; font-size: 18px; color: #007aff; border: none;")
        self.back_btn.clicked.connect(self.go_back)
        
        self.path_lbl = QLabel("/files")
        self.path_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #1c1c1e;")
        
        toolbar.addWidget(self.back_btn)
        toolbar.addWidget(self.path_lbl)
        toolbar.addStretch()
        self.right_layout.addLayout(toolbar)

        # Область прокрутки для файлов
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none; background: white;")
        
        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll.setWidget(self.list_widget)
        self.right_layout.addWidget(self.scroll)
        
        # Статус-бар внизу
        self.status_bar = QLabel("Элементов: 0")
        self.status_bar.setStyleSheet("color: #8e8e93; font-size: 11px; padding: 5px;")
        self.right_layout.addWidget(self.status_bar)

        self.main_layout.addWidget(right_widget)

    def add_side_btn(self, layout, text, path):
        btn = QPushButton(text)
        btn.setStyleSheet("""
            QPushButton { 
                text-align: left; padding: 10px; border: none; 
                border-radius: 8px; color: #1c1c1e; font-weight: 500; 
            }
            QPushButton:hover { background-color: #e5e5ea; }
        """)
        btn.clicked.connect(lambda: self.enter_dir(path))
        layout.addWidget(btn)

    def refresh_list(self):
        for i in reversed(range(self.list_layout.count())): 
            self.list_layout.itemAt(i).widget().setParent(None)

        self.path_lbl.setText(f"OrangeOS › {self.current_dir.name}")

        try:
            items = sorted(os.listdir(self.current_dir))
            self.status_bar.setText(f"Элементов: {len(items)}")
            
            for item in items:
                self.create_item_row(item)
        except Exception as e:
            self.list_layout.addWidget(QLabel(f"Ошибка: {e}"))

    def create_item_row(self, name):
        full_path = self.current_dir / name
        is_dir = full_path.is_dir()
        
        row = QFrame()
        row.setStyleSheet("""
            QFrame { background: #ffffff; border-bottom: 1px solid #f2f2f7; }
            QFrame:hover { background: #f9f9fb; }
        """)
        l = QHBoxLayout(row)
        
        # Красивая иконка
        icon_lbl = QLabel("📁" if is_dir else "📄")
        icon_lbl.setStyleSheet("font-size: 20px; border: none;")
        
        name_btn = QPushButton(name)
        name_btn.setStyleSheet("text-align: left; border: none; color: black; font-weight: 500; font-size: 13px;")
        if is_dir:
            name_btn.clicked.connect(lambda: self.enter_dir(full_path))
        
        l.addWidget(icon_lbl)
        l.addWidget(name_btn)
        l.addStretch()

        # Проверка защиты Orange System
        is_protected = any(x in str(full_path) for x in ["HyperPyOS", "user", "fonts"])
        
        if is_protected:
            lock = QLabel("􀎠 System")
            lock.setStyleSheet("color: #ff9500; font-weight: bold; font-size: 10px; border: none;")
            l.addWidget(lock)
        else:
            del_btn = QPushButton("Удалить")
            del_btn.setFixedSize(75, 25)
            del_btn.setStyleSheet("""
                QPushButton { background: #f2f2f7; color: #ff3b30; border-radius: 6px; font-weight: bold; }
                QPushButton:hover { background: #ff3b30; color: white; }
            """)
            del_btn.clicked.connect(lambda ch, p=full_path: self.delete_item(p))
            l.addWidget(del_btn)
            
        self.list_layout.addWidget(row)

    def enter_dir(self, path):
        if path.exists():
            self.current_dir = path
            self.refresh_list()

    def go_back(self):
        if self.current_dir != self.base_path:
            self.current_dir = self.current_dir.parent
            self.refresh_list()

    def delete_item(self, path):
        if QMessageBox.question(self, "OrangeOS", f"Удалить {path.name}?") == QMessageBox.StandardButton.Yes:
            try:
                if path.is_dir(): shutil.rmtree(path)
                else: os.remove(path)
                self.refresh_list()
            except Exception as e:
                QMessageBox.critical(self, "Доступ запрещен", f"{e}")

if __name__ == "__main__":
    MIOSORPIOS.run(OrangeExplorer)