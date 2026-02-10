#!/bin/sh

# Xcode Cloud Pre-Build Script для Flutter
# Этот скрипт выполняется перед сборкой Xcode

set -e

echo "🚀 Xcode Cloud: Начало pre-build скрипта для Flutter"

# Определяем путь к Flutter SDK
# Xcode Cloud использует стандартные пути
FLUTTER_PATH="${FLUTTER_ROOT:-$HOME/flutter}"

# Если Flutter не установлен, устанавливаем
if [ ! -d "$FLUTTER_PATH" ]; then
    echo "📥 Установка Flutter SDK..."
    git clone https://github.com/flutter/flutter.git -b stable "$FLUTTER_PATH"
fi

# Добавляем Flutter в PATH
export PATH="$FLUTTER_PATH/bin:$PATH"

# Проверяем версию Flutter
echo "📋 Flutter версия:"
flutter --version

# Переходим в директорию проекта (относительно корня репозитория)
cd "$CI_WORKSPACE/spa" || exit 1

# Устанавливаем Flutter зависимости
echo "📦 Установка Flutter зависимостей..."
flutter pub get

# Устанавливаем CocoaPods зависимости
echo "🍫 Установка CocoaPods зависимостей..."
cd ios
pod install
cd ..

# Генерируем Flutter файлы (если нужно)
echo "🔧 Генерация Flutter файлов..."
flutter precache --ios

# Генерируем конфигурацию для iOS (создает необходимые файлы)
echo "⚙️ Генерация iOS конфигурации..."
flutter build ios --config-only --release --no-codesign

echo "✅ Xcode Cloud: Pre-build скрипт завершен успешно"
