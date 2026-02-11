#!/usr/bin/env python3
"""
Генератор временных заглушек для скриншотов App Store
Создает изображения с нейтральным фоном и текстом "Скоро"
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Размеры для разных устройств
SIZES = {
    'iphone_6_7': (1290, 2796),  # iPhone 6.7" (iPhone 14 Pro Max, 13 Pro Max, 12 Pro Max)
    'iphone_6_5': (1284, 2778),  # iPhone 6.5" (iPhone 11 Pro Max, XS Max)
    'ipad_pro_13': (2048, 2732),  # iPad Pro 13" (12.9")
}

def create_placeholder(size, text="Скоро", bg_color=(240, 240, 240), text_color=(100, 100, 100)):
    """Создает заглушку для скриншота"""
    width, height = size
    
    # Создаем изображение
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Пытаемся использовать системный шрифт, если не получится - используем default
    try:
        # Для Windows
        font_path = "C:/Windows/Fonts/arial.ttf"
        if os.path.exists(font_path):
            font = ImageFont.truetype(font_path, size=120)
        else:
            # Для Mac/Linux
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size=120)
    except:
        # Fallback на default font
        font = ImageFont.load_default()
    
    # Получаем размеры текста
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Центрируем текст
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Рисуем текст
    draw.text((x, y), text, fill=text_color, font=font)
    
    return img

def main():
    """Генерирует все необходимые заглушки"""
    
    # Создаем папку для скриншотов
    output_dir = "app_store_screenshots"
    os.makedirs(output_dir, exist_ok=True)
    
    print("Создание заглушек для App Store...")
    
    # iPhone 6.7" (основной размер)
    print("  - iPhone 6.7\" (1290x2796)...")
    img = create_placeholder(SIZES['iphone_6_7'], "Скоро")
    img.save(os.path.join(output_dir, "iphone_6_7_placeholder.png"), "PNG")
    
    # iPhone 6.5" (альтернативный)
    print("  - iPhone 6.5\" (1284x2778)...")
    img = create_placeholder(SIZES['iphone_6_5'], "Скоро")
    img.save(os.path.join(output_dir, "iphone_6_5_placeholder.png"), "PNG")
    
    # iPad Pro 13"
    print("  - iPad Pro 13\" (2048x2732)...")
    img = create_placeholder(SIZES['ipad_pro_13'], "Скоро")
    img.save(os.path.join(output_dir, "ipad_pro_13_placeholder.png"), "PNG")
    
    # Вариант с белым фоном
    print("  - iPhone 6.7\" (белый фон)...")
    img = create_placeholder(SIZES['iphone_6_7'], "Скоро", bg_color=(255, 255, 255), text_color=(150, 150, 150))
    img.save(os.path.join(output_dir, "iphone_6_7_white.png"), "PNG")
    
    # Вариант с "Coming Soon"
    print("  - iPhone 6.7\" (Coming Soon)...")
    img = create_placeholder(SIZES['iphone_6_7'], "Coming Soon", bg_color=(240, 240, 240), text_color=(100, 100, 100))
    img.save(os.path.join(output_dir, "iphone_6_7_coming_soon.png"), "PNG")
    
    print(f"\n[OK] Готово! Заглушки сохранены в папку: {output_dir}/")
    print("\nИспользуйте:")
    print("  - iphone_6_7_placeholder.png для iPhone 6.5\" в App Store Connect")
    print("  - ipad_pro_13_placeholder.png для iPad Pro 13\" в App Store Connect")

if __name__ == "__main__":
    main()
