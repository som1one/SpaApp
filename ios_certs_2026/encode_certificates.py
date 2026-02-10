#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Кодирование сертификатов и профилей в Base64 для Codemagic
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

def print_info(msg):
    try:
        print(f"{BLUE}[INFO] {msg}{RESET}")
    except:
        print(f"[INFO] {msg}")

def encode_file(file_path, output_name):
    """Кодирует файл в Base64"""
    if not os.path.exists(file_path):
        print_error(f"Файл не найден: {file_path}")
        return False
    
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        base64_content = base64.b64encode(content).decode('ascii')
        
        output_path = Path(__file__).parent / output_name
        with open(output_path, 'w') as f:
            f.write(base64_content)
        
        print_success(f"Закодирован: {file_path}")
        print_info(f"Сохранен в: {output_path}")
        print_info(f"Длина Base64: {len(base64_content)} символов")
        
        return True
    except Exception as e:
        print_error(f"Ошибка кодирования {file_path}: {e}")
        return False

def main():
    print("=" * 60)
    print("Кодирование сертификатов в Base64 для Codemagic")
    print("=" * 60)
    
    script_dir = Path(__file__).parent
    
    # Ищем .p12 файлы
    p12_files = list(script_dir.glob('*.p12'))
    if p12_files:
        print(f"\n[FOUND] Найдено {len(p12_files)} .p12 файл(ов):")
        for p12_file in p12_files:
            encode_file(str(p12_file), f"{p12_file.stem}_base64.txt")
            print(f"  -> Используйте для CM_CERTIFICATE в Codemagic")
    else:
        print(f"\n[WARN] Не найдено .p12 файлов в {script_dir}")
    
    # Ищем .mobileprovision файлы
    profile_files = list(script_dir.glob('*.mobileprovision'))
    if profile_files:
        print(f"\n[FOUND] Найдено {len(profile_files)} .mobileprovision файл(ов):")
        for profile_file in profile_files:
            encode_file(str(profile_file), f"{profile_file.stem}_base64.txt")
            print(f"  -> Используйте для CM_PROVISIONING_PROFILE в Codemagic")
    else:
        print(f"\n[WARN] Не найдено .mobileprovision файлов в {script_dir}")
    
    print("\n" + "=" * 60)
    print("Следующие шаги:")
    print("1. Скопируйте содержимое *_base64.txt файлов")
    print("2. Вставьте в Codemagic Environment Variables:")
    print("   - CM_CERTIFICATE (из .p12_base64.txt)")
    print("   - CM_PROVISIONING_PROFILE (из .mobileprovision_base64.txt)")
    print("3. Убедитесь, что пароль от .p12 указан в codemagic.yaml")
    print("=" * 60)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
