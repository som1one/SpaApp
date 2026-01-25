#!/usr/bin/env python3
"""
Проверка размеров иконки приложения

Использование:
    python scripts/check_icon_sizes.py
"""

import sys
from pathlib import Path

def check_icon():
    """Проверяет размеры иконки"""
    project_root = Path(__file__).parent.parent
    icon_path = project_root / "spa" / "assets" / "images" / "app_icon.png"
    
    if not icon_path.exists():
        print(f"❌ Иконка не найдена: {icon_path}")
        return False
    
    try:
        from PIL import Image
        
        img = Image.open(icon_path)
        width, height = img.size
        mode = img.mode
        file_size = icon_path.stat().st_size / 1024  # KB
        
        print(f"📊 Информация об иконке:")
        print(f"   Путь: {icon_path}")
        print(f"   Размер: {width}x{height} px")
        print(f"   Формат: {mode}")
        print(f"   Размер файла: {file_size:.2f} KB")
        
        # Проверка требований
        print(f"\n✅ Проверка требований:")
        
        if width == height:
            print(f"   ✅ Квадратное изображение")
        else:
            print(f"   ❌ Не квадратное ({width}x{height})")
        
        if width >= 512:
            print(f"   ✅ Размер достаточен для Google Play (минимум 512x512)")
        else:
            print(f"   ⚠️  Размер меньше рекомендуемого (нужно минимум 512x512)")
        
        if mode in ('RGBA', 'LA', 'P'):
            print(f"   ⚠️  Есть прозрачность ({mode}) - нужно убрать для Google Play")
        else:
            print(f"   ✅ Без прозрачности ({mode})")
        
        if width == 512 and height == 512:
            print(f"\n🎉 Идеальный размер для Google Play!")
        elif width >= 512:
            print(f"\n💡 Можно использовать, но лучше создать 512x512 версию")
        else:
            print(f"\n⚠️  Нужно увеличить размер до 512x512 px")
        
        return True
        
    except ImportError:
        print("⚠️  Pillow не установлен, проверка размеров недоступна")
        print("Установите: pip install Pillow")
        print(f"\nФайл существует: {icon_path}")
        print(f"Размер файла: {icon_path.stat().st_size / 1024:.2f} KB")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    success = check_icon()
    sys.exit(0 if success else 1)

