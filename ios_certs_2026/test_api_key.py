#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Локальная проверка App Store Connect API ключа
Проверяет валидность ключа без отправки запросов к API
"""

import os
import sys
import base64
from pathlib import Path

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

def check_p8_file(p8_path):
    """Проверяет .p8 файл"""
    print(f"\n[CHECK] Проверка файла: {p8_path}")
    
    if not os.path.exists(p8_path):
        print_error(f"Файл не найден: {p8_path}")
        return False
    
    try:
        with open(p8_path, 'r') as f:
            content = f.read()
        
        # Проверяем формат PEM
        if not content.startswith('-----BEGIN PRIVATE KEY-----'):
            print_error("Файл не является валидным PEM форматом")
            print_info("Должен начинаться с: -----BEGIN PRIVATE KEY-----")
            return False
        
        if not content.endswith('-----END PRIVATE KEY-----\n'):
            if not content.endswith('-----END PRIVATE KEY-----'):
                print_warning("Файл должен заканчиваться на: -----END PRIVATE KEY-----")
        
        # Проверяем длину ключа (примерно)
        key_lines = [line for line in content.split('\n') 
                    if line and not line.startswith('-----')]
        key_content = ''.join(key_lines)
        
        if len(key_content) < 100:
            print_warning("Ключ кажется слишком коротким")
        else:
            print_success(f"Формат PEM корректен (длина: {len(key_content)} символов)")
        
        # Пытаемся декодировать Base64
        try:
            decoded = base64.b64decode(key_content)
            print_success(f"Base64 декодирование успешно (размер: {len(decoded)} байт)")
        except Exception as e:
            print_error(f"Ошибка декодирования Base64: {e}")
            return False
        
        # Извлекаем Key ID из имени файла
        filename = os.path.basename(p8_path)
        if filename.startswith('AuthKey_') and filename.endswith('.p8'):
            key_id = filename.replace('AuthKey_', '').replace('.p8', '')
            print_success(f"Key ID из имени файла: {key_id}")
            return True, key_id
        else:
            print_warning("Не удалось извлечь Key ID из имени файла")
            print_info("Ожидаемый формат: AuthKey_XXXXXXXXXX.p8")
            return True, None
        
    except Exception as e:
        print_error(f"Ошибка чтения файла: {e}")
        return False

def check_base64_key(base64_path):
    """Проверяет Base64 закодированный ключ"""
    print(f"\n[CHECK] Проверка Base64 файла: {base64_path}")
    
    if not os.path.exists(base64_path):
        print_error(f"Файл не найден: {base64_path}")
        return False
    
    try:
        with open(base64_path, 'r') as f:
            base64_content = f.read().strip()
        
        # Проверяем, что это Base64
        try:
            decoded = base64.b64decode(base64_content)
            print_success(f"Base64 валиден (размер: {len(decoded)} байт)")
            
            # Пытаемся декодировать как PEM
            try:
                pem_content = decoded.decode('utf-8')
                if 'BEGIN PRIVATE KEY' in pem_content:
                    print_success("Содержит валидный PEM ключ")
                    return True
                else:
                    print_warning("Декодированный контент не похож на PEM ключ")
                    return True
            except:
                print_warning("Не удалось декодировать как UTF-8, но Base64 валиден")
                return True
                
        except Exception as e:
            print_error(f"Ошибка декодирования Base64: {e}")
            return False
            
    except Exception as e:
        print_error(f"Ошибка чтения файла: {e}")
        return False

def main():
    print("=" * 60)
    print("Проверка App Store Connect API ключа")
    print("=" * 60)
    
    # Определяем директорию скрипта
    script_dir = Path(__file__).parent
    
    # Ищем .p8 файлы
    p8_files = list(script_dir.glob('AuthKey_*.p8'))
    
    if not p8_files:
        print_error("Не найдено .p8 файлов в текущей директории")
        print_info(f"Директория: {script_dir}")
        return 1
    
    print(f"\n[FOUND] Найдено {len(p8_files)} .p8 файл(ов):")
    for i, p8_file in enumerate(p8_files, 1):
        print(f"  {i}. {p8_file.name}")
    
    # Проверяем все файлы
    all_ok = True
    key_ids = []
    
    for p8_file in p8_files:
        result = check_p8_file(str(p8_file))
        if result:
            if isinstance(result, tuple):
                key_id = result[1]
                if key_id:
                    key_ids.append(key_id)
            all_ok = all_ok and True
        else:
            all_ok = False
    
    # Проверяем Base64 файлы
    base64_files = list(script_dir.glob('*_base64.txt')) + list(script_dir.glob('key_base64.txt'))
    
    if base64_files:
        print(f"\n📁 Найдено {len(base64_files)} Base64 файл(ов):")
        for base64_file in base64_files:
            check_base64_key(str(base64_file))
    
    # Итоги
    print("\n" + "=" * 60)
    if all_ok:
        print_success("Все проверки пройдены!")
        if key_ids:
            print(f"\n[KEY ID] Найденные Key ID:")
            for key_id in key_ids:
                print(f"  - {key_id}")
            print(f"\n[TIP] Используйте эти Key ID в Codemagic:")
            print(f"   APP_STORE_KEY_ID = {key_ids[0]}")
    else:
        print_error("Обнаружены проблемы с ключами")
        return 1
    
    print("\n" + "=" * 60)
    print("Следующие шаги:")
    print("1. Проверьте Key ID в App Store Connect:")
    print("   https://appstoreconnect.apple.com/access/api")
    print("2. Убедитесь, что ключ имеет роль 'App Manager' или 'Admin'")
    print("3. Проверьте, что сервис 'App Store Connect API' включен")
    print("4. Добавьте переменные в Codemagic (см. CODEMAGIC_APP_STORE_SETUP.md)")
    print("=" * 60)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
