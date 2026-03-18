# Настройка Firebase и push-уведомлений для iOS

Пошаговый гайд: от создания проекта до проверки пушей на устройстве.

---

## 1. Firebase Console

1. Откройте [Firebase Console](https://console.firebase.google.com/) и выберите проект (или создайте новый).
2. **Project settings** (шестерёнка) → вкладка **General** → запомните **Project ID** (он понадобится для бэкенда).
3. В разделе **Your apps** нажмите **Add app** → иконка **iOS**.
4. **Apple bundle ID** должен совпадать с `PRODUCT_BUNDLE_IDENTIFIER` в Xcode (например `ru.prirodaspa.app`). Узнать: Xcode → выберите target **Runner** → **General** → **Bundle Identifier**.
5. Зарегистрируйте приложение, при необходимости укажите App Store ID и никнейм.
6. Скачайте **GoogleService-Info.plist** и сохраните файл — он понадобится в шаге 3.

---

## 2. Включение Cloud Messaging и (опционально) Authentication

- **Cloud Messaging:** включён по умолчанию после добавления iOS-приложения. Дополнительно ничего включать не нужно.
- **Authentication:** если используете вход через Email/Google/Apple — в **Build** → **Authentication** → **Sign-in method** включите нужные провайдеры.

---

## 3. Добавление GoogleService-Info.plist в Xcode

1. Откройте проект в Xcode:
   ```bash
   cd spa
   open ios/Runner.xcworkspace
   ```
2. В левой панели (Project Navigator) найдите папку **Runner**.
3. Перетащите скачанный **GoogleService-Info.plist** в папку **Runner**.
4. В диалоге включите **Copy items if needed** и убедитесь, что отмечена цель **Runner**.
5. Файл должен появиться в `ios/Runner/GoogleService-Info.plist` и быть в target **Runner**.

---

## 4. Push Notifications capability

1. В Xcode выберите проект (синяя иконка) → target **Runner** → вкладка **Signing & Capabilities**.
2. Нажмите **+ Capability**.
3. Найдите **Push Notifications** и добавьте его.
4. Добавьте **Background Modes** (если ещё нет) и отметьте:
   - **Remote notifications**

(В проекте уже могут быть настроены **Push Notifications** и **Background Modes** с `remote-notification` — тогда этот шаг можно пропустить.)

---

## 5. Entitlements

Убедитесь, что в проекте используется **Runner.entitlements** с включёнными push:

- В **Signing & Capabilities** для **Runner** должна быть ссылка на entitlements-файл.
- В `ios/Runner/Runner.entitlements` не должно быть лишних ограничений для push.

Если файла нет — Xcode создаёт его при добавлении Push Notifications capability.

---

## 6. Flutter: firebase_options.dart

Конфиг Flutter подтягивается через FlutterFire CLI:

```bash
cd spa
dart pub global activate flutterfire_cli   # один раз
firebase login                             # если ещё не входили
flutterfire configure
```

Выберите тот же проект Firebase и платформу iOS. Будет создан/обновлён `lib/firebase_options.dart`.

---

## 7. Сборка и запуск на устройстве

- **Пуши не приходят на симуляторе iOS.** Нужно реальное устройство.
1. Подключите iPhone и выберите его в Xcode как target device.
2. Убедитесь, что **Signing** настроен (Team, provisioning profile). Для push нужен профиль с поддержкой Push Notifications.
3. Соберите и запустите:
   ```bash
   cd spa
   flutter pub get
   flutter run
   ```
   или запуск из Xcode (Run).

---

## 8. Проверка пушей

1. Войдите в приложение под пользователем (токен FCM регистрируется после входа).
2. В админке создайте тестовую рассылку (push) и отправьте на выбранную аудиторию.
3. На iPhone должно прийти уведомление. По тапу приложение открывается (при необходимости — переход по глубокой ссылке).

---

## Частые проблемы (iOS)

| Проблема | Что проверить |
|----------|----------------|
| Пуши не приходят | Реальное устройство (не симулятор), Push Notifications capability, правильный provisioning profile с push. |
| «Firebase not initialized» | Вызов `Firebase.initializeApp()` до FCM, наличие `firebase_options.dart`, платформа в `currentPlatform`. |
| Токен не регистрируется на бэке | Пользователь должен быть авторизован; проверить логи приложения и бэкенда, доступность API `/devices/register`. |
| Ошибка подписи / provisioning | В Apple Developer: App ID с Push Notifications, профиль с этим App ID; в Xcode — выбран правильный Team. |

---

## Что дальше

- Настройка **бэкенда** для отправки пушей: **FIREBASE_CREDENTIALS.md** (сервисный аккаунт) и **backend/ENV_SETUP.md** (FCM v1).
- Общий сценарий: **FIREBASE_SETUP.md**.
