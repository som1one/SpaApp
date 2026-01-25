# 🤖 Полный гайд: Подпись Android приложения

## 📋 Информация о проекте

- **Package Name (Application ID):** `ru.prirodaspa.app`
- **Название приложения:** PRIRODA SPA
- **Рабочая директория:** `spa/`

---

## ✅ Текущее состояние

У вас уже настроено:
- ✅ `key.properties` — файл с настройками подписи
- ✅ `my-release-key.jks` — keystore файл
- ✅ `build.gradle.kts` — настроен для использования подписи
- ✅ Package name обновлен на `ru.prirodaspa.app`

---

## 🔍 Проверка текущей конфигурации

### Ваш `key.properties`

⚠️ **Не вставляйте реальные пароли в документацию/чаты.** Проверяем только, что файл существует и что значения внутри согласованы с keystore.

### Проверка keystore:

```bash
# Проверьте, что keystore существует и правильный
cd spa/android
keytool -list -v -keystore my-release-key.jks -alias <ВАШ_ALIAS_ИЗ_key.properties>
# Пароль вводите тот, что указан в key.properties (storePassword/keyPassword)
```

Если команда работает — keystore настроен правильно! ✅

---

## 🚀 Сборка подписанного приложения

### Вариант 1: App Bundle (для Google Play)

```bash
cd spa
flutter build appbundle --release
```

**Результат:**
```
spa/build/app/outputs/bundle/release/app-release.aab
```

### Вариант 2: APK (для тестирования или прямого распространения)

```bash
cd spa
flutter build apk --release
```

**Результат:**
```
spa/build/app/outputs/flutter-apk/app-release.apk
```

### Вариант 3: Split APK (оптимизированные APK по архитектурам)

```bash
cd spa
flutter build apk --split-per-abi --release
```

**Результат:**
- `app-armeabi-v7a-release.apk` (32-bit)
- `app-arm64-v8a-release.apk` (64-bit)
- `app-x86_64-release.apk` (x86_64)

---

## 📤 Загрузка в Google Play

### Через Google Play Console (веб-интерфейс):

1. Откройте: https://play.google.com/console
2. Выберите ваше приложение
3. Перейдите: **Production** → **Create new release**
4. Загрузите **App Bundle** (`.aab` файл)
5. Заполните информацию о релизе
6. Нажмите **Review release**

### Через Google Play Console API (автоматизация):

Можно настроить автоматическую загрузку через API, но это сложнее.

---

## 🔧 Настройка подписи (если нужно пересоздать)

### Способ 1: Автоматический скрипт (Windows)

```powershell
cd spa/android
powershell -ExecutionPolicy Bypass -File setup_signing.ps1
```

Скрипт автоматически:
- Создаст keystore
- Создаст key.properties
- Запросит все необходимые данные

### Способ 2: Автоматический скрипт (Linux/Mac)

```bash
cd spa/android
chmod +x setup_signing.sh
./setup_signing.sh
```

### Способ 3: Вручную

#### Шаг 1: Создание keystore

```bash
cd spa/android

keytool -genkey -v -keystore my-release-key.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias my-alias \
  -storepass prirodapass \
  -keypass prirodapass \
  -dname "CN=PRIRODA SPA, OU=Development, O=PRIRODA SPA, L=Moscow, ST=Moscow, C=RU"
```

#### Шаг 2: Создание key.properties

Создайте файл `spa/android/key.properties`:

```properties
storePassword=prirodapass
keyPassword=prirodapass
keyAlias=my-alias
storeFile=../my-release-key.jks
```

⚠️ **Важно:** Путь `storeFile` должен быть относительно `android/app/`

---

## ✅ Проверка подписи

### Проверка APK/AAB:

```bash
# Для APK
jarsigner -verify -verbose -certs spa/build/app/outputs/flutter-apk/app-release.apk

# Для AAB (нужно распаковать)
unzip -q spa/build/app/outputs/bundle/release/app-release.aab -d temp_aab
jarsigner -verify -verbose -certs temp_aab/BUNDLE-METADATA/com.android.tools.build.bundletool-*.apk
rm -rf temp_aab
```

### Проверка через apksigner (Android SDK):

```bash
# Найти apksigner (обычно в Android SDK)
$ANDROID_HOME/build-tools/*/apksigner verify --print-certs spa/build/app/outputs/flutter-apk/app-release.apk
```

---

## 🔐 Безопасность

### ⚠️ ВАЖНО:

1. **Сохраните keystore в безопасном месте!**
   - Без keystore нельзя обновлять приложение в Google Play
   - Если потеряете — придется создавать новое приложение

2. **Сохраните пароли:**
   - `storePassword` = `prirodapass`
   - `keyPassword` = `prirodapass`
   - `keyAlias` = `my-alias`

3. **Файлы в .gitignore:**
   - ✅ `key.properties` — не коммитится
   - ✅ `*.jks` — не коммитится
   - ✅ `my-release-key.jks` — не коммитится

4. **Резервное копирование:**
   - Скопируйте `my-release-key.jks` в безопасное место
   - Сохраните пароли в менеджере паролей
   - Задокументируйте информацию о keystore

---

## 📝 Чеклист перед сборкой

- [ ] `key.properties` существует в `spa/android/`
- [ ] `my-release-key.jks` существует в `spa/android/`
- [ ] Пароли известны и сохранены
- [ ] Package name = `ru.prirodaspa.app` (проверено)
- [ ] Flutter зависимости установлены (`flutter pub get`)
- [ ] Проект собирается без ошибок

---

## 🚀 Быстрая сборка

```bash
# Полная сборка App Bundle для Google Play
cd spa
flutter clean
flutter pub get
flutter build appbundle --release

# Результат: spa/build/app/outputs/bundle/release/app-release.aab
```

---

## ❌ Решение проблем

### Ошибка: "Release signing не настроен"

**Решение:**
1. Проверьте, что `key.properties` существует
2. Проверьте путь к keystore в `key.properties`
3. Убедитесь, что keystore файл существует

### Ошибка: "Keystore file not found"

**Решение:**
1. Проверьте путь в `key.properties`:
   - Если keystore в `android/` → путь: `../my-release-key.jks`
   - Если keystore в `android/app/` → путь: `my-release-key.jks`
2. Убедитесь, что файл существует

### Ошибка: "Wrong password"

**Решение:**
1. Проверьте пароли в `key.properties`
2. Убедитесь, что пароли правильные (без пробелов, без кавычек)
3. Попробуйте проверить keystore:
   ```bash
   keytool -list -v -keystore my-release-key.jks -alias my-alias
   ```

### Ошибка: "Alias does not exist"

**Решение:**
1. Проверьте alias в `key.properties` (должен быть `my-alias`)
2. Проверьте alias в keystore:
   ```bash
   keytool -list -keystore my-release-key.jks
   ```

---

## 📊 Информация о текущем keystore

### Проверка информации:

```bash
cd spa/android
keytool -list -v -keystore my-release-key.jks -alias my-alias
# Введите пароль: prirodapass
```

Вы увидите:
- Тип keystore
- Alias
- Дата создания
- Владелец сертификата
- Срок действия

---

## 🔄 Обновление приложения в Google Play

### Важно:

1. **Используйте тот же keystore** для всех обновлений
2. **Увеличьте versionCode** в `pubspec.yaml`:
   ```yaml
   version: 1.0.1+2  # +2 — это versionCode
   ```
3. **Соберите новый App Bundle:**
   ```bash
   flutter build appbundle --release
   ```
4. **Загрузите в Google Play Console**

---

## 📚 Дополнительные ресурсы

- **Flutter Android Deployment:** https://docs.flutter.dev/deployment/android
- **Google Play Console:** https://play.google.com/console
- **Android App Signing:** https://developer.android.com/studio/publish/app-signing

---

## ✅ Готово!

Теперь вы можете:
- ✅ Собирать подписанные APK и AAB
- ✅ Загружать в Google Play
- ✅ Обновлять приложение

**Соберите приложение:**
```bash
cd spa
flutter build appbundle --release
```

**Готово!** 🎉
