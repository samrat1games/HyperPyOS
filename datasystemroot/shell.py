import tkinter as tk
from tkinter import Menu, filedialog, messagebox
from PIL import Image, ImageTk
import os, sys, time, subprocess, ctypes
from pathlib import Path

# Библиотека для звука (Установи: pip install pygame)
try:
    import pygame
    pygame.mixer.init()
except ImportError:
    pygame = None

# Библиотека для размытия (Установи: pip install pywinstyles)
try:
    import pywinstyles
except ImportError:
    pywinstyles = None

# Скрытие таскбара Windows
user32 = ctypes.windll.user32
def set_taskbar_visible(visible=True):
    handle = user32.FindWindowW("Shell_TrayWnd", None)
    user32.ShowWindow(handle, 5 if visible else 0)

# Пути проекта
BASE_DIR = Path(__file__).parent.parent.resolve()
ICON_DIR = BASE_DIR / "icon"
APPS_DIR = BASE_DIR / "apps"
SYS_APPS_DIR = BASE_DIR / "systemapproot"
SOUND_DIR = BASE_DIR / "sound"

class OrangeOS_Shell(tk.Tk):
    def __init__(self):
        super().__init__()
        
        set_taskbar_visible(False)
        self.attributes("-fullscreen", True)
        self.overrideredirect(True)
        self.config(bg="#121212")
        
        # Основной холст
        self.canvas = tk.Canvas(self, highlightthickness=0, bg="#121212")
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_img_id = self.canvas.create_image(0, 0, anchor="nw")
        
        self.load_wallpaper("bg.jpg")
        self.setup_top_bar()
        self.setup_dock()
        
        if pywinstyles:
            pywinstyles.apply_style(self, "acrylic")
        
        self.launchpad = None
        
        # Клик по рабочему столу отправляет его под окна приложений
        self.canvas.bind("<Button-1>", lambda e: self.lower())
        self.bind("<Escape>", self.exit_system)

    def load_wallpaper(self, path):
        p = BASE_DIR / "data" / "wallpaper" / path
        if not p.exists(): p = Path(path)
        if p.exists():
            img = Image.open(p).resize((self.winfo_screenwidth(), self.winfo_screenheight()))
            self.bg_img = ImageTk.PhotoImage(img)
            self.canvas.itemconfig(self.bg_img_id, image=self.bg_img)

    def setup_top_bar(self):
        self.top_bar = tk.Frame(self, height=32, bg="#1a1a1a")
        self.top_bar.place(x=0, y=0, relwidth=1)
        
        # Кнопка системы
        orange_p = BASE_DIR / "files" / "fonts" / "orange.png"
        if orange_p.exists():
            img = Image.open(orange_p).resize((20, 20), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(img)
            lbl = tk.Label(self.top_bar, image=self.logo_img, bg="#1a1a1a", cursor="hand2")
            lbl.pack(side="left", padx=10)
            lbl.bind("<Button-1>", self.show_system_menu)

        tk.Label(self.top_bar, text="OrangeOS", font=("Segoe UI", 9, "bold"), bg="#1a1a1a", fg="#ffcc00").pack(side="left")
        
        # Часы
        self.clock = tk.Label(self.top_bar, font=("Segoe UI", 10), bg="#1a1a1a", fg="white")
        self.clock.pack(side="right", padx=15)
        self.update_clock()

    def create_rounded_rect(self, canvas, x, y, w, h, r, **kwargs):
        points = [x+r, y, x+w-r, y, x+w, y, x+w, y+r, x+w, y+h-r, x+w, y+h, x+w-r, y+h, x+r, y+h, x, y+h, x, y+h-r, x, y+r, x, y]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    def setup_dock(self):
        dock_w = 700
        self.dock_canvas = tk.Canvas(self, width=dock_w, height=90, bg="#121212", highlightthickness=0)
        self.create_rounded_rect(self.dock_canvas, 10, 10, dock_w-20, 70, 35, fill="#222222", outline="#444444")
        self.dock_canvas.place(relx=0.5, rely=0.98, anchor="s")

        self.inner_dock = tk.Frame(self.dock_canvas, bg="#222222")
        self.dock_canvas.create_window(dock_w//2, 45, window=self.inner_dock)

        # Статичные иконки в доке
        dock_apps = [
            ("settings.png", self.toggle_launchpad),
            ("explorer.png", lambda: self.run_py(SYS_APPS_DIR / "explorer.py")),
            ("terminal.png", lambda: self.run_py(SYS_APPS_DIR / "terminal.py")),
            ("browser.png", lambda: self.run_py(SYS_APPS_DIR / "browser.py"))
        ]

        for icon_file, cmd in dock_apps:
            path = ICON_DIR / icon_file
            if path.exists():
                img = Image.open(path).resize((48, 48), Image.Resampling.LANCZOS)
                icon_img = ImageTk.PhotoImage(img)
                btn = tk.Button(self.inner_dock, image=icon_img, bg="#222222", bd=0, command=cmd, activebackground="#333333")
                btn.image = icon_img
                btn.pack(side="left", padx=10)

    def toggle_launchpad(self):
        if self.launchpad:
            self.launchpad.destroy()
            self.launchpad = None
            return
        
        self.launchpad = tk.Toplevel(self)
        self.launchpad.attributes("-fullscreen", True, "-topmost", True)
        self.launchpad.configure(bg="#121212")

        # Крестик для выхода из меню
        close_btn = tk.Button(self.launchpad, text="✕", font=("Segoe UI", 20), bg="#121212", fg="white", 
                              bd=0, cursor="hand2", command=self.toggle_launchpad, activeforeground="#ffcc00")
        close_btn.place(relx=0.95, rely=0.05, anchor="center")
        
        container = tk.Frame(self.launchpad, bg="#121212")
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        r, c = 0, 0
        
        # 1. Поиск системных программ
        if SYS_APPS_DIR.exists():
            for py_file in SYS_APPS_DIR.glob("*.py"):
                if py_file.name.startswith("__"): continue
                self.add_app_to_grid(container, py_file, r, c, is_system=True)
                c += 1
                if c > 5: c = 0; r += 1

        # 2. Поиск в папке apps (поддержка папок и одиночных .py)
        if APPS_DIR.exists():
            for item in APPS_DIR.iterdir():
                target = None
                if item.is_dir() and (item / "app.py").exists(): target = item / "app.py"
                elif item.is_file() and item.suffix == ".py": target = item
                
                if target:
                    self.add_app_to_grid(container, target, r, c)
                    c += 1
                    if c > 5: c = 0; r += 1

    def add_app_to_grid(self, master, path, r, c, is_system=False):
        frame = tk.Frame(master, bg="#121212", padx=20, pady=20)
        frame.grid(row=r, column=c)
        
        # Логика иконок
        icon_name = path.stem + ".png"
        icon_path = ICON_DIR / icon_name if is_system else path.parent / "appicon.png"
        if not icon_path.exists(): icon_path = ICON_DIR / "explorer.png"
            
        img = Image.open(icon_path).resize((70, 70), Image.Resampling.LANCZOS)
        icon_img = ImageTk.PhotoImage(img)
        
        btn = tk.Button(frame, image=icon_img, bg="#121212", bd=0, command=lambda: self.run_py(path))
        btn.image = icon_img
        btn.pack()
        
        label_text = path.stem if is_system else (path.parent.name if path.name == "app.py" else path.name)
        tk.Label(frame, text=label_text, fg="white", bg="#121212", font=("Segoe UI", 10)).pack(pady=5)

    def run_py(self, path):
        if Path(path).exists():
            subprocess.Popen([sys.executable, str(path)])
            if self.launchpad: self.toggle_launchpad()
            # Прячем шелл под запущенное приложение
            self.after(500, self.lower)
        else:
            messagebox.showerror("Error", f"File not found: {path}")

    def show_system_menu(self, event):
        m = Menu(self, tearoff=0, bg="#222222", fg="white", activebackground="#ffcc00", activeforeground="black")
        m.add_command(label="Restart Shell", command=self.restart_shell)
        m.add_separator()
        m.add_command(label="Shutdown OrangeOS", command=self.exit_system)
        m.post(event.x_root, event.y_root)

    def restart_shell(self):
        set_taskbar_visible(True)
        os.execv(sys.executable, ['python'] + sys.argv)

    def update_clock(self):
        self.clock.config(text=time.strftime("%H:%M:%S"))
        self.after(1000, self.update_clock)

    def exit_system(self, event=None):
        # Звук выключения
        sound_path = SOUND_DIR / "TurnOff.mp3"
        if pygame and sound_path.exists():
            try:
                pygame.mixer.music.load(str(sound_path))
                pygame.mixer.music.play()
                time.sleep(2) # Даем звуку проиграть перед закрытием
            except: pass
            
        set_taskbar_visible(True)
        self.destroy()
        sys.exit()

def launch_system(base_path=None):
    app = OrangeOS_Shell()
    app.mainloop()

if __name__ == "__main__":
    launch_system()