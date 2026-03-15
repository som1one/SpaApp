# 🚀 Настройка Xcode Cloud для Flutter проекта

## ✅ Xcode Cloud подходит для публикации IPA!

Xcode Cloud — это CI/CD сервис от Apple, который:
- ✅ **Бесплатно** до 25 часов/месяц (для платных аккаунтов)
- ✅ **Автоматически** загружает билды в App Store Connect
- ✅ **Интегрирован** с TestFlight и App Store
- ✅ Поддерживает **ручной code signing**

---

## 📋 Требования

1. **Apple Developer Account** (платный, $99/год)
2. **Доступ к App Store Connect** (через веб-интерфейс)
3. ⚠️ **Mac НЕ обязателен!** Можно настроить через веб-интерфейс App Store Connect

### ⚠️ Важно про Mac:

- **Билды выполняются на облачных Mac-машинах Apple** (вам Mac не нужен)
- **Настройка workflow:** Можно через веб-интерфейс App Store Connect (без Mac)
- **Настройка проекта:** Если проект уже настроен (code signing, Bundle ID), Mac не нужен
- **Xcode на Mac:** Нужен только если хотите настроить через Xcode IDE (удобнее, но не обязательно)

---

## 🔧 Шаг 1: Настройка проекта (опционально, если есть Mac)

> ⚠️ **Если у вас нет Mac**, этот шаг можно пропустить, если:
> - Bundle ID уже настроен в `Info.plist` (у вас: `ru.prirodaspa.app`)
> - Code signing настроен через сертификаты в Xcode Cloud
> - Проект уже собирался ранее

### 1.1. Откройте проект в Xcode (если есть Mac)

```bash
cd spa/ios
open Runner.xcworkspace
```

⚠️ **Важно:** Открывайте `.xcworkspace`, а не `.xcodeproj`!

### 1.2. Настройте Code Signing (если есть Mac)

1. Выберите проект **Runner** в левой панели
2. Выберите target **Runner**
3. Перейдите на вкладку **"Signing & Capabilities"**
4. Настройте:
   - ✅ **Team:** Ваш Apple Developer Team
   - ✅ **Bundle Identifier:** `ru.prirodaspa.app`
   - ✅ **Signing:** Manual (или Automatic, если хотите)

### 1.3. Проверьте схему сборки (если есть Mac)

1. Product → Scheme → Edit Scheme
2. Выберите **Archive** слева
3. Build Configuration: **Release**

### ✅ Без Mac:

Если Mac нет, просто убедитесь, что:
- Bundle ID правильный в `spa/ios/Runner/Info.plist` (должен быть `ru.prirodaspa.app`)
- Сертификаты загружены в Xcode Cloud (см. Шаг 4)

---

## ☁️ Шаг 2: Настройка Xcode Cloud

### 2.1. Включите Xcode Cloud (БЕЗ Mac!)

**Через веб-интерфейс App Store Connect:**

