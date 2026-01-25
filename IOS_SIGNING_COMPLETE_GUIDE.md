# 🔐 Полный гайд: Подпись iOS приложения

## 📋 Информация о проекте

- **Bundle ID:** `ru.prirodaspa.app` (обновлен)
- **Название приложения:** PRIRODA SPA
- **Рабочая директория:** `spa/`

---

## 🎯 Способ 1: Автоматическая подпись (РЕКОМЕНДУЕТСЯ)

Самый простой способ — Xcode автоматически создаст сертификаты и provisioning profiles.

### Шаг 1: Откройте проект в Xcode

```bash
cd spa/ios
open Runner.xcworkspace
```

⚠️ **Важно:** Открывайте `.xcworkspace`, а не `.xcodeproj`!

### Шаг 2: Настройте автоматическую подпись

1. В Xcode выберите проект **Runner** в левой панели
2. Выберите target **Runner**
3. Перейдите на вкладку **"Signing & Capabilities"**

4. **Включите автоматическую подпись:**
   - ✅ Отметьте галочку **"Automatically manage signing"**
   - Выберите **Team** (ваш Apple Developer аккаунт)
   - Если Team не выбран — добавьте Apple ID:
     - Xcode → Settings → Accounts
     - Нажмите **"+"** → добавьте Apple ID
     - Вернитесь в проект → выберите Team

5. **Проверьте Bundle Identifier:**
   - Должен быть: `ru.prirodaspa.app`
   - Если другой — измените на `ru.prirodaspa.app`

### Шаг 3: Выберите правильную схему

1. Вверху Xcode выберите схему: **Runner**
2. Выберите устройство: **Any iOS Device (arm64)**
   - ⚠️ **НЕ выбирайте симулятор!** Для подписи нужен реальный device

### Шаг 4: Соберите проект

**Вариант A: Через Flutter (рекомендуется)**

```bash
cd spa
flutter clean
flutter pub get
cd ios && pod install && cd ..
flutter build ipa --release
```

**Вариант B: Через Xcode**

1. Product → **Archive**
2. Дождитесь завершения сборки
3. Откроется окно **Organizer**

### Шаг 5: Экспорт IPA

1. В **Organizer** выберите ваш архив
2. Нажмите **"Distribute App"**
3. Выберите: **App Store Connect**
4. Выберите: **Upload**
5. Следуйте инструкциям

---

## 🔧 Способ 2: Ручная подпись

Если нужно использовать существующие сертификаты.

### Шаг 1: Подготовка сертификатов

**Импорт сертификата:**
1. Откройте **Keychain Access** (⌘+Space → "Keychain")
2. File → Import Items...
3. Выберите `certificate.p12`
4. Введите пароль: `prirodaspa2018`
5. Сертификат появится в разделе **My Certificates**

**Импорт Provisioning Profile:**
1. Откройте Finder
2. Нажмите **⌘+Shift+G**
3. Введите: `~/Library/MobileDevice/Provisioning Profiles`
4. Скопируйте `profile.mobileprovision` в эту папку

### Шаг 2: Настройка в Xcode

1. В **Signing & Capabilities**:
   - ❌ Снимите галочку **"Automatically manage signing"**
   - Выберите **Team**
   - В **Provisioning Profile** выберите ваш профиль:
     - Должен быть для **App Store Distribution**
     - Bundle ID должен совпадать: `ru.prirodaspa.app`
   - В **Signing Certificate** выберите ваш сертификат:
     - Должен быть **"iPhone Distribution"**

### Шаг 3: Обновите ExportOptions.plist

Откройте `spa/ios/ExportOptions.plist` и измените:

```xml
<key>signingStyle</key>
<string>manual</string>
<key>provisioningProfiles</key>
<dict>
    <key>ru.prirodaspa.app</key>
    <string>Название вашего provisioning profile</string>
</dict>
```

### Шаг 4: Соберите проект

```bash
cd spa
flutter build ipa --release --export-options-plist=ios/ExportOptions.plist
```

---

## 🚀 Способ 3: Через Codemagic (без Mac)

См. подробный гайд: `CODEMAGIC_IOS_SIGNING_GUIDE.md`

