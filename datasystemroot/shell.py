import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import sys
import subprocess
import ctypes
import logging
from pathlib import Path
from datetime import datetime

# Библиотека для работы с окнами
try:
    import pygetwindow as gw
    HAS_GW = True
except ImportError:
    HAS_GW = False

# =============================================================================
# ПУТИ И КОНФИГУРАЦИЯ
# =============================================================================
BASE_DIR = Path(__file__).parent.parent.resolve()
ICON_DIR = BASE_DIR / "icon"
SYS_APPS_DIR = BASE_DIR / "systemapproot"
APPS_DIR = BASE_DIR / "apps"
DATA_DIR = BASE_DIR / "files" / "HyperPyOS" / "data"
WALLPAPER_DIR = DATA_DIR / "wallpaper"
THEME_FILE = DATA_DIR / "theme.txt"

user32 = ctypes.windll.user32

class HyperPyOS_Shell(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Настройка графического интерфейса
        self.attributes("-fullscreen", True)
        self.overrideredirect(True)
        self.config(bg="#000000")
        
        # Полное скрытие интерфейса Windows
        self.toggle_windows_ui(False)
        
        # Кэш
        self.image_cache = {}
        self.launchpad_win = None
        
        # Только твои закрепленные приложения (без системных из Win)
        self.pinned_apps = [
            {"name": "Explorer", "file": "explorer.py", "icon": "explorer.png"},
            {"name": "Terminal", "file": "terminal.py", "icon": "terminal.png"},
            {"name": "Browser", "file": "browser.py", "icon": "browser.png"}
        ]
        
        # Фоновые слои
        self.canvas = tk.Canvas(self, highlightthickness=0, bg="#000000", bd=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_id = self.canvas.create_image(0, 0, anchor="nw")
        
        self.apply_wallpaper()
        self.init_ui_elements()
        
        # Запуск служб мониторинга
        self.start_daemons()
        
        self.bind("<Escape>", lambda e: self.shutdown_dialog())

    # --- СИСТЕМНОЕ УПРАВЛЕНИЕ ---
    def toggle_windows_ui(self, show):
        handle = user32.FindWindowW("Shell_TrayWnd", None)
        user32.ShowWindow(handle, 5 if show else 0)

    def apply_wallpaper(self):
        img_name = "bg.jpg"
        if THEME_FILE.exists():
            try: img_name = THEME_FILE.read_text().strip() or "bg.jpg"
            except: pass
        
        path = WALLPAPER_DIR / img_name
        if not path.exists(): path = WALLPAPER_DIR / "bg.jpg"
        
        img = Image.open(path).resize((self.winfo_screenwidth(), self.winfo_screenheight()), Image.Resampling.LANCZOS)
        self.tk_wall = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self.bg_id, image=self.tk_wall)

    def start_daemons(self):
        self.clock_loop()
        self.dock_monitor_loop()

    # --- ВИЗУАЛЬНЫЕ КОМПОНЕНТЫ ---
    def init_ui_elements(self):
        # Верхняя панель
        self.top_bar = tk.Frame(self, height=32, bg="#0d0d0d")
        self.top_bar.place(x=0, y=0, relwidth=1)
        
        tk.Label(self.top_bar, text="HyperPyOS Core", fg="#00a2ff", bg="#0d0d0d", 
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=15)
        
        self.clock_lbl = tk.Label(self.top_bar, text="", fg="white", bg="#0d0d0d", font=("Segoe UI", 9))
        self.clock_lbl.pack(side="right", padx=15)

        # Док-станция
        self.dock_frame = tk.Frame(self, bg="#1a1a1a", padx=10, pady=5)
        self.dock_frame.place(relx=0.5, rely=0.98, anchor="s")
        self.dock_inner = tk.Frame(self.dock_frame, bg="#1a1a1a")
        self.dock_inner.pack()

    def clock_loop(self):
        self.clock_lbl.config(text=datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self.clock_loop)

    # --- УМНЫЙ МОНИТОРИНГ ТВОИХ ПРИЛОЖЕНИЙ ---
    def dock_monitor_loop(self):
        """Сканирует только твои процессы, игнорируя системные окна Windows"""
        if not HAS_GW: return

        for child in self.dock_inner.winfo_children():
            child.destroy()

        # 1. Синяя S
        self.draw_dock_icon("S", self.toggle_launchpad, is_start=True)

        # 2. Список твоих существующих скриптов (Белый список)
        # Мы смотрим только те окна, которые называются как твои файлы
        my_apps = [p.stem.lower() for p in list(SYS_APPS_DIR.glob("*.py")) + list(APPS_DIR.glob("*.py"))]
        
        # Получаем все открытые окна
        all_windows = gw.getAllWindows()
        # Фильтруем: оставляем только те, что входят в наш список скриптов
        active_scripts = [w for w in all_windows if w.visible and w.title.lower() in my_apps]

        processed_names = []

        # 3. Рисуем закрепленные
        for app in self.pinned_apps:
            is_open = any(app["name"].lower() == w.title.lower() for w in active_scripts)
            self.draw_dock_icon(app["icon"], lambda a=app: self.app_control(a), active=is_open)
            processed_names.append(app["name"].lower())

        # 4. Рисуем запущенные, которых нет в закрепе (например, из папки /apps)
        for w in active_scripts:
            name = w.title.lower()
            if name not in processed_names:
                icon_file = f"{name}.png"
                self.draw_dock_icon(icon_file, lambda t=w.title: self.focus_win(t), active=True)
                processed_names.append(name)

        self.after(1200, self.dock_monitor_loop)

    def draw_dock_icon(self, icon_res, command, active=False, is_start=False):
        f = tk.Frame(self.dock_inner, bg="#1a1a1a")
        f.pack(side="left", padx=4)

        if is_start:
            btn = tk.Button(f, text="S", fg="#00a2ff", bg="#1a1a1a", font=("Arial", 18, "bold"),
                           bd=0, activebackground="#333", command=command)
        else:
            p = ICON_DIR / icon_res
            # Если иконки нет - ставим дефолтную иконку скрипта (explorer.png)
            if not p.exists(): p = ICON_DIR / "explorer.png"
            
            try:
                img = Image.open(p).resize((36, 36), Image.Resampling.LANCZOS)
                itk = ImageTk.PhotoImage(img)
                self.image_cache[icon_res] = itk
                btn = tk.Button(f, image=itk, bg="#1a1a1a", bd=0, activebackground="#333", command=command)
            except:
                btn = tk.Button(f, text="?", fg="white", bg="#333", width=4, bd=0, command=command)
        
        btn.pack()
        # Оранжевый индикатор
        indicator = tk.Frame(f, bg="#ff6600" if active else "#1a1a1a", height=2, width=22)
        indicator.pack(pady=(2, 0))

    # --- ЛОГИКА ОКОН ---
    def app_control(self, app):
        wins = [w for w in gw.getWindowsWithTitle(app["name"]) if w.visible]
        if wins:
            w = wins[0]
            if w.isMinimized: w.restore()
            w.activate()
        else:
            subprocess.Popen([sys.executable, str(SYS_APPS_DIR / app["file"])])

    def focus_win(self, title):
        wins = [w for w in gw.getWindowsWithTitle(title) if w.visible]
        if wins:
            if wins[0].isMinimized: wins[0].restore()
            wins[0].activate()

    # --- МЕНЮ ПРИЛОЖЕНИЙ ---
    def toggle_launchpad(self):
        if self.launchpad_win:
            self.launchpad_win.destroy()
            self.launchpad_win = None
            return

        self.launchpad_win = tk.Toplevel(self)
        self.launchpad_win.attributes("-fullscreen", True, "-topmost", True)
        self.launchpad_win.config(bg="#050505")
        
        tk.Button(self.launchpad_win, text="✕", font=("Arial", 22), bg="#050505", fg="white", 
                  bd=0, command=self.toggle_launchpad).place(relx=0.94, rely=0.04)

        grid = tk.Frame(self.launchpad_win, bg="#050505")
        grid.place(relx=0.5, rely=0.5, anchor="center")
        
        apps = list(SYS_APPS_DIR.glob("*.py")) + list(APPS_DIR.glob("*.py"))
        r, c = 0, 0
        for path in apps:
            if path.name.startswith("__"): continue
            item = tk.Frame(grid, bg="#050505", padx=25, pady=25)
            item.grid(row=r, column=c)
            
            icon_p = ICON_DIR / f"{path.stem}.png"
            if not icon_p.exists(): icon_p = ICON_DIR / "explorer.png"
            
            img = Image.open(icon_p).resize((60, 60), Image.Resampling.LANCZOS)
            itk = ImageTk.PhotoImage(img)
            btn = tk.Button(item, image=itk, bg="#050505", bd=0, command=lambda p=path: self.launch_script(p))
            btn.image = itk
            btn.pack()
            tk.Label(item, text=path.stem, fg="white", bg="#050505").pack(pady=5)
            
            c += 1
            if c > 5: c = 0; r += 1

    def launch_script(self, path):
        subprocess.Popen([sys.executable, str(path)])
        self.toggle_launchpad()

    def shutdown_dialog(self):
        if messagebox.askyesno("HyperPyOS", "Выйти в Windows?"):
            self.toggle_windows_ui(True)
            self.destroy()
            sys.exit()

def launch_system(base_path=None):
    app = HyperPyOS_Shell()
    app.mainloop()

if __name__ == "__main__":
    launch_system()