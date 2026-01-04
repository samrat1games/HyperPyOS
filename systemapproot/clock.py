import sys
from pathlib import Path

# Поиск SDK
BASE = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BASE / "models" / "apps"))

import MIOSORPIOS
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QTimer, QTime, Qt

# МЕНЯЕМ PIOSApp НА HyperApp
class OrangeClock(MIOSORPIOS.HyperApp): 
    def __init__(self):
        super().__init__(title="Orange Clock")
        self.setFixedSize(320, 200)
        self.content.setStyleSheet("background-color: #0f111a; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;")
        
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("color: #ff8c00; font-size: 50px; font-weight: bold; font-family: 'Consolas'; border: none;")
        self.layout.addWidget(self.time_label)

        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
        self.update_time()

    def update_time(self):
        self.time_label.setText(QTime.currentTime().toString("HH:mm:ss"))

if __name__ == "__main__":
    MIOSORPIOS.run(OrangeClock)