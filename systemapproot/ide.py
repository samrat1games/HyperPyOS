import sys, subprocess
from pathlib import Path
from PyQt6.QtWidgets import QTextEdit, QPushButton, QVBoxLayout
from PyQt6.QtGui import QFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "models" / "apps"))
import MIOSORPIOS

class OrangeStudio(MIOSORPIOS.HyperApp):
    def __init__(self):
        super().__init__(title="Orange Studio (OS-I)")
        self.setFixedSize(800, 600)
        self.init_ui()

    def init_ui(self):
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Consolas", 12))
        self.editor.setPlaceholderText("# Напиши свой код здесь...")
        self.editor.setStyleSheet("background: #282c34; color: #abb2bf; border-radius: 10px; padding: 10px;")
        
        run_btn = QPushButton("▶ Run Code")
        run_btn.setStyleSheet("background: #ff9500; color: white; font-weight: bold; height: 40px;")
        run_btn.clicked.connect(self.run_code)
        
        self.layout.addWidget(self.editor)
        self.layout.addWidget(run_btn)

    def run_code(self):
        code = self.editor.toPlainText()
        with open("temp_run.py", "w", encoding="utf-8") as f:
            f.write(code)
        subprocess.Popen([sys.executable, "temp_run.py"], creationflags=subprocess.CREATE_NEW_CONSOLE)

if __name__ == "__main__":
    MIOSORPIOS.run(OrangeStudio)