# Настройка Firebase и push-уведомлений для Android

Пошаговый гайд: от создания проекта до проверки пушей на устройстве.

---

## 1. Firebase Console

1. Откройте [Firebase Console](https://console.firebase.google.com/) и выберите проект (или создайте новый).
2. **Project settings** (шестерёнка) → вкладка **General** → запомните **Project ID** (пригодится для бэкенда).
3. В разделе **Your apps** нажмите **Add app** → иконка **Android**.
4. **Android package name** должен совпадать с `applicationId` из `android/app/build.gradle` (например `ru.prirodaspa.app`).
5. По желании укажите никнейм приложения и SHA-1 (нужен для Google Sign-In).
6. Зарегистрируйте приложение и скачайте **google-services.json** — понадобится в шаге 3.

---

## 2. Включение Cloud Messaging и (опционально) Authentication

- **Cloud Messaging:** включён по умолчанию после добавления Android-приложения.
- **Authentication:** если используете вход через Email/Google — в **Build** → **Authentication** → **Sign-in method** включите нужные провайдеры.

---

## 3. Добавление google-services.json в проект

1. Скопируйте скачанный **google-services.json** в каталог приложения:
   ```
   spa/android/app/google-services.json
   ```
   (рядом с `build.gradle` внутри `app`.)

2. Убедитесь, что в корневом `android/build.gradle` есть зависимость и плагин:
   ```gradle
   dependencies {
       classpath 'com.google.gms:google-services:4.x.x'
   }
   ```
   И в `android/app/build.gradle` в конце файла:
   ```gradle
   apply plugin: 'com.google.gms.google-services'
   ```
   (В типичном Flutter-проекте это уже подключено.)

---

## 4. Канал уведомлений (Android 8+)

В приложении канал уведомлений создаётся в коде (например, в `PushService` — канал `priroda_push`). Дополнительно в манифесте для FCM ничего указывать не нужно — конфигурация идёт из `google-services.json`.

---

## 5. Flutter: firebase_options.dart

Конфиг Flutter подтягивается через FlutterFire CLI:

```bash
cd spa
dart pub global activate flutterfire_cli   # один раз
firebase login                             # если ещё не входили
flutterfire configure
```

Выберите тот же проект Firebase и платформу Android. Будет создан/обновлён `lib/firebase_options.dart`.

---

## 6. Сборка и запуск

1. Подключите устройство или запустите эмулятор.
2. Соберите и запустите:
   ```bash
   cd spa
   flutter pub get
   flutter run
   ```

Для **release**-сборки (APK/AAB) при необходимости настройте подпись — см. **android/SETUP_SIGNING.md**.

---

## 7. Проверка пушей

1. Войдите в приложение под пользователем (токен FCM регистрируется после входа).
2. В админке создайте тестовую рассылку (push) и отправьте.
3. На устройстве должно прийти уведомление. По тапу приложение открывается (при необходимости — переход по глубокой ссылке).

---

## Частые проблемы (Android)

| Проблема | Что проверить |
|----------|----------------|
| Пуши не приходят | Наличие `google-services.json` в `android/app/`, канал уведомлений создаётся в коде; отключите агрессивную экономию батареи для приложения. |
| «Firebase not initialized» | Вызов `Firebase.initializeApp()` до FCM, наличие `firebase_options.dart`, платформа в `currentPlatform`. |
| Токен не регистрируется на бэке | Пользователь должен быть авторизован; проверить логи приложения и бэкенда, доступность API `/devices/register`. |
| Release-сборка | Подпись: **android/SETUP_SIGNING.md**. |

---

## Что дальше

- Настройка **бэкенда** для отправки пушей: **FIREBASE_CREDENTIALS.md** (сервисный аккаунт) и **backend/ENV_SETUP.md** (FCM v1).
- Общий сценарий: **FIREBASE_SETUP.md**.