### Кратко:

1. Создайте API ключ в App Store Connect
2. Настройте переменные в Codemagic:
   - `APP_STORE_ISSUER_ID`
   - `APP_STORE_KEY_ID`
   - `APP_STORE_PRIVATE_KEY`
3. Запустите сборку в Codemagic

**Bundle ID в codemagic.yaml:** `ru.prirodaspa.app` (уже обновлен)

---

## ✅ Что было исправлено в проекте:

1. ✅ Добавлен `CODE_SIGN_STYLE = Automatic;` во все конфигурации
2. ✅ Bundle ID изменен на `ru.prirodaspa.app` во всех файлах:
   - iOS project.pbxproj
   - Android build.gradle.kts
   - Android AndroidManifest.xml
   - Firebase конфигурации
   - codemagic.yaml

---

## ❌ Решение проблем

### Ошибка: "No signing certificate found"

**Решение:**
1. Xcode → Settings → Accounts
2. Добавьте Apple ID
3. Выберите команду → Download Manual Profiles
4. В проекте выберите Team

### Ошибка: "No provisioning profile found"

**Решение:**
1. Включите "Automatically manage signing"
2. Выберите Team
3. Xcode автоматически создаст provisioning profile

### Ошибка: "Code signing is required"

**Решение:**
1. Signing & Capabilities → включите "Automatically manage signing"
2. Выберите Team
3. Убедитесь, что Bundle ID = `ru.prirodaspa.app`

### Ошибка: "Invalid Bundle Identifier"

**Решение:**
1. Проверьте Bundle ID: должен быть `ru.prirodaspa.app`
2. Убедитесь, что нет пробелов или лишних символов
3. В Signing & Capabilities → Bundle Identifier

### Ошибка: "Bundle identifier is already in use"

**Решение:**
1. Если `ru.prirodaspa.app` уже занят — выберите другой:
   - `ru.priroda.spa`
   - `com.priroda.spa`
   - `ru.prirodaspa.mobile`
2. Замените во всех файлах (см. список выше)

---

## 📝 Чеклист перед сборкой

- [ ] Xcode обновлен до последней версии
- [ ] Проект открыт через `.xcworkspace`
- [ ] CocoaPods зависимости установлены (`pod install`)
- [ ] Apple ID добавлен в Xcode (Settings → Accounts)
- [ ] Team выбран в Signing & Capabilities
- [ ] "Automatically manage signing" включено
- [ ] Bundle ID = `ru.prirodaspa.app`
- [ ] Схема: **Runner** → **Any iOS Device** (не симулятор)
- [ ] Build Configuration: **Release**

---

## 🔍 Проверка подписи

После сборки проверьте подпись:

```bash
# Распакуйте IPA
unzip "PRIRODA SPA.ipa" -d temp_ipa

# Проверьте подпись
codesign -dvvv --entitlements - "temp_ipa/Payload/PRIRODA SPA.app"

# Проверьте provisioning profile
security cms -D -i "temp_ipa/Payload/PRIRODA SPA.app/embedded.mobileprovision"

# Удалите временную папку
rm -rf temp_ipa
```

---

## 📚 Дополнительные ресурсы

- **Apple Developer Documentation:** https://developer.apple.com/documentation
- **Flutter iOS Deployment:** https://docs.flutter.dev/deployment/ios
- **Xcode Help:** ⌘+Shift+? в Xcode

---

## ⚠️ Важно о Firebase

После изменения Bundle ID нужно:

1. **Обновить Firebase конфигурацию:**
   - Откройте Firebase Console: https://console.firebase.google.com
   - Выберите проект `prirodaspa-74540`
   - Добавьте новое iOS приложение с Bundle ID: `ru.prirodaspa.app`
   - Скачайте новый `GoogleService-Info.plist`
   - Замените файл в `spa/ios/Runner/GoogleService-Info.plist`

2. **Обновить Android конфигурацию:**
   - Добавьте новое Android приложение с package name: `ru.prirodaspa.app`
   - Скачайте новый `google-services.json`
   - Замените файл в `spa/android/app/google-services.json`

---

**Готово!** Теперь у вас новый Bundle ID и полный гайд по подписи. 🎉
