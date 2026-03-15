# Исправленные проблемы iOS

## ✅ Что исправлено:

### 1. NSAppTransportSecurity (HTTP API)
**Проблема:** API использует HTTP (`http://194.87.187.146:9003`), но в Info.plist не было исключения для этого домена.

**Исправление:** Добавлено исключение для `194.87.187.146` в `NSAppTransportSecurity` → `NSExceptionDomains`.

**Файл:** `spa/ios/Runner/Info.plist`

### 2. Push Notifications Environment
**Проблема:** `aps-environment` был установлен в `development`, но для TestFlight/production нужен `production`.

**Исправление:** Изменено на `production` в `Runner.entitlements`.

**Файл:** `spa/ios/Runner/Runner.entitlements`

### 3. Неблокирующая инициализация
**Проблема:** Firebase и другие сервисы блокировали запуск приложения на iOS.

**Исправление:** 
- Приложение запускается сразу после инициализации StorageService
- Firebase, AuthService и PushService инициализируются в фоне
- Добавлены проверки Firebase перед использованием

**Файлы:** 
- `spa/lib/main.dart`
- `spa/lib/services/auth_service.dart`
- `spa/lib/services/push_service.dart`

### 4. Обработка ошибок
**Проблема:** Ошибки инициализации могли приводить к белому экрану.

**Исправление:**
- Добавлены глобальные обработчики ошибок Flutter
- Добавлена обработка ошибок в `_loadLocale()`
- Все async операции обернуты в try-catch

**Файлы:**
- `spa/lib/main.dart`
- `spa/lib/app.dart`

## ✅ Что уже правильно настроено:

1. **Разрешения (Permissions):**
   - ✅ `NSPhotoLibraryUsageDescription` - доступ к фотогалерее
   - ✅ `NSCameraUsageDescription` - доступ к камере
   - ✅ `NSMicrophoneUsageDescription` - доступ к микрофону

2. **URL Schemes:**
   - ✅ `LSApplicationQueriesSchemes` - https, http, tel, mailto, sms

3. **Firebase:**
   - ✅ `GoogleService-Info.plist` присутствует и правильно настроен
   - ✅ Bundle ID совпадает: `ru.prirodaspa.app`

4. **Локализация:**
   - ✅ Обработка ошибок в `_loadLocale()`
   - ✅ Fallback на русский язык

5. **AppDelegate:**
   - ✅ Правильная регистрация плагинов
   - ✅ Наследование от `FlutterAppDelegate`

## ⚠️ Что нужно проверить после билда:

1. **Push Notifications:**
   - Проверить, что уведомления работают в TestFlight
   - Если не работают, возможно нужно изменить `aps-environment` обратно на `development` для тестирования

2. **HTTP API:**
   - Проверить, что запросы к `http://194.87.187.146:9003` проходят
   - Если есть проблемы, возможно нужно добавить больше исключений

3. **Логи:**
   - Проверить логи в TestFlight на наличие ошибок
   - Убедиться, что все сервисы инициализируются правильно

## 📝 Следующие шаги:

1. Запустить новый билд в Codemagic
2. Загрузить в TestFlight
3. Протестировать на реальном iPhone
4. Проверить логи в TestFlight
5. Если все работает - готово к релизу!
