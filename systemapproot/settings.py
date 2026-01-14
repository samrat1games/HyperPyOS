import sys, os, subprocess
from pathlib import Path
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

# --- КОНФИГ ПУТЕЙ ---
BASE_PATH = Path(__file__).parent.parent.resolve()
DATA_DIR = BASE_PATH / "files" / "HyperPyOS" / "data"
WALL_DIR = DATA_DIR / "wallpaper"
THEME_FILE = DATA_DIR / "theme.txt"
ENGINE_PATH = BASE_PATH / "models" / "apps"
EGG_PATH = BASE_PATH / "datasystemroot" / "memz.py"

sys.path.append(str(ENGINE_PATH))
try:
    from MIOSORPIOS import HyperApp
except ImportError:
    HyperApp = QWidget 

class SettingsApp(HyperApp):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HyperPyOS Settings Beta 2.1")
        self.resize(900, 650)
        self.egg_clicks = 0

        # ЧЕРНЫЙ ШРИФТ И ЧИСТЫЙ СТИЛЬ
        self.setStyleSheet("""
            QWidget { background-color: #ffffff; color: #000000; font-family: 'Segoe UI', sans-serif; }
            QListWidget { background-color: #f2f2f7; border: none; color: #000000; }
            QListWidget::item:selected { background-color: #007aff; color: #ffffff; }
            QGroupBox { border: 1px solid #d1d1d6; border-radius: 10px; margin-top: 15px; font-weight: bold; color: #000; padding-top: 20px; }
            QPushButton { background-color: #007aff; color: white; border-radius: 6px; padding: 10px; font-weight: bold; }
            QPushButton:hover { background-color: #0056b3; }
        """)

        container = getattr(self, "content", self)
        self.main_layout = QHBoxLayout(container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # САЙДБАР
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.addItems(["Сеть", "Обои", "О системе"])
        self.main_layout.addWidget(self.sidebar)

        self.pages = QStackedWidget()
        self.main_layout.addWidget(self.pages)
        
        self.init_pages()
        self.sidebar.currentRowChanged.connect(self.pages.setCurrentIndex)

    def init_pages(self):
        # 1. СЕТЬ (УЛЬТРА-СКАНЕР)
        p1 = QWidget(); l1 = QVBoxLayout(p1)
        l1.setContentsMargins(30, 20, 30, 20)
        l1.addWidget(QLabel("Беспроводные интерфейсы", styleSheet="font-size: 24px; font-weight: bold;"))

        wf_box = QGroupBox("Wi-Fi Сети")
        wf_lay = QVBoxLayout(wf_box)
        self.wifi_status = QLabel(f"Платформа: {sys.platform}")
        self.wifi_list = QListWidget()
        self.wifi_list.setFixedHeight(250)
        self.wifi_list.setStyleSheet("background: #f9f9f9; border: 1px solid #ccc; color: #000;")
        
        btn_scan = QPushButton("⚡ ГЛУБОКИЙ ПОИСК (Windows + Linux)")
        btn_scan.clicked.connect(self.run_real_scan)
        
        wf_lay.addWidget(self.wifi_status)
        wf_lay.addWidget(self.wifi_list)
        wf_lay.addWidget(btn_scan)
        l1.addWidget(wf_box)

        # Bluetooth
        bt_box = QGroupBox("Bluetooth")
        bt_lay = QVBoxLayout(bt_box)
        self.bt_info = QLabel("Статус: Не проверен")
        btn_bt = QPushButton("🔍 Проверить адаптер")
        btn_bt.clicked.connect(self.check_bt_real)
        bt_lay.addWidget(self.bt_info)
        bt_lay.addWidget(btn_bt)
        l1.addWidget(bt_box)
        
        l1.addStretch()
        self.pages.addWidget(p1)

        # 2. ОБОИ (ВОЗВРАЩАЕМ ТВОЙ КОД)
        p2 = QWidget(); l2 = QVBoxLayout(p2)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_cont = QWidget(); grid = QGridLayout(scroll_cont)
        if WALL_DIR.exists():
            images = [f for f in WALL_DIR.iterdir() if f.suffix.lower() in ['.jpg', '.png', '.jpeg']]
            for i, img in enumerate(images):
                btn = QPushButton()
                btn.setFixedSize(180, 110)
                btn.setIcon(QIcon(str(img))); btn.setIconSize(QSize(180, 110))
                btn.clicked.connect(lambda ch, n=img.name: self.apply_wall(n))
                grid.addWidget(btn, i // 3, i % 3)
        scroll.setWidget(scroll_cont)
        l2.addWidget(scroll)
        self.pages.addWidget(p2)

        # 3. О СИСТЕМЕ
        p3 = QWidget(); l3 = QVBoxLayout(p3)
        self.info_lbl = QLabel("HyperPyOS v2.8.5\nDev: O&ANGE_X\n\n(Кликни 5 раз)")
        self.info_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_lbl.setStyleSheet("font-size: 18px;")
        self.info_lbl.mousePressEvent = self.trigger_egg
        l3.addStretch(); l3.addWidget(self.info_lbl); l3.addStretch()
        self.pages.addWidget(p3)

    # --- ЛОГИКА ---
    def run_real_scan(self):
        self.wifi_list.clear()
        self.wifi_status.setText("⏳ Опрашиваю железо...")
        QTimer.singleShot(1500, self._do_scan)

    def _do_scan(self):
        nets = []
        try:
            if sys.platform == "win32":
                # Режим BSSID заставляет Windows видеть КАЖДУЮ частоту отдельно
                out = subprocess.check_output("netsh wlan show networks mode=bssid", shell=True).decode("cp866", errors="ignore")
                for line in out.split("\n"):
                    if "SSID" in line and ":" in line:
                        n = line.split(":", 1)[1].strip()
                        if n and n not in nets: nets.append(n)
            elif sys.platform == "linux":
                # Реальная команда для Linux
                out = subprocess.check_output("nmcli -t -f SSID dev wifi", shell=True).decode("utf-8")
                nets = list(set([l.strip() for l in out.split("\n") if l.strip()]))

            self.wifi_list.addItems([f"📶 {x}" for x in nets])
            self.wifi_status.setText(f"Найдено: {len(nets)}")
        except Exception as e:
            self.wifi_status.setText(f"Ошибка: {e}")

    def check_bt_real(self):
        try:
            cmd = 'sc query "bthserv"' if sys.platform == "win32" else "bluetoothctl show"
            out = subprocess.check_output(cmd, shell=True).decode("cp866" if sys.platform == "win32" else "utf-8")
            self.bt_info.setText("✅ Работает" if ("RUNNING" in out or "Powered: yes" in out) else "❌ Выключен")
        except: self.bt_info.setText("⚠️ Не найден")

    def apply_wall(self, name):
        THEME_FILE.write_text(name)
        print(f"Wallpaper: {name}")

    def trigger_egg(self, event):
        self.egg_clicks += 1
        if self.egg_clicks >= 5:
            if EGG_PATH.exists():
                subprocess.Popen([sys.executable, str(EGG_PATH)])
                self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SettingsApp(); window.show()
    sys.exit(app.exec())