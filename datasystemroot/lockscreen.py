import tkinter as tk
from tkinter import filedialog
import os
import json
import subprocess
import sys
from time import strftime
from PIL import Image, ImageTk

class HyperPyOS_LockScreen:
    def __init__(self, root):
        self.root = root
        self.root.attributes('-fullscreen', True)
        self.root.overrideredirect(True)

        self.screen_height = self.root.winfo_screenheight()
        self.screen_width = self.root.winfo_screenwidth()

        # --- ПУТИ ---
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.parent_dir = os.path.dirname(self.current_dir)
        self.config_path = os.path.join(self.parent_dir, "password", "config.json")
        self.wallpaper_path = os.path.join(self.parent_dir, "files", "HyperPyOS", "data", "wallpaper", "bg.jpg")
        self.shell_path = os.path.join(self.current_dir, "shell.py")

        # Загрузка конфига
        self.config = self.load_config()

        # Цвета и настройки из JSON
        self.bg_color = self.config.get("bg", "#1A1A1A")
        self.fg_color = self.config.get("fg", "#FFFFFF")
        self.lang = self.config.get("language", "EN")

        self.start_y = 0 
        self.is_unlocked = False

        # Основной фрейм
        self.main_frame = tk.Frame(self.root, width=self.screen_width, height=self.screen_height, bg=self.bg_color)
        self.main_frame.place(x=0, y=0)

        self.canvas = tk.Canvas(self.main_frame, highlightthickness=0, bg=self.bg_color, 
                                width=self.screen_width, height=self.screen_height)
        self.canvas.pack()

        self.load_wallpaper()

        # Часы
        self.time_text_id = self.canvas.create_text(
            self.screen_width // 2, self.screen_height // 3,
            text="00:00", font=("Arial Black", 120), fill=self.fg_color
        )

        # Текст подсказки
        swipe_text = "︿ SWIPE UP TO UNLOCK" if self.lang == "EN" else "︿ СМАХНИТЕ ВВЕРХ"
        self.canvas.create_text(self.screen_width // 2, self.screen_height - 80, 
                                text=swipe_text, fill=self.fg_color, font=("Arial", 14))

        # Бинды
        self.canvas.bind("<Button-1>", self.start_swipe)
        self.canvas.bind("<B1-Motion>", self.drag_swipe)
        self.canvas.bind("<ButtonRelease-1>", self.end_swipe)
        self.root.bind("<space>", lambda e: self.animate_unlock())

        self.update_time()

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {"bg": "#1A1A1A", "fg": "#FFFFFF", "language": "EN"}

    def load_wallpaper(self):
        if os.path.exists(self.wallpaper_path):
            try:
                img = Image.open(self.wallpaper_path).resize((self.screen_width, self.screen_height))
                self.bg_img = ImageTk.PhotoImage(img)
                self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")
            except: pass

    def update_time(self):
        self.canvas.itemconfig(self.time_text_id, text=strftime('%H:%M'))
        self.root.after(1000, self.update_time)

    def start_swipe(self, event): self.start_y = event.y_root

    def drag_swipe(self, event):
        y = event.y_root - self.start_y
        if y < 0: self.main_frame.place(y=y)

    def end_swipe(self, event):
        delta = event.y_root - self.start_y
        if delta < -(self.screen_height * 0.2):
            self.animate_unlock()
        else:
            self.main_frame.place(y=0)

    def animate_unlock(self):
        y = self.main_frame.winfo_y()
        if y > -self.screen_height:
            self.main_frame.place(y=y - 80)
            self.root.after(5, self.animate_unlock)
        else:
            if os.path.exists(self.shell_path):
                subprocess.Popen([sys.executable, self.shell_path])
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = HyperPyOS_LockScreen(root)
    root.mainloop()