import tkinter as tk
from PIL import Image, ImageTk
import random
import time
import os
import ctypes  # Используем стандартную библиотеку Windows

# Настройки путей
ORANGE_PATH = "files/fonts/orange.png"
RICK_IMAGE_PATH = "files/fonts/rickroll.png"
RICK_SOUND_PATH = os.path.abspath("sound/rickroll.mp3") # Нужен абсолютный путь

DURATION = 15
ORANGE_COUNT = 10
RICK_COUNT = 10

# Функция для запуска звука через Windows API
def play_sound(file_path):
    try:
        # Команды для MCI (Media Control Interface)
        ctypes.windll.winmm.mciSendStringW(f'open "{file_path}" type mpegvideo alias rick', None, 0, None)
        ctypes.windll.winmm.mciSendStringW('play rick repeat', None, 0, None)
    except Exception as e:
        print(f"Ошибка звука: {e}")

def stop_sound():
    ctypes.windll.winmm.mciSendStringW('stop rick', None, 0, None)
    ctypes.windll.winmm.mciSendStringW('close rick', None, 0, None)

class FloatingImage:
    def __init__(self, canvas, image_path, sw, sh, size=(180, 180)):
        self.canvas = canvas
        self.size = size
        img = Image.open(image_path).convert("RGBA")
        img = img.resize(self.size, Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(img)
        
        self.x = random.randint(0, sw - size[0])
        self.y = random.randint(0, sh - size[1])
        self.dx = random.randint(8, 20) * random.choice([-1, 1])
        self.dy = random.randint(8, 20) * random.choice([-1, 1])
        
        self.item = self.canvas.create_image(self.x, self.y, image=self.photo, anchor="nw")
        self.sw, self.sh = sw, sh

    def move(self):
        self.x += self.dx
        self.y += self.dy
        if self.x <= 0 or self.x >= self.sw - self.size[0]: self.dx *= -1
        if self.y <= 0 or self.y >= self.sh - self.size[1]: self.dy *= -1
        self.canvas.coords(self.item, self.x, self.y)

def run_prank():
    # Запускаем звук без всяких pygame
    play_sound(RICK_SOUND_PATH)

    root = tk.Tk()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f"{sw}x{sh}+0+0")
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.config(bg='black')
    root.attributes("-transparentcolor", "black")

    canvas = tk.Canvas(root, width=sw, height=sh, bg='black', highlightthickness=0)
    canvas.pack()

    objects = []
    for _ in range(ORANGE_COUNT):
        objects.append(FloatingImage(canvas, ORANGE_PATH, sw, sh, size=(130, 130)))
    for _ in range(RICK_COUNT):
        objects.append(FloatingImage(canvas, RICK_IMAGE_PATH, sw, sh, size=(200, 200)))

    start_time = time.time()

    def update():
        for obj in objects:
            obj.move()
            
        if time.time() - start_time < DURATION:
            root.after(20, update)
        else:
            stop_sound() # Останавливаем музыку
            root.destroy()

    update()
    root.mainloop()

if __name__ == "__main__":
    if os.path.exists(ORANGE_PATH) and os.path.exists(RICK_IMAGE_PATH) and os.path.exists(RICK_SOUND_PATH):
        run_prank()
    else:
        print("Ошибка: Проверь файлы в files/fonts/ и sound/")
        print(f"Ищу звук тут: {RICK_SOUND_PATH}")