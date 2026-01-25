# 🍎 Гайд: Подпись и финальная сборка iOS приложения в Xcode

## 🎯 Обзор

Этот гайд описывает процесс подписания и сборки финального IPA файла для iOS приложения в Xcode.

**Информация о проекте:**
- **Bundle ID:** `com.prirodaspa.app`
- **Название:** PRIRODA SPA
- **Тип проекта:** Flutter
- **Рабочая директория:** `spa/ios/`

---

## 📋 Подготовка

### Что нужно иметь:

1. ✅ **Mac с установленным Xcode** (последняя версия)
2. ✅ **Apple Developer аккаунт** (платный, $99/год)
3. ✅ **Сертификат подписи** (Distribution Certificate)
4. ✅ **Provisioning Profile** (App Store Distribution)
5. ✅ **Flutter проект** собран и готов

---

## 🔐 Шаг 1: Подготовка сертификатов

### Вариант A: У вас уже есть сертификаты

Если у вас есть файлы:
- `certificate.p12` (или `.cer` + `private_key.pem`)
- `profile.mobileprovision` (или `Priroda_Spa.mobileprovision`)

**Импорт сертификата:**
1. Откройте **Keychain Access** (⌘+Space, введите "Keychain")
2. Перейдите: **File** → **Import Items...**
3. Выберите `certificate.p12`
4. Введите пароль: `prirodaspa2018`
5. Сертификат появится в разделе **My Certificates**

**Импорт Provisioning Profile:**
1. Откройте Finder
2. Нажмите **⌘+Shift+G** (Go to Folder)
3. Введите: `~/Library/MobileDevice/Provisioning Profiles`
4. Скопируйте `profile.mobileprovision` в эту папку
5. Переименуйте файл в UUID (можно узнать через Xcode)

### Вариант B: Создание через Xcode (автоматически)

1. Откройте Xcode
2. Перейдите: **Xcode** → **Settings** → **Accounts**
3. Нажмите **"+"** и добавьте ваш Apple ID
4. Выберите аккаунт → **Download Manual Profiles**
5. Xcode автоматически создаст сертификаты и профили

---

## 🛠️ Шаг 2: Настройка проекта в Xcode

### 2.1. Открытие проекта

```bash
# Перейдите в папку iOS проекта
cd spa/ios

# Откройте workspace (НЕ project!)
open Runner.xcworkspace
```

⚠️ **Важно:** Открывайте `.xcworkspace`, а не `.xcodeproj` (нужно для CocoaPods)

### 2.2. Настройка Signing & Capabilities

1. В Xcode выберите проект **Runner** в левой панели
2. Выберите target **Runner**
3. Перейдите на вкладку **Signing & Capabilities**

#### Для автоматической подписи (рекомендуется):

1. Отметьте **"Automatically manage signing"**
2. Выберите **Team** (ваш Apple Developer аккаунт)
3. Xcode автоматически:
   - Создаст/обновит сертификат
   - Создаст/обновит provisioning profile
   - Настроит Bundle ID

#### Для ручной подписи:

1. Снимите галочку **"Automatically manage signing"**
2. Выберите **Team**
3. В **Provisioning Profile** выберите ваш профиль:
   - Должен быть для **App Store Distribution**
   - Bundle ID должен совпадать: `com.prirodaspa.app`
4. В **Signing Certificate** выберите ваш сертификат:
   - Должен быть **"iPhone Distribution"**

### 2.3. Проверка Bundle ID

1. Убедитесь, что **Bundle Identifier** = `com.prirodaspa.app`
2. Если нужно изменить: **Signing & Capabilities** → **Bundle Identifier**

### 2.4. Проверка версии и build number

1. Выберите target **Runner**
2. Вкладка **General**
3. Проверьте:
   - **Version:** текущая версия (например, `1.0.0`)
   - **Build:** номер сборки (например, `1`)

Или установите через Flutter:
```bash
flutter build ipa --build-name=1.0.0 --build-number=1
```

---

## 📦 Шаг 3: Сборка через Flutter (рекомендуется)

Самый простой способ для Flutter проектов:

### 3.1. Сборка IPA

```bash
# Перейдите в корень проекта
cd spa

# Установите зависимости
flutter pub get

# Установите CocoaPods зависимости
cd ios
pod install
cd ..

# Соберите IPA
flutter build ipa --release
```

### 3.2. Результат

IPA файл будет в:
```
spa/build/ios/ipa/PRIRODA SPA.ipa
```

### 3.3. Проверка подписи

```bash
# Проверьте, что IPA подписан
codesign -dvvv --entitlements - "spa/build/ios/ipa/PRIRODA SPA.ipa"
```

---

## 🏗️ Шаг 4: Сборка через Xcode (альтернатива)

Если нужно собрать через Xcode напрямую:

### 4.1. Настройка схемы

1. В Xcode выберите схему **Runner** (вверху слева)
2. Выберите устройство: **Any iOS Device (arm64)**
   - ⚠️ **НЕ выбирайте симулятор!** Для App Store нужен реальный device

### 4.2. Archive (Архивация)

1. Меню: **Product** → **Archive**
2. Дождитесь завершения сборки
3. Откроется окно **Organizer**

### 4.3. Экспорт IPA

1. В **Organizer** выберите ваш архив
2. Нажмите **"Distribute App"**
3. Выберите метод распространения:
   - **App Store Connect** - для публикации в App Store
   - **Ad Hoc** - для тестирования на конкретных устройствах
   - **Enterprise** - для корпоративного распространения
   - **Development** - для разработки

