#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Локальная проверка сертификатов и provisioning профилей
Проверяет валидность файлов без использования ключей
"""

import os
import sys
import base64
import plistlib
from pathlib import Path
from datetime import datetime

# Настройка кодировки для Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Цвета для вывода
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(msg):
    try:
        print(f"{GREEN}[OK] {msg}{RESET}")
    except:
        print(f"[OK] {msg}")

def print_error(msg):
    try:
        print(f"{RED}[ERROR] {msg}{RESET}")
    except:
        print(f"[ERROR] {msg}")

def print_warning(msg):
    try:
        print(f"{YELLOW}[WARN] {msg}{RESET}")
    except:
        print(f"[WARN] {msg}")

def print_info(msg):
    try:
        print(f"{BLUE}[INFO] {msg}{RESET}")
    except:
        print(f"[INFO] {msg}")

def check_provisioning_profile(profile_path):
    """Проверяет .mobileprovision файл"""
    print(f"\n[CHECK] Проверка provisioning profile: {profile_path}")
    
    if not os.path.exists(profile_path):
        print_error(f"Файл не найден: {profile_path}")
        return False
    
    try:
        # Читаем файл
        with open(profile_path, 'rb') as f:
            content = f.read()
        
        # Проверяем, что это plist (может быть закодирован)
        if content.startswith(b'<?xml'):
            # XML plist
            try:
                plist = plistlib.loads(content)
            except:
                print_error("Не удалось распарсить XML plist")
                return False
        elif content.startswith(b'bplist'):
            # Binary plist
            try:
                plist = plistlib.loads(content)
            except:
                print_error("Не удалось распарсить binary plist")
                return False
        else:
            # Может быть закодирован (CMS)
            print_warning("Файл может быть закодирован (CMS format)")
            print_info("Попробуйте открыть в Xcode или использовать security команду на Mac")
            return True
        
        # Извлекаем информацию
        bundle_id = plist.get('Entitlements', {}).get('application-identifier', 'N/A')
        if bundle_id != 'N/A':
            # Убираем Team ID префикс
            if '.' in bundle_id:
                bundle_id = bundle_id.split('.', 1)[1]
            print_success(f"Bundle ID: {bundle_id}")
        else:
            print_warning("Bundle ID не найден")
        
        # Проверяем тип профиля
        profile_type = plist.get('ProvisionedDevices')
        if profile_type is None:
            profile_type_name = "App Store / Enterprise"
            print_success(f"Тип профиля: {profile_type_name}")
        else:
            print_info(f"Тип профиля: Development (содержит {len(profile_type)} устройств)")
        
        # Проверяем дату истечения
        expiration_date = plist.get('ExpirationDate')
        if expiration_date:
            if isinstance(expiration_date, datetime):
                exp_date = expiration_date
            else:
                exp_date = datetime.fromisoformat(str(expiration_date))
            
            now = datetime.now()
            if exp_date > now:
                days_left = (exp_date - now).days
                print_success(f"Профиль действителен до: {exp_date.strftime('%Y-%m-%d')} ({days_left} дней)")
            else:
                print_error(f"Профиль истек: {exp_date.strftime('%Y-%m-%d')}")
                return False
        
        # Проверяем сертификаты в профиле
        certificates = plist.get('DeveloperCertificates', [])
        if certificates:
            print_success(f"Профиль содержит {len(certificates)} сертификат(ов)")
        
        return True
        
    except Exception as e:
        print_error(f"Ошибка проверки профиля: {e}")
        return False

def check_p12_certificate(p12_path, password=None):
    """Проверяет .p12 сертификат (базовая проверка)"""
    print(f"\n[CHECK] Проверка .p12 сертификата: {p12_path}")
    
    if not os.path.exists(p12_path):
        print_error(f"Файл не найден: {p12_path}")
        return False
    
    try:
        # Проверяем размер файла
        size = os.path.getsize(p12_path)
        if size < 1000:
            print_warning(f"Файл слишком маленький ({size} байт)")
        else:
            print_success(f"Размер файла: {size} байт")
        
        # Читаем файл
        with open(p12_path, 'rb') as f:
            content = f.read()
        
        # Проверяем, что это PKCS12 (начинается с определенных байтов)
        # PKCS12 обычно начинается с 0x30 0x82 или похожих
        if content.startswith(b'\x30\x82') or content.startswith(b'0\x82'):
            print_success("Формат PKCS12 корректен")
        else:
            print_warning("Файл может быть не в формате PKCS12")
            print_info("Для полной проверки нужен Mac с командой 'security'")
        
        # Проверяем Base64 версию
        try:
            base64_content = base64.b64encode(content).decode('ascii')
            print_success(f"Base64 кодирование успешно (длина: {len(base64_content)} символов)")
            print_info("Это значение можно использовать в CM_CERTIFICATE")
        except Exception as e:
            print_error(f"Ошибка Base64 кодирования: {e}")
        
        if password:
            print_info(f"Пароль указан: {'*' * len(password)}")
            print_warning("Для проверки пароля нужен Mac с командой 'security import'")
        else:
            print_warning("Пароль не указан - не могу проверить валидность")
            print_info("Используйте: python test_certificates.py --password YOUR_PASSWORD")
        
        return True
        
    except Exception as e:
        print_error(f"Ошибка проверки сертификата: {e}")
        return False

def main():
    print("=" * 60)
    print("Проверка сертификатов и provisioning профилей")
    print("=" * 60)
    
    # Определяем директорию скрипта
    script_dir = Path(__file__).parent
    
    # Ищем provisioning профили
    profile_files = list(script_dir.glob('*.mobileprovision'))
    
    if profile_files:
        print(f"\n📁 Найдено {len(profile_files)} provisioning профиль(ей):")
        for profile_file in profile_files:
            check_provisioning_profile(str(profile_file))
    else:
        print_warning("Не найдено .mobileprovision файлов")
    
    # Ищем .p12 сертификаты
    p12_files = list(script_dir.glob('*.p12'))
    
    if p12_files:
        print(f"\n📁 Найдено {len(p12_files)} .p12 сертификат(ов):")
        for p12_file in p12_files:
            # Пароль из аргументов или дефолтный
            password = '12345'  # Дефолтный пароль из codemagic.yaml
            if len(sys.argv) > 2 and sys.argv[1] == '--password':
                password = sys.argv[2]
            check_p12_certificate(str(p12_file), password)
    else:
        print_warning("Не найдено .p12 файлов")
        print_info("Ищите файлы с расширениями: .p12, .cer, .cert")
    
    # Итоги
    print("\n" + "=" * 60)
    print("Следующие шаги:")
    print("1. Убедитесь, что сертификаты не истекли")
    print("2. Проверьте, что Bundle ID в профиле совпадает с проектом")
    print("3. Закодируйте файлы в Base64 для Codemagic:")
    print("   python encode_certificates.py")
    print("4. Добавьте переменные в Codemagic:")
    print("   - CM_CERTIFICATE (Base64 .p12)")
    print("   - CM_PROVISIONING_PROFILE (Base64 .mobileprovision)")
    print("=" * 60)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
