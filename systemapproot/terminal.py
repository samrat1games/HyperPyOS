import sys, os, subprocess
from pathlib import Path
from PyQt6.QtWidgets import QTextEdit, QLineEdit
from PyQt6.QtCore import Qt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "models" / "apps"))
import MIOSORPIOS

class OrangeTerminal(MIOSORPIOS.HyperApp):
    def __init__(self):
        super().__init__(title="OTS Terminal")
        self.setFixedSize(700, 450)
        self.init_ui()

    def init_ui(self):
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("background: #0c0c0c; color: #00ff00; font-family: Consolas;")
        self.output.append("OrangeOS Terminal Interface\nType 'ots help' for system commands.\n")
        
        self.input = QLineEdit()
        self.input.setStyleSheet("background: #0c0c0c; color: white; border: none; font-family: Consolas;")
        self.input.returnPressed.connect(self.handle_cmd)
        
        self.layout.addWidget(self.output)
        self.layout.addWidget(self.input)

    def handle_cmd(self):
        cmd = self.input.text()
        self.output.append(f"ots_user> {cmd}")
        self.input.clear()

        if cmd.startswith("ots "):
            parts = cmd.split(" ")
            sub = parts[1] if len(parts) > 1 else ""
            
            if sub == "help":
                self.output.append("ots shell - Open OTS Shell\nots list - List directory\nots version - System info")
            elif sub == "list":
                self.output.append("\n".join(os.listdir(".")))
            elif sub == "version":
                self.output.append("OrangeOS v1.0.4 [Stable]")
            else:
                self.output.append(f"OTS Error: Unknown command '{sub}'")
        else:
            # Обычный запуск Python или системных команд
            try:
                proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = proc.communicate()
                self.output.append(out.decode('cp866') if out else err.decode('cp866'))
            except Exception as e:
                self.output.append(f"Exec Error: {e}")

if __name__ == "__main__":
    MIOSORPIOS.run(OrangeTerminal)