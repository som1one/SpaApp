#!/bin/bash
# Генерация иконок и сборка приложения SpaApp
set -e
cd "$(dirname "$0")/.."

echo "==> flutter pub get"
flutter pub get

echo "==> Генерация иконок (flutter_launcher_icons)"
dart run flutter_launcher_icons

echo "==> Сборка Android (APK)"
flutter build apk --release

echo "==> Готово. APK: build/app/outputs/flutter-apk/app-release.apk"
echo ""
echo "Для сборки iOS (IPA) выполните: flutter build ipa --release"