4. Выберите **"Export"**
5. Выберите опции:
   - ✅ **Include bitcode** (обычно выключено)
   - ✅ **Upload your app's symbols** (включено)
6. Выберите команду (Team)
7. Выберите provisioning profile (если ручная подпись)
8. Нажмите **"Export"**
9. Выберите папку для сохранения

### 4.4. Результат

IPA файл будет в выбранной папке:
```
PRIRODA SPA.ipa
```

---

## 🔍 Шаг 5: Проверка подписи

### Проверка сертификата в IPA

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

### Что должно быть:

✅ **Certificate:** `iPhone Distribution: ...`  
✅ **Bundle ID:** `com.prirodaspa.app`  
✅ **Provisioning Profile:** для App Store Distribution  
✅ **Team ID:** ваш Team ID (например, `A7X8837V79`)

---

## 📤 Шаг 6: Загрузка в App Store Connect

### 6.1. Через Xcode

1. В **Organizer** выберите архив
2. Нажмите **"Distribute App"**
3. Выберите **"App Store Connect"**
4. Выберите **"Upload"**
5. Следуйте инструкциям
6. После загрузки приложение появится в App Store Connect

### 6.2. Через Transporter (альтернатива)

1. Установите **Transporter** из App Store
2. Откройте Transporter
3. Перетащите IPA файл
4. Нажмите **"Deliver"**
5. Войдите с Apple ID
6. Дождитесь загрузки

### 6.3. Через командную строку (altool)

```bash
# Загрузите через altool (устаревший, но работает)
xcrun altool --upload-app \
  --type ios \
  --file "PRIRODA SPA.ipa" \
  --username "your@email.com" \
  --password "app-specific-password"
```

### 6.4. Через командную строку (notarytool) - новый способ

```bash
# Создайте app-specific password в appleid.apple.com
# Затем загрузите:
xcrun notarytool submit "PRIRODA SPA.ipa" \
  --apple-id "your@email.com" \
  --team-id "A7X8837V79" \
  --password "app-specific-password" \
  --wait
```

---

## ⚙️ Настройка ExportOptions.plist

Ваш файл `spa/ios/ExportOptions.plist` уже настроен:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>app-store</string>
    <key>uploadBitcode</key>
    <false/>
    <key>uploadSymbols</key>
    <true/>
    <key>compileBitcode</key>
    <false/>
    <key>signingStyle</key>
    <string>automatic</string>
</dict>
</plist>
```

### Для ручной подписи измените:

```xml
<key>signingStyle</key>
<string>manual</string>
<key>provisioningProfiles</key>
<dict>
    <key>com.prirodaspa.app</key>
    <string>Название вашего provisioning profile</string>
</dict>
```

---

## 🐛 Решение проблем

### Ошибка: "No signing certificate found"

**Решение:**
1. Проверьте, что сертификат импортирован в Keychain
2. Убедитесь, что сертификат не истек
3. Создайте новый сертификат через Xcode → Settings → Accounts

### Ошибка: "No provisioning profile found"

**Решение:**
1. Проверьте, что provisioning profile в папке `~/Library/MobileDevice/Provisioning Profiles`
2. Убедитесь, что Bundle ID совпадает: `com.prirodaspa.app`
3. Проверьте, что профиль для App Store Distribution

### Ошибка: "Code signing is required"

**Решение:**
1. Перейдите в **Signing & Capabilities**
2. Включите **"Automatically manage signing"** или выберите профиль вручную
3. Убедитесь, что Team выбран

### Ошибка: "Bundle identifier is already in use"

**Решение:**
1. Измените Bundle ID на уникальный
2. Или используйте существующий Bundle ID, если у вас есть доступ к нему

### Ошибка при сборке Flutter: "CocoaPods not installed"

**Решение:**
```bash
# Установите CocoaPods
sudo gem install cocoapods

# Обновите pods
cd spa/ios
pod install
```

---

## 📝 Чеклист перед финальной сборкой

- [ ] Xcode обновлен до последней версии
- [ ] Flutter проект собран без ошибок
- [ ] CocoaPods зависимости установлены (`pod install`)
- [ ] Сертификат импортирован в Keychain
- [ ] Provisioning Profile импортирован
- [ ] Bundle ID = `com.prirodaspa.app`
- [ ] Team выбран в Xcode
- [ ] Signing настроен (автоматический или ручной)
- [ ] Версия и build number установлены
- [ ] Выбрано устройство "Any iOS Device" (не симулятор)
- [ ] ExportOptions.plist настроен правильно

---

## 🚀 Быстрая сборка (команды)

```bash
# Полная сборка через Flutter
cd spa
flutter clean
flutter pub get
cd ios && pod install && cd ..
flutter build ipa --release

# IPA будет в: spa/build/ios/ipa/PRIRODA SPA.ipa
```

---

## 💡 Советы

1. **Всегда используйте Release конфигурацию** для финальной сборки
2. **Проверяйте подпись** перед загрузкой в App Store Connect
3. **Тестируйте на TestFlight** перед публикацией
4. **Сохраняйте сертификаты** в безопасном месте
5. **Используйте автоматическую подпись**, если возможно - это проще

---

## 📚 Дополнительные ресурсы

- **Apple Developer Documentation:** https://developer.apple.com/documentation
- **Flutter iOS Deployment:** https://docs.flutter.dev/deployment/ios
- **Xcode Help:** ⌘+Shift+? в Xcode

---

**Удачи с подписанием и сборкой! 🎉**

