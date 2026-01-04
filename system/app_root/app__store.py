import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import shutil

class AppStore(tk.Toplevel):
    def __init__(self, parent, kernel):
        super().__init__(parent)
        self.kernel = kernel
        self.title("App Store")
        self.geometry("800x500")
        self.configure(bg="#f5f5f7") # Светлый серый Apple-style
        
        # Путь к репозиторию системных приложений
        self.repo_path = self.kernel.base_dir / "apps"
        
        self.setup_ui()

    def setup_ui(self):
        # Боковая панель
        sidebar = tk.Frame(self, bg="#e1e1e3", width=180)
        sidebar.pack(side="left", fill="y")
        
        tk.Label(sidebar, text="PIOS Store", font=("Arial", 14, "bold"), 
                 bg="#e1e1e3", pady=20).pack()
        
        for cat in ["Discover", "Create", "Work", "Play"]:
            tk.Button(sidebar, text=cat, relief="flat", bg="#e1e1e3", 
                      anchor="w", padx=20).pack(fill="x", pady=2)

        # Основная область
        self.main_area = tk.Frame(self, bg="white")
        self.main_area.pack(side="right", expand=True, fill="both", padx=20, pady=20)
        
        tk.Label(self.main_area, text="Featured Apps", font=("Arial", 18, "bold"), 
                 bg="white").pack(anchor="w", pady=10)
        
        self.load_apps()

    def load_apps(self):
        """Сканирует папку apps/ на наличие доступных программ."""
        if not self.repo_path.exists():
            tk.Label(self.main_area, text="No apps found in system/apps", bg="white").pack()
            return

        # Создаем сетку (имитация)
        for app_file in self.repo_path.glob("*.py"):
            if app_file.name == "__init__.py": continue
            self.create_app_card(app_file.stem)

    def create_app_card(self, app_name):
        card = tk.Frame(self.main_area, bg="#fbfbfd", highlightbackground="#d2d2d7", 
                        highlightthickness=1, padx=10, pady=10)
        card.pack(fill="x", pady=5)
        
        tk.Label(card, text=f"📦 {app_name}", font=("Arial", 12, "bold"), bg="#fbfbfd").pack(side="left")
        
        btn_install = tk.Button(card, text="GET", bg="#0071e3", fg="white", 
                                relief="flat", font=("Arial", 9, "bold"),
                                command=lambda: self.install_app(app_name))
        btn_install.pack(side="right")

    def install_app(self, app_name):
        """Логика 'установки' приложения."""
        # В нашей модели 'установка' - это регистрация приложения в системе
        messagebox.showinfo("PIOS Store", f"App '{app_name}' installed successfully!")