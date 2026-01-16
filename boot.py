import os
import sys
from pathlib import Path

# Определяем корень
BASE = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE))

print(f"[BOOT] BASE PATH: {BASE}")

try:
    # Запуск lockscreen.py
    lockscreen_path = BASE / "datasystemroot" / "lockscreen.py"
    if lockscreen_path.exists():
        os.system(f'python "{lockscreen_path}"')
    else:
        print("LOCKSCREEN NOT FOUND")
except Exception as e:
    print(f"BOOT ERROR: {e}")
    import traceback
    traceback.print_exc() 