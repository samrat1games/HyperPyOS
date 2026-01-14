import os
import sys
from pathlib import Path

# Определяем корень
BASE = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE))

print(f"[BOOT] BASE PATH: {BASE}")

try:
    from datasystemroot import shell
    # Проверяем наличие функции перед запуском
    if hasattr(shell, 'launch_system'):
        shell.launch_system(BASE)
    else:
        print("KERNEL PANIC: Function 'launch_system' not found in shell.py ПИЗДЕЦ ПОНИМАЕШЬ")
except Exception as e:
    print(f"BOOT ERROR: {e}")
    import traceback
    traceback.print_exc() 