import sys, os, shutil, importlib.util
from pathlib import Path
from PyQt6.QtWidgets import (QLabel, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QFrame, QScrollArea, QWidget, QMessageBox, 
                             QLineEdit, QTextEdit)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parent.parent 
sys.path.insert(0, str(PROJECT_ROOT / "models" / "apps"))

import MIOSORPIOS

class OrangeExplorer(MIOSORPIOS.HyperApp):
    def __init__(self):
        super().__init__(title="Orange Explorer Pro")
        self.setFixedSize(900, 650)
        self.base_path = PROJECT_ROOT 
        self.current_dir = self.base_path
        
        self.init_ui()
        self.init_overlays() 
        self.refresh_list()

    def init_ui(self):
        self.content.setStyleSheet("background-color: #ffffff;")
        self.layout_container = QWidget(self.content)
        self.layout_container.setGeometry(0, 0, 900, 650)
        
        self.main_layout = QHBoxLayout(self.layout_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- 1. SIDEBAR (Боковая панель) ---
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(180)
        self.sidebar.setStyleSheet("""
            QFrame { background-color: #f2f2f7; border-right: 1px solid #d1d1d6; }
            QPushButton { 
                text-align: left; padding: 10px; border: none; 
                color: #000000; font-size: 13px; font-weight: bold; background: transparent;
            }
            QPushButton:hover { background-color: #e5e5ea; border-radius: 5px; }
        """)
        
        side_layout = QVBoxLayout(self.sidebar)
        side_layout.setContentsMargins(10, 15, 10, 15)
        side_layout.setSpacing(5)

        # Навигация
        self.add_side_btn(side_layout, "[ ROOT ]", self.base_path)
        self.add_side_btn(side_layout, "[ FILES ]", self.base_path / "files")
        self.add_side_btn(side_layout, "[ SYSTEM ]", self.base_path / "files" / "HyperPyOS")
        
        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #d1d1d6;")
        side_layout.addWidget(line)

        # КНОПКИ СОЗДАНИЯ (Теперь сверху и с черным текстом)
        create_btn_style = """
            QPushButton { 
                background: #e5e5ea; border: 1px solid #c7c7cc; 
                border-radius: 6px; padding: 8px; color: #000000;
            }
            QPushButton:hover { background: #d1d1d6; }
        """

        self.btn_new_file = QPushButton("NEW FILE")
        self.btn_new_file.setStyleSheet(create_btn_style)
        self.btn_new_file.clicked.connect(lambda: self.show_input_overlay("FILE"))
        
        self.btn_new_folder = QPushButton("NEW FOLDER")
        self.btn_new_folder.setStyleSheet(create_btn_style)
        self.btn_new_folder.clicked.connect(lambda: self.show_input_overlay("FOLDER"))
        
        side_layout.addWidget(self.btn_new_file)
        side_layout.addWidget(self.btn_new_folder)
        
        side_layout.addStretch() # Пружина уходит вниз
        self.main_layout.addWidget(self.sidebar)

        # --- 2. CONTENT AREA ---
        right_widget = QWidget()
        self.right_layout = QVBoxLayout(right_widget)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        
        toolbar = QFrame()
        toolbar.setFixedHeight(45)
        toolbar.setStyleSheet("background: white; border-bottom: 1px solid #e0e0e0;")
        t_layout = QHBoxLayout(toolbar)
        
        self.back_btn = QPushButton("< BACK")
        self.back_btn.setStyleSheet("border: none; font-weight: bold; color: #007aff;")
        self.back_btn.clicked.connect(self.go_back)
        
        self.path_lbl = QLabel("/")
        self.path_lbl.setStyleSheet("font-family: 'Consolas'; color: #333; font-size: 11px;")
        
        t_layout.addWidget(self.back_btn)
        t_layout.addWidget(self.path_lbl)
        t_layout.addStretch()
        self.right_layout.addWidget(toolbar)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none; background: white;")
        
        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.list_layout.setSpacing(0)
        
        self.scroll.setWidget(self.list_widget)
        self.right_layout.addWidget(self.scroll)
        self.main_layout.addWidget(right_widget)

    def init_overlays(self):
        self.overlay_bg = QFrame(self.content)
        self.overlay_bg.setGeometry(0, 0, 900, 650)
        self.overlay_bg.setStyleSheet("background: rgba(0, 0, 0, 0.6);")
        self.overlay_bg.hide()

        self.input_panel = QFrame(self.content)
        self.input_panel.setFixedSize(320, 150)
        self.input_panel.move(290, 250)
        self.input_panel.setStyleSheet("""
            QFrame { background: #1c1c1e; border-radius: 12px; border: 1px solid #3a3a3c; }
            QLabel { color: white; border: none; font-weight: bold; }
            QLineEdit { background: #2c2c2e; color: white; padding: 8px; border-radius: 6px; }
        """)
        self.input_panel.hide()
        
        ip_layout = QVBoxLayout(self.input_panel)
        self.ip_title = QLabel("CREATE NEW")
        self.ip_input = QLineEdit()
        
        btn_box = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet("background: #0a84ff; color: white; font-weight: bold; padding: 5px; border-radius: 5px;")
        ok_btn.clicked.connect(self.process_input_overlay)
        
        cancel_btn = QPushButton("CANCEL")
        cancel_btn.setStyleSheet("background: #3a3a3c; color: white; padding: 5px; border-radius: 5px;")
        cancel_btn.clicked.connect(self.hide_overlay)
        
        btn_box.addWidget(cancel_btn)
        btn_box.addWidget(ok_btn)
        
        ip_layout.addWidget(self.ip_title)
        ip_layout.addWidget(self.ip_input)
        ip_layout.addLayout(btn_box)

        # Редактор кода
        self.editor_panel = QFrame(self.content)
        self.editor_panel.setGeometry(50, 50, 800, 550)
        self.editor_panel.setStyleSheet("background: #1e1e1e; border-radius: 10px; border: 1px solid #333;")
        self.editor_panel.hide()
        
        ed_layout = QVBoxLayout(self.editor_panel)
        self.ed_text = QTextEdit()
        self.ed_text.setStyleSheet("color: #d4d4d4; font-family: 'Consolas'; border: none; font-size: 14px; background: transparent;")
        
        self.ed_save_btn = QPushButton("SAVE AND CLOSE")
        self.ed_save_btn.setStyleSheet("background: #28a745; color: white; padding: 10px; font-weight: bold; border-radius: 5px;")
        
        ed_layout.addWidget(self.ed_text)
        ed_layout.addWidget(self.ed_save_btn)

    def show_input_overlay(self, mode):
        self.input_mode = mode
        self.ip_title.setText(f"NEW {mode}")
        self.ip_input.clear()
        self.overlay_bg.show()
        self.input_panel.show()
        self.input_panel.raise_()
        self.ip_input.setFocus()

    def process_input_overlay(self):
        name = self.ip_input.text().strip()
        if name:
            try:
                path = self.current_dir / name
                if self.input_mode == "FILE":
                    path.touch()
                    self.refresh_list()
                    self.open_internal_editor(path)
                else:
                    path.mkdir(exist_ok=True)
                    self.refresh_list()
            except Exception as e: print(e)
        self.hide_overlay()

    def open_internal_editor(self, path):
        self.current_editing_path = path
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.ed_text.setPlainText(f.read())
        except: self.ed_text.setPlainText("")
        self.overlay_bg.show()
        self.editor_panel.show()
        self.editor_panel.raise_()
        try: self.ed_save_btn.clicked.disconnect()
        except: pass
        self.ed_save_btn.clicked.connect(self.save_internal_editor)

    def save_internal_editor(self):
        try:
            with open(self.current_editing_path, 'w', encoding='utf-8') as f:
                f.write(self.ed_text.toPlainText())
        except: pass
        self.hide_overlay()

    def hide_overlay(self):
        self.overlay_bg.hide()
        self.input_panel.hide()
        self.editor_panel.hide()

    def add_side_btn(self, layout, text, path):
        btn = QPushButton(text)
        btn.clicked.connect(lambda: self.enter_dir(path))
        layout.addWidget(btn)

    def refresh_list(self):
        for i in reversed(range(self.list_layout.count())): 
            w = self.list_layout.itemAt(i).widget()
            if w: w.setParent(None)
        self.path_lbl.setText(f" PATH: {self.current_dir}")
        try:
            items = sorted(os.listdir(self.current_dir))
            for item in items:
                self.create_item_row(item)
        except: pass

    def create_item_row(self, name):
        full_path = self.current_dir / name
        is_dir = full_path.is_dir()
        row = QFrame()
        row.setFixedHeight(35)
        row.setStyleSheet("QFrame { background: white; border-bottom: 1px solid #f0f0f0; } QFrame:hover { background: #f9f9fb; }")
        l = QHBoxLayout(row)
        l.setContentsMargins(10, 0, 10, 0)
        
        type_mark = "[DIR] " if is_dir else "[FILE]"
        name_btn = QPushButton(f"{type_mark} {name}")
        name_btn.setStyleSheet("text-align: left; border: none; color: black; font-size: 13px; font-weight: normal;")
        
        if is_dir: 
            name_btn.clicked.connect(lambda: self.enter_dir(full_path))
        else: 
            # Запуск .py как приложения или открытие в редакторе
            if name.endswith(".py"):
                name_btn.clicked.connect(lambda: self.run_py_file(full_path))
            else:
                name_btn.clicked.connect(lambda: self.open_internal_editor(full_path))
        
        l.addWidget(name_btn)
        l.addStretch()
        
        del_btn = QPushButton("X")
        del_btn.setFixedSize(22, 22)
        del_btn.setStyleSheet("color: red; border: 1px solid red; border-radius: 4px; font-weight: bold;")
        del_btn.clicked.connect(lambda: self.delete_item(full_path))
        l.addWidget(del_btn)
        self.list_layout.addWidget(row)

    def run_py_file(self, path):
        """Метод для динамического запуска Python приложений"""
        try:
            spec = importlib.util.spec_from_file_location("dynamic_app", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Ищем класс HyperApp в модуле
            for attr in dir(module):
                obj = getattr(module, attr)
                if isinstance(obj, type) and issubclass(obj, MIOSORPIOS.HyperApp) and obj is not MIOSORPIOS.HyperApp:
                    MIOSORPIOS.run(obj)
                    return
            
            # Если это обычный скрипт
            os.system(f'python "{path}"')
        except Exception as e:
            print(f"Exec Error: {e}")

    def enter_dir(self, path):
        if path.exists() and path.is_dir():
            self.current_dir = path
            self.refresh_list()

    def go_back(self):
        if self.current_dir != self.base_path:
            self.current_dir = self.current_dir.parent
            self.refresh_list()

    def delete_item(self, path):
        try:
            if path.is_dir(): shutil.rmtree(path)
            else: os.remove(path)
            self.refresh_list()
        except: pass

if __name__ == "__main__":
    MIOSORPIOS.run(OrangeExplorer)