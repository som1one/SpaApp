#!/bin/bash
# Скрипт для настройки подписи Android (Linux/Mac)
# Запусти: chmod +x setup_signing.sh && ./setup_signing.sh

echo "=== Настройка подписи Android для PRIRODA SPA ==="
echo ""

# Проверяем, существует ли уже keystore
if [ -f "upload-keystore.jks" ]; then
    echo "⚠️  Keystore уже существует!"
    read -p "Перезаписать? (y/n) " overwrite
    if [ "$overwrite" != "y" ]; then
        echo "Отменено."
        exit
    fi
    rm upload-keystore.jks
fi

# Запрашиваем пароли
echo "Введи пароли для keystore:"
read -sp "Store Password (минимум 6 символов): " store_password
echo ""

if [ ${#store_password} -lt 6 ]; then
    echo "❌ Пароль должен быть минимум 6 символов!"
    exit 1
fi

read -sp "Key Password (или Enter для использования того же): " key_password
echo ""

if [ -z "$key_password" ]; then
    key_password="$store_password"
    echo "Используется тот же пароль для key"
fi

# Запрашиваем информацию о сертификате
echo ""
echo "Информация о сертификате:"
read -p "Имя и фамилия (CN) [PRIRODA SPA]: " name
name=${name:-PRIRODA SPA}

read -p "Подразделение (OU) [Development]: " org_unit
org_unit=${org_unit:-Development}

read -p "Организация (O) [PRIRODA SPA]: " org
org=${org:-PRIRODA SPA}

read -p "Город (L) [Moscow]: " city
city=${city:-Moscow}

read -p "Область/Регион (ST) [Moscow]: " state
state=${state:-Moscow}

read -p "Код страны (C, 2 буквы) [RU]: " country
country=${country:-RU}

# Создаем keystore
echo ""
echo "Создаю keystore..."

keytool -genkey -v \
    -keystore upload-keystore.jks \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000 \
    -alias upload \
    -storepass "$store_password" \
    -keypass "$key_password" \
    -dname "CN=$name, OU=$org_unit, O=$org, L=$city, ST=$state, C=$country"

if [ $? -eq 0 ]; then
    echo "✅ Keystore создан успешно!"
else
    echo "❌ Ошибка при создании keystore!"
    echo "   Убедись, что Java установлена и keytool в PATH"
    exit 1
fi

# Создаем key.properties
echo ""
echo "Создаю key.properties..."

if [ -f "key.properties" ]; then
    echo "⚠️  key.properties уже существует!"
    read -p "Перезаписать? (y/n) " overwrite
    if [ "$overwrite" != "y" ]; then
        echo "Отменено."
        exit
    fi
fi

cat > key.properties << EOF
# Файл с паролями для подписи Android
# НЕ коммить в git!

storePassword=$store_password
keyPassword=$key_password
keyAlias=upload
storeFile=../upload-keystore.jks
EOF

echo "✅ key.properties создан!"

echo ""
echo "=== Готово! ==="
echo ""
echo "✅ Keystore: android/upload-keystore.jks"
echo "✅ Конфигурация: android/key.properties"
echo ""
echo "⚠️  ВАЖНО:"
echo "   - Сохрани keystore и пароли в безопасном месте!"
echo "   - Без keystore нельзя обновлять приложение в Google Play!"
echo "   - Эти файлы уже добавлены в .gitignore"
echo ""
echo "Теперь можно собрать release версию:"
echo "  flutter build appbundle --release"

