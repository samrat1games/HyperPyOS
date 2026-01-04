import tkinter as tk
from tkinter import Menu, filedialog
from PIL import Image, ImageTk
import os, sys, time, subprocess, ctypes, zipfile, io
from pathlib import Path

# Пытаемся включить блюр (Lucid Glass)
try:
    import pywinstyles
except ImportError:
    pywinstyles = None

# Скрытие таскбара Windows
user32 = ctypes.windll.user32
def set_taskbar_visible(visible=True):
    handle = user32.FindWindowW("Shell_TrayWnd", None)
    user32.ShowWindow(handle, 5 if visible else 0)

BASE_DIR = Path(__file__).parent.parent.resolve()
ICON_DIR = BASE_DIR / "icon"

class OrangeOS_Shell(tk.Tk):
    def __init__(self):
        super().__init__()
        
        set_taskbar_visible(False)
        self.attributes("-fullscreen", True, "-topmost", True)
        self.overrideredirect(True)
        self.config(bg="#121212")
        
        # Фоновый холст
        self.canvas = tk.Canvas(self, highlightthickness=0, bg="#121212")
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_img_id = self.canvas.create_image(0, 0, anchor="nw")
        
        self.load_wallpaper("bg.jpg")
        self.setup_top_bar()
        self.setup_dock()
        
        if pywinstyles:
            pywinstyles.apply_style(self, "acrylic")
        
        self.launchpad = None
        self.bind("<Escape>", self.exit_system)

    def load_wallpaper(self, path):
        p = BASE_DIR / "data" / "wallpaper" / path
        if not p.exists(): p = Path(path)
        if p.exists():
            img = Image.open(p).resize((self.winfo_screenwidth(), self.winfo_screenheight()))
            self.bg_img = ImageTk.PhotoImage(img)
            self.canvas.itemconfig(self.bg_img_id, image=self.bg_img)

    def setup_top_bar(self):
        self.top_bar = tk.Frame(self, height=32, bg="#1e1e1e")
        self.top_bar.place(x=0, y=0, relwidth=1)
        
        orange_p = BASE_DIR / "files" / "fonts" / "orange.png"
        if orange_p.exists():
            img = Image.open(orange_p).resize((18, 18), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(img)
            lbl = tk.Label(self.top_bar, image=self.logo_img, bg="#1e1e1e", cursor="hand2")
            lbl.pack(side="left", padx=10)
            lbl.bind("<Button-1>", self.show_system_menu)

        tk.Label(self.top_bar, text="OrangeOS", font=("Segoe UI", 9, "bold"), bg="#1e1e1e", fg="white").pack(side="left")
        self.clock = tk.Label(self.top_bar, font=("Segoe UI", 10), bg="#1e1e1e", fg="white")
        self.clock.pack(side="right", padx=15)
        self.update_clock()

    def create_rounded_rect(self, canvas, x, y, w, h, r, **kwargs):
        points = [x+r, y, x+w-r, y, x+w, y, x+w, y+r, x+w, y+h-r, x+w, y+h, x+w-r, y+h, x+r, y+h, x, y+h, x, y+h-r, x, y+r, x, y]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    def setup_dock(self):
        # Док: Темно-серый Lucid Glass стиль
        self.dock_canvas = tk.Canvas(self, width=620, height=85, bg="#121212", highlightthickness=0)
        self.create_rounded_rect(self.dock_canvas, 5, 5, 610, 75, 38, fill="#252525", outline="#3d3d3d")
        self.dock_canvas.place(relx=0.5, rely=0.98, anchor="s")

        self.inner_dock = tk.Frame(self.dock_canvas, bg="#252525")
        self.dock_canvas.create_window(310, 42, window=self.inner_dock)

        # Системные иконки из папки icon/
        icons = ["settings.png", "explorer.png", "browser.png", "terminal.png", "ide.png", "appstore.png"]
        for icon in icons:
            path = ICON_DIR / icon
            cmd = self.toggle_launchpad if icon == "settings.png" else lambda i=icon: self.run_app(f"systemapproot/{i.replace('.png', '.py')}")
            if path.exists():
                img = Image.open(path).resize((48, 48), Image.Resampling.LANCZOS)
                icon_img = ImageTk.PhotoImage(img)
                btn = tk.Button(self.inner_dock, image=icon_img, bg="#252525", activebackground="#333333", relief="flat", bd=0, command=cmd)
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
        if pywinstyles: pywinstyles.apply_style(self.launchpad, "acrylic")
        
        container = tk.Frame(self.launchpad, bg="#121212")
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        apps_data = []
        for folder in ["systemapproot", "apps"]:
            p = BASE_DIR / folder
            if not p.exists(): continue
            
            # Сканируем .oa (Твоя матрёшка: Архив -> Папка -> файлы)
            for oa in p.glob("*.oa"):
                try:
                    with zipfile.ZipFile(oa, 'r') as z:
                        root = z.namelist()[0].split('/')[0]
                        icon_data = z.read(f"{root}/appicon.png")
                        img = Image.open(io.BytesIO(icon_data))
                        apps_data.append({"name": oa.stem, "exec": oa, "icon": img, "type": "oa", "root": root})
                except:
                    apps_data.append({"name": oa.stem, "exec": oa, "icon": None, "type": "oa", "root": None})

            # Сканируем обычные .py
            for py in p.glob("*.py"):
                if py.name.startswith("__"): continue
                apps_data.append({"name": py.stem, "exec": py, "icon": None, "type": "py"})

        r, c = 0, 0
        for app in apps_data:
            frame = tk.Frame(container, bg="#121212", padx=25, pady=25)
            frame.grid(row=r, column=c)
            
            if app.get("icon"):
                img = app["icon"].resize((75, 75), Image.Resampling.LANCZOS)
            else:
                icon_path = ICON_DIR / f"{app['name']}.png"
                if not icon_path.exists(): icon_path = ICON_DIR / "document.png"
                img = Image.open(icon_path).resize((75, 75), Image.Resampling.LANCZOS)
            
            icon_img = ImageTk.PhotoImage(img)
            btn = tk.Button(frame, image=icon_img, bg="#121212", relief="flat", bd=0, 
                            command=lambda a=app: self.launch_logic(a))
            btn.image = icon_img
            btn.pack()
            tk.Label(frame, text=app["name"], font=("Segoe UI", 10), bg="#121212", fg="white").pack(pady=5)
            
            c += 1
            if c > 5: c = 0; r += 1

    def launch_logic(self, app):
        if app["type"] == "oa":
            archive = str(app["exec"])
            root = app["root"]
            # Запуск: читаем код из папки внутри архива и исполняем его
            try:
                with zipfile.ZipFile(archive, 'r') as z:
                    code = z.read(f"{root}/app.py").decode("utf-8")
                    # Передаем путь к архиву в sys.path, чтобы работали импорты
                    wrapped_code = f"import sys, os; sys.path.insert(0, r'{archive}'); {code}"
                    subprocess.Popen([sys.executable, "-c", wrapped_code])
            except Exception as e:
                print(f"Ошибка запуска {app['name']}: {e}")
        else:
            subprocess.Popen([sys.executable, str(app["exec"])])
            
        if self.launchpad: self.toggle_launchpad()

    def run_app(self, rel_path):
        p = BASE_DIR / rel_path
        if p.exists(): subprocess.Popen([sys.executable, str(p)])

    def show_system_menu(self, event):
        m = Menu(self, tearoff=0, bg="#1e1e1e", fg="white", activebackground="#333333")
        m.add_command(label="Обои", command=lambda: self.load_wallpaper(filedialog.askopenfilename()))
        m.add_separator()
        m.add_command(label="Выход", command=self.exit_system)
        m.post(event.x_root, event.y_root)

    def update_clock(self):
        self.clock.config(text=time.strftime("%H:%M"))
        self.after(10000, self.update_clock)

    def exit_system(self, event=None):
        set_taskbar_visible(True)
        self.destroy()

def launch_system(base_path=None):
    app = OrangeOS_Shell()
    app.mainloop()

if __name__ == "__main__":
    launch_system()