# Настройка Firebase для PRIRODA SPA

Краткий гайд по настройке Firebase для аутентификации и push-уведомлений в мобильном приложении.

---

## 1. Создание проекта Firebase

1. Откройте [Firebase Console](https://console.firebase.google.com/).
2. Нажмите **«Добавить проект»** (или выберите существующий).
3. Укажите имя проекта (например, `prirodaspa`), при необходимости включите Google Analytics.
4. Дождитесь создания проекта.

---

## 2. Регистрация приложений

### Android

1. В проекте нажмите **«Добавить приложение»** → иконка Android.
2. **Package name** должен совпадать с `applicationId` из `android/app/build.gradle` (например, `ru.prirodaspa.app`).
3. По желании укажите никнейм и SHA-1 (нужен для Google Sign-In).
4. Скачайте **`google-services.json`** и положите в каталог:
   ```
   spa/android/app/google-services.json
   ```
5. В `android/app/build.gradle` должна быть строка:
   ```gradle
   apply plugin: 'com.google.gms.google-services'
   ```
   (обычно подключается через корневой `build.gradle` и плагин `com.google.gms.google-services`.)

### iOS

1. В проекте нажмите **«Добавить приложение»** → иконка iOS.
2. **Bundle ID** должен совпадать с `PRODUCT_BUNDLE_IDENTIFIER` в Xcode (например, `ru.prirodaspa.app`).
3. Скачайте **`GoogleService-Info.plist`** и добавьте его в Xcode в цель **Runner** (перетащите в `ios/Runner` и отметьте «Copy items if needed»).
4. В Xcode: **Signing & Capabilities** → **+ Capability** → добавьте **Push Notifications**.
5. Для аутентификации через Google при необходимости настройте URL scheme в **Info** → **URL Types**.

### Обновление конфигурации Flutter (firebase_options.dart)

После добавления/изменения приложений в Firebase обновите конфиг Flutter:

```bash
cd spa
dart pub global activate flutterfire_cli
flutterfire configure
```

Будет создан/обновлён `lib/firebase_options.dart` с ключами для каждой платформы. Файл уже есть в проекте — при смене проекта или приложений в Firebase запускайте `flutterfire configure` заново.

---

## 3. Включение сервисов в Firebase

### Authentication

1. В консоли: **Build** → **Authentication** → **Get started**.
2. На вкладке **Sign-in method** включите нужные провайдеры:
   - **Email/Password**
   - **Google** (при использовании Google Sign-In)
   - При необходимости — другие (Apple, VK и т.д.).

### Cloud Messaging (FCM) — для push-уведомлений

1. **Build** → **Cloud Messaging**.
2. FCM включён по умолчанию после добавления Android/iOS приложений.
3. Для отправки пушей с бэкенда понадобится **Server Key** (см. раздел 5).

---

## 4. Настройка push в приложении

### Android

- В `AndroidManifest.xml` ничего дополнительно для FCM указывать не нужно (используется конфиг из `google-services.json`).
- Канал уведомлений создаётся в коде (`PushService`, канал `priroda_push`). Для Android 8+ этого достаточно.

### iOS

- **Push Notifications** capability добавлена в шаге 2 (iOS).
- Для тестов на симуляторе пуши не приходят — нужен реальный iPhone.
- В **Signing & Capabilities** проверьте, что включён **Background Modes** и при необходимости отмечен **Remote notifications**.

### Поведение в приложении

- **Foreground:** приложение само показывает уведомление через `flutter_local_notifications` (чтобы пуши были видны при открытом приложении).
- **Background / Terminated:** уведомление показывает система; по тапу открывается приложение и выполняется переход на главный экран (при необходимости можно доработать глубокую ссылку по `campaign_id`).

---

## 5. Server Key для бэкенда (отправка пушей)

Чтобы админка могла отправлять рассылки на устройства:

1. В Firebase Console: **Project settings** (шестерёнка) → вкладка **Cloud Messaging**.
2. В блоке **Cloud Messaging API (Legacy)** найдите **Server key**.  
   Если блока нет — включите **Cloud Messaging API (Legacy)** в [Google Cloud Console](https://console.cloud.google.com/) для проекта Firebase (APIs & Services → Enabled APIs).
3. Скопируйте **Server key** и добавьте в `.env` бэкенда:
   ```env
   FCM_SERVER_KEY=ваш-server-key-без-пробелов
   ```
4. Перезапустите бэкенд. Без `FCM_SERVER_KEY` рассылки с сервера выполняться не будут (в логах будет предупреждение).

Подробнее про переменные бэкенда см. `backend/ENV_SETUP.md` (раздел про FCM).

---

## 6. Проверка

1. **Сборка:**
   ```bash
   cd spa
   flutter pub get
   flutter run
   ```
2. Войти в приложение под пользователем (регистрация/логин).
3. Убедиться, что в логах есть сообщение об успешной регистрации FCM-токена и устройстве на бэкенде.
4. В админке создать тестовую рассылку (push), отправить — уведомление должно прийти на устройство. На симуляторе iOS пуши не приходят.

---

## 7. Частые проблемы

| Проблема | Что проверить |
|----------|----------------|
| На iOS не приходят пуши | Реальное устройство, Push Notifications capability, правильный provisioning profile. |
| На Android не приходят пуши | Наличие `google-services.json`, канал уведомлений (создаётся в коде), не убита батарейная оптимизация для приложения. |
| «Firebase not initialized» | Вызов `Firebase.initializeApp()` до работы с FCM, наличие `firebase_options.dart` и корректная платформа в `currentPlatform`. |
| Токен не регистрируется на бэке | Пользователь должен быть авторизован; проверить логи приложения и бэкенда, доступность API `/devices/register`. |
| Пуши не отправляются с бэка | В `.env` задан `FCM_SERVER_KEY`, бэкенд перезапущен после изменения `.env`. |

---

## Полезные ссылки

- [Документация Firebase Flutter](https://firebase.google.com/docs/flutter/setup)
- [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging)
- [FlutterFire CLI](https://firebase.flutter.dev/docs/cli/)
