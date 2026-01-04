import ctypes
user32 = ctypes.windll.user32
# Находим дескриптор панели задач
handle = user32.FindWindowW("Shell_TrayWnd", None)
# Команда 5 означает "Показать" (SW_SHOW)
user32.ShowWindow(handle, 5)
print("Панель задач Windows должна была появиться!")