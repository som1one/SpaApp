# Настройка Firebase для PRIRODA SPA

Краткий гайд по настройке Firebase для аутентификации и push-уведомлений в мобильном приложении.

**Пошаговые гайды по платформам:**
- **iOS** — [FIREBASE_IOS.md](FIREBASE_IOS.md) (Xcode, Push capability, проверка на устройстве).
- **Android** — [FIREBASE_ANDROID.md](FIREBASE_ANDROID.md) (google-services.json, канал, подпись).

Что скачать из консоли и куда положить — [FIREBASE_CREDENTIALS.md](FIREBASE_CREDENTIALS.md).

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
3. Для отправки пушей с бэкенда настройте **FCM v1** (сервисный аккаунт) или Legacy (см. раздел 5).

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

## 5. Настройка бэкенда для отправки пушей

Бэкенд поддерживает два варианта:

### Вариант A (рекомендуется): FCM HTTP v1 API

Работает с **Firebase Cloud Messaging API (V1)** — не требует Legacy API.

1. В Firebase Console: **Project settings** (шестерёнка) → вкладка **General** → скопируйте **Project ID**.
2. **Project settings** → вкладка **Service accounts** → **Generate new private key** — скачайте JSON ключа сервисного аккаунта.
3. В `.env` бэкенда задайте:
   ```env
   FCM_PROJECT_ID=ваш-project-id
   GOOGLE_APPLICATION_CREDENTIALS=/путь/к/скачанному-ключу.json
   ```
   Либо вместо пути можно передать JSON одной строкой (удобно для Docker):
   ```env
   FCM_PROJECT_ID=ваш-project-id
   FCM_CREDENTIALS_JSON={"type":"service_account",...}
   ```
4. Перезапустите бэкенд.

Подробнее: **FIREBASE_CREDENTIALS.md** (раздел про сервисный аккаунт) и **backend/ENV_SETUP.md**.

### Вариант B (устаревший): Legacy Server Key

Только если у вас включён **Cloud Messaging API (Legacy)** в Google Cloud:

1. Firebase Console → **Project settings** → вкладка **Cloud Messaging** → блок **Cloud Messaging API (Legacy)** → **Server key**.
2. В `.env` бэкенда:
   ```env
   FCM_SERVER_KEY=ваш-server-key-без-пробелов
   ```
3. Перезапустите бэкенд.

Без настроенного FCM (v1 или Legacy) рассылки с сервера выполняться не будут.

---

## 6. Проверка

### Проверка по API (настройка бэкенда)

Убедиться, что бэкенд видит FCM-ключ (без выдачи самого ключа):

```bash
# Общий health (в т.ч. push)
curl -s https://ваш-домен.ru/health | jq .

# Отдельный эндпоинт статуса push
curl -s https://ваш-домен.ru/api/v1/config/push | jq .
```

Ожидаемый ответ при настроенном FCM:
```json
{
  "fcm_configured": true,
  "message": "FCM настроен, рассылки доступны"
}
```

Если `fcm_configured: false` — настройте FCM v1 (`FCM_PROJECT_ID` + `GOOGLE_APPLICATION_CREDENTIALS` или `FCM_CREDENTIALS_JSON`) или Legacy (`FCM_SERVER_KEY`) в `backend/.env` и перезапустите бэкенд.

### Проверка приложения и рассылок

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
| Пуши не отправляются с бэка | Настроены FCM v1 (FCM_PROJECT_ID + credentials) или FCM_SERVER_KEY в `.env`, бэкенд перезапущен. Проверка: `GET /api/v1/config/push` → `fcm_configured: true`. |

---

## Полезные ссылки

- [Документация Firebase Flutter](https://firebase.google.com/docs/flutter/setup)
- [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging)
- [FlutterFire CLI](https://firebase.flutter.dev/docs/cli/)
