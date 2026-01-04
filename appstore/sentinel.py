import sys
import datetime
import calendar
from pathlib import Path
from PyQt6.QtWidgets import (QLabel, QVBoxLayout, QHBoxLayout, QProgressBar, 
                             QComboBox, QFrame, QWidget)
from PyQt6.QtCore import QTimer, Qt

# Подключаем твой SDK
CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "models" / "apps"))
import MIOSORPIOS

class TimeSentinel(MIOSORPIOS.HyperApp):
    def __init__(self):
        super().__init__(title="Time Sentinel")
        self.setFixedSize(450, 400)
        self.init_ui()
        
    def init_ui(self):
        # Основной фон белый, но текст теперь будет СТРОГО черным
        self.content.setStyleSheet("background-color: #ffffff;")
        
        # Заголовок
        self.header = QLabel("Выбери цель отсчета:")
        self.header.setStyleSheet("font-size: 20px; font-weight: bold; color: #000000; margin-top: 10px;")
        self.layout.addWidget(self.header)

        # Выпадающее меню для выбора цели
        self.selector = QComboBox()
        self.selector.addItems(["До конца дня", "До конца месяца", "До конца года", "До конца текущего сезона"])
        self.selector.setStyleSheet("""
            QComboBox { 
                border: 2px solid #d1d1d6; border-radius: 8px; padding: 5px; 
                color: #000000; background: #f5f5f7; font-size: 14px;
            }
            QComboBox QAbstractItemView { color: #000000; background: #ffffff; }
        """)
        self.layout.addWidget(self.selector)

        # Карточка с результатом
        self.display_card = QFrame()
        self.display_card.setStyleSheet("background: #f5f5f7; border-radius: 15px; margin-top: 20px;")
        card_layout = QVBoxLayout(self.display_card)

        self.label_status = QLabel("Расчет...")
        self.label_status.setStyleSheet("font-size: 16px; font-weight: bold; color: #000000; border: none;")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar { border: 1px solid #d1d1d6; border-radius: 10px; text-align: center; height: 30px; background: #ffffff; color: #000000; font-weight: bold; }
            QProgressBar::chunk { background-color: #0071e3; border-radius: 9px; }
        """)
        
        self.label_info = QLabel("Осталось: --")
        self.label_info.setStyleSheet("font-size: 14px; color: #333333; border: none;")

        card_layout.addWidget(self.label_status)
        card_layout.addWidget(self.progress_bar)
        card_layout.addWidget(self.label_info)
        
        self.layout.addWidget(self.display_card)
        self.layout.addStretch()

        # Таймер
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)

    def update_stats(self):
        now = datetime.datetime.now()
        mode = self.selector.currentText()
        self.label_status.setText(mode)

        if mode == "До конца дня":
            percent, info = self.calc_day(now)
        elif mode == "До конца месяца":
            percent, info = self.calc_month(now)
        elif mode == "До конца года":
            percent, info = self.calc_year(now)
        else:
            percent, info = self.calc_season(now)

        self.progress_bar.setValue(int(percent))
        self.label_info.setText(info)

    def calc_day(self, now):
        passed = now.hour * 3600 + now.minute * 60 + now.second
        total = 86400
        rem = datetime.timedelta(seconds=total - passed)
        return (passed / total) * 100, f"Осталось: {rem}"

    def calc_month(self, now):
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        passed = (now.day - 1) * 86400 + (now.hour * 3600)
        total = days_in_month * 86400
        return (passed / total) * 100, f"Осталось дней: {days_in_month - now.day}"

    def calc_year(self, now):
        day_of_year = now.timetuple().tm_yday
        total_days = 366 if calendar.isleap(now.year) else 365
        return (day_of_year / total_days) * 100, f"До НГ осталось: {total_days - day_of_year} дн."

    def calc_season(self, now):
        # Март(3), Июнь(6), Сентябрь(9), Декабрь(12)
        seasons = [3, 6, 9, 12]
        target_month = next((m for m in seasons if m > now.month), 3)
        year = now.year if target_month > now.month else now.year + 1
        target_date = datetime.datetime(year, target_month, 1)
        diff = target_date - now
        # Примерный расчет прогресса сезона (90 дней)
        percent = max(0, min(100, (1 - diff.days / 90) * 100))
        return percent, f"До смены сезона: {diff.days} дн."

if __name__ == "__main__":
    MIOSORPIOS.run(TimeSentinel)