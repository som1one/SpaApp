#!/usr/bin/env python3
"""
Генерация иконок для Google Play из исходного изображения

Требования:
    pip install Pillow

Использование:
    python scripts/generate_google_play_icons.py [путь_к_исходному_изображению]
    
Пример:
    python scripts/generate_google_play_icons.py spa/assets/images/app_icon.png
"""

import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("❌ Ошибка: Pillow не установлен")
    print("Установите: pip install Pillow")
    sys.exit(1)

def generate_icons(source_path: str, output_dir: str = "google_play_icons"):
    """Генерирует все нужные размеры иконок для Google Play"""
    
    # Размеры для Google Play
    sizes = {
        "app_icon_512": 512,      # Основная иконка для Google Play
        "app_icon_1024": 1024,    # Исходный размер (для проверки)
    }
    
    source = Path(source_path)
    if not source.exists():
        print(f"❌ Файл не найден: {source_path}")
        print(f"Проверьте путь к файлу")
        return False
    
    output = Path(output_dir)
    output.mkdir(exist_ok=True)
    
    print(f"📂 Исходный файл: {source}")
    print(f"📂 Папка вывода: {output}\n")
    
    try:
        img = Image.open(source)
        print(f"✅ Изображение загружено: {img.size[0]}x{img.size[1]} px, режим: {img.mode}")
        
        # Конвертируем в RGB если нужно (убираем прозрачность для Google Play)
        if img.mode in ('RGBA', 'LA', 'P'):
            print("🔄 Конвертация из RGBA в RGB (убираем прозрачность)...")
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[-1])
            else:
                background.paste(img)
            img = background
            print("✅ Прозрачность удалена, фон белый")
        
        # Генерируем все размеры
        for name, size in sizes.items():
            if img.size[0] != size or img.size[1] != size:
                print(f"📐 Изменение размера до {size}x{size}...")
                resized = img.resize((size, size), Image.Resampling.LANCZOS)
            else:
                resized = img
            
            output_path = output / f"{name}.png"
            resized.save(output_path, "PNG", optimize=True)
            print(f"✅ Создан: {output_path.name} ({size}x{size} px)")
        
        print(f"\n🎉 Все иконки созданы в папке: {output.absolute()}")
        print("\n📋 Что дальше:")
        print("   1. Используйте app_icon_512.png для Google Play Console")
        print("   2. Проверьте, что иконка хорошо видна на светлом и темном фоне")
        print("   3. Убедитесь, что нет мелких деталей")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при обработке изображения: {e}")
        return False

def main():
    # Определяем путь к исходному файлу
    if len(sys.argv) > 1:
        source_path = sys.argv[1]
    else:
        # Пытаемся найти app_icon.png в проекте
        project_root = Path(__file__).parent.parent
        default_path = project_root / "spa" / "assets" / "images" / "app_icon.png"
        
        if default_path.exists():
            source_path = str(default_path)
            print(f"📂 Используется файл по умолчанию: {source_path}\n")
        else:
            print("❌ Исходный файл не найден")
            print("\nИспользование:")
            print("  python scripts/generate_google_play_icons.py [путь_к_изображению]")
            print("\nПример:")
            print("  python scripts/generate_google_play_icons.py spa/assets/images/app_icon.png")
            sys.exit(1)
    
    success = generate_icons(source_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

