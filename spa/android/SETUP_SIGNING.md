# Настройка подписи Android для продакшена

## Автоматическая настройка (рекомендуется)

### Windows:
```powershell
cd spa/android
powershell -ExecutionPolicy Bypass -File setup_signing.ps1
```

### Linux/Mac:
```bash
cd spa/android
chmod +x setup_signing.sh
./setup_signing.sh
```

Скрипт автоматически:
- Создаст keystore с запросом паролей
- Создаст key.properties с правильными настройками
- Запросит информацию о сертификате

## Ручная настройка (если скрипт не работает)

### Шаг 1: Создание keystore

Выполни команду в терминале (из папки `spa/android`):

```bash
keytool -genkey -v -keystore upload-keystore.jks -keyalg RSA -keysize 2048 -validity 10000 -alias upload
```

**Важно:**
- Запомни пароли (store password и key password) - они понадобятся позже
- Запомни alias (`upload`) - он используется в конфигурации
- Файл `upload-keystore.jks` должен быть в папке `android/`
- **НЕ коммить** keystore в git!

### Шаг 2: Создание key.properties

1. Скопируй шаблон:
```bash
cd android
cp key.properties.template key.properties
```

2. Открой `key.properties` и заполни реальными значениями:
```properties
storePassword=твой_store_пароль
keyPassword=твой_key_пароль
keyAlias=upload
storeFile=../upload-keystore.jks
```

**Важно:**
- `storeFile` должен указывать на путь к keystore относительно `android/app/`
- Если keystore в `android/upload-keystore.jks`, то путь: `../upload-keystore.jks`
- **НЕ коммить** key.properties в git!

## Шаг 3: Проверка

После настройки собери release версию:

```bash
cd spa
flutter build appbundle --release
```

Если всё настроено правильно, сборка пройдет успешно и будет использоваться release signing.

## Безопасность

- ✅ `key.properties` и `*.jks` уже добавлены в `.gitignore`
- ✅ Они не попадут в git
- ⚠️ **Сохрани keystore и пароли в безопасном месте!**
- ⚠️ **Без keystore нельзя обновлять приложение в Google Play!**

## Если key.properties не существует

Если файл `key.properties` не найден, сборка будет использовать debug signing (для разработки). Это нормально для локальной разработки, но для продакшена нужно настроить release signing.

