#!/bin/sh

# Xcode Cloud Post-Clone Script для Flutter
# Этот скрипт выполняется сразу после клонирования репозитория

set -e

echo "🚀 Xcode Cloud: Начало post-clone скрипта"

# CocoaPods обычно уже установлен в Xcode Cloud
# Если нет - попробуем установить через gem (без sudo, если возможно)
if ! command -v pod &> /dev/null; then
    echo "🍫 Установка CocoaPods..."
    # Xcode Cloud может не иметь sudo, пробуем без него
    gem install cocoapods --user-install || sudo gem install cocoapods
    export PATH="$HOME/.gem/ruby/$(ruby -e 'puts RUBY_VERSION[/\d+\.\d+/]')/bin:$PATH"
fi

# Проверяем версию CocoaPods
echo "📋 CocoaPods версия:"
pod --version

echo "✅ Xcode Cloud: Post-clone скрипт завершен успешно"