1. Откройте [App Store Connect](https://appstoreconnect.apple.com)
2. Войдите в свой Apple Developer аккаунт
3. Перейдите в **Xcode Cloud** (в меню слева)
4. Нажмите **"Create Workflow"** или **"Get Started"**
5. Выберите ваш репозиторий (GitHub, GitLab, Bitbucket)
6. Подключите репозиторий к Xcode Cloud

**Альтернатива (если есть Mac):**
- В Xcode: **Product** → **Cloud** → **Create Workflow...**

### 2.2. Настройте Workflow

1. **Название:** `iOS Release`
2. **Триггер:** 
   - Выберите ветку (например, `master`)
   - Или настройте по расписанию

3. **Environment:**
   - **macOS:** Latest
   - **Xcode:** Latest stable

4. **Build Actions:**
   - ✅ **Archive**
   - ✅ **Export for App Store**
   - ✅ **Distribute to App Store Connect**

### 2.3. Настройте Code Signing в Workflow

1. В настройках Workflow найдите **"Signing & Distribution"**
2. Выберите:
   - **Signing:** Manual
   - **Certificate:** Ваш Distribution Certificate
   - **Provisioning Profile:** Ваш App Store Provisioning Profile

   Или используйте **Automatic signing** (если настроили в проекте)

---

## 📝 Шаг 3: Скрипты для Flutter

Скрипты уже созданы в `spa/ios/ci_scripts/`:

### `ci_post_clone.sh`
- Устанавливает CocoaPods
- Выполняется сразу после клонирования репозитория

### `ci_pre_xcodebuild.sh`
- Устанавливает Flutter SDK
- Запускает `flutter pub get`
- Запускает `pod install`
- Генерирует Flutter framework
- Выполняется перед сборкой Xcode

---

## 🔑 Шаг 4: Настройка сертификатов (Manual Signing)

Если используете **Manual Signing**, нужно добавить сертификаты в Xcode Cloud:

### 4.1. В App Store Connect

1. Перейдите в **Users and Access** → **Keys**
2. Создайте или используйте существующий **App Store Connect API Key**
3. Загрузите `.p8` файл

### 4.2. В Xcode Cloud Workflow

1. Откройте настройки Workflow
2. **Signing & Distribution** → **Certificates**
3. Загрузите:
   - **Distribution Certificate** (`.p12` файл)
   - **Provisioning Profile** (`.mobileprovision` файл)
4. Введите пароль от сертификата

---

## 🚀 Шаг 5: Запуск первого билда

### 5.1. Через App Store Connect (БЕЗ Mac!)

1. Откройте [App Store Connect](https://appstoreconnect.apple.com)
2. Перейдите в **Xcode Cloud**
3. Выберите ваш проект
4. Нажмите **"Start Build"** или выберите workflow и запустите

### 5.2. Автоматически

При пуше в выбранную ветку (например, `master`) билд запустится автоматически.

### 5.3. Через Xcode (если есть Mac)

1. **Product** → **Cloud** → **Start Build**
2. Выберите Workflow
3. Дождитесь завершения

---

## 📊 Мониторинг билдов

1. **Xcode:** Product → Cloud → View Builds
2. **App Store Connect:** Xcode Cloud → Ваш проект → Builds
3. **Email уведомления** (настраиваются в App Store Connect)

---

## ✅ Проверка результата

После успешного билда:

1. Перейдите в **App Store Connect** → **My Apps** → Ваше приложение
2. Перейдите в **TestFlight** (если включили)
3. Или в **App Store** → **Versions** (для публикации)

---

## 🔧 Troubleshooting

### Ошибка: "Flutter command not found"

**Решение:** Проверьте, что скрипт `ci_pre_xcodebuild.sh` правильно устанавливает Flutter.

### Ошибка: "No signing certificate found"

**Решение:** 
1. Проверьте настройки Signing в Workflow
2. Убедитесь, что сертификат загружен в Xcode Cloud
3. Проверьте, что Bundle ID совпадает

### Ошибка: "CocoaPods not found"

**Решение:** Скрипт `ci_post_clone.sh` должен установить CocoaPods автоматически.

### Ошибка: "Archive failed"

**Решение:**
1. Проверьте логи билда в Xcode Cloud
2. Убедитесь, что все зависимости установлены
3. Проверьте версию Xcode (должна поддерживать ваш iOS SDK)

---

## 📚 Полезные ссылки

- [Xcode Cloud Documentation](https://developer.apple.com/documentation/xcode)
- [Flutter iOS Deployment](https://docs.flutter.dev/deployment/ios)
- [App Store Connect API](https://developer.apple.com/documentation/appstoreconnectapi)

---

## 🎯 Сравнение: Xcode Cloud vs Codemagic

| Функция | Xcode Cloud | Codemagic |
|---------|-------------|-----------|
| **Цена** | Бесплатно (25 ч/мес) | Платно |
| **Flutter поддержка** | Требует скрипты | Нативная |
| **Интеграция с Apple** | Полная | Через API |
| **Настройка** | Через Xcode/Web | YAML файл |
| **Скорость** | Зависит от очереди | Обычно быстрее |

---

**Готово!** Теперь ваш Flutter проект настроен для публикации через Xcode Cloud! 🎉
