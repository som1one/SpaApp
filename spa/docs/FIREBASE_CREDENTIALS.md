# Как получить всё нужное для Firebase

Чеклист: что скачать/скопировать в Firebase и куда это положить в проекте.

---

## Где брать: Firebase Console

Вход: **[console.firebase.google.com](https://console.firebase.google.com/)** → выберите проект (или создайте новый).

---

## 1. Файл для Android: `google-services.json`

**Откуда:**  
Firebase Console → **Project settings** (шестерёнка рядом с «Обзор проекта») → внизу блок **«Ваши приложения»** → приложение с иконкой Android.

- Если приложения ещё нет: **«Добавить приложение»** → Android → укажите **Package name** (как в `android/app/build.gradle` → `applicationId`, например `ru.prirodaspa.app`) → **Зарегистрировать приложение**.
- На шаге «Загрузите конфигурационный файл» нажмите **Скачать google-services.json**.

**Куда положить:**
```
spa/android/app/google-services.json
```
(рядом с `build.gradle` внутри `app`.)

---

## 2. Файл для iOS: `GoogleService-Info.plist`

**Откуда:**  
Firebase Console → **Project settings** → **«Ваши приложения»** → приложение с иконкой iOS.

- Если приложения ещё нет: **«Добавить приложение»** → iOS → укажите **Apple bundle ID** (как в Xcode, например `ru.prirodaspa.app`) → **Зарегистрировать приложение**.
- Скачайте **GoogleService-Info.plist**.

**Куда положить:**  
Добавить в Xcode в цель **Runner**: перетащить файл в папку `ios/Runner` в проекте и включить **Copy items if needed**. Либо положить файл в каталог:
```
spa/ios/Runner/GoogleService-Info.plist
```
и убедиться, что он добавлен в target Runner в Xcode.

---

## 3. Конфиг Flutter: `firebase_options.dart`

**Откуда:**  
Генерируется локально у вас на машине через FlutterFire CLI (он подтягивает данные из выбранного проекта Firebase).

**Как получить:**

1. Установить CLI (один раз):
   ```bash
   dart pub global activate flutterfire_cli
   ```
2. Войти в Google (если ещё не залогинены):
   ```bash
   firebase login
   ```
3. В корне Flutter-проекта:
   ```bash
   cd spa
   flutterfire configure
   ```
4. Выбрать проект Firebase и платформы (Android, iOS). CLI создаст/обновит файл.

**Куда кладётся:**  
Файл создаётся автоматически по пути:
```
spa/lib/firebase_options.dart
```

При смене проекта Firebase или добавлении приложений — снова запустить `flutterfire configure`.

---

## 4. Бэкенд: отправка пушей (FCM v1 — рекомендуется)

**Откуда:**  
Firebase Console → **Project settings** → вкладка **General** → **Project ID** (скопировать).  
Затем вкладка **Service accounts** → **Generate new private key** — скачать JSON файл сервисного аккаунта.

**Куда положить:**

- **Вариант 1 (файл):** положите JSON в безопасное место на сервере и укажите путь в `.env`:
  ```env
  FCM_PROJECT_ID=ваш-project-id
  GOOGLE_APPLICATION_CREDENTIALS=/путь/к/ключу.json
  ```
- **Вариант 2 (Docker/CI):** содержимое JSON одной строкой в `.env`:
  ```env
  FCM_PROJECT_ID=ваш-project-id
  FCM_CREDENTIALS_JSON={"type":"service_account","project_id":"...",...}
  ```

Перезапустите бэкенд. FCM v1 не требует включения Legacy API в Google Cloud.

### Альтернатива: Legacy Server Key

Если у вас включён **Cloud Messaging API (Legacy)** в Google Cloud:  
Firebase Console → **Project settings** → **Cloud Messaging** → блок **Cloud Messaging API (Legacy)** → **Server key** → в `.env`: `FCM_SERVER_KEY=...`

---

## Краткая таблица

| Что нужно              | Где взять                          | Куда положить |
|------------------------|------------------------------------|----------------|
| `google-services.json` | Firebase → Project settings → Android app → скачать | `spa/android/app/google-services.json` |
| `GoogleService-Info.plist` | Firebase → Project settings → iOS app → скачать | `spa/ios/Runner/` + добавить в target Runner |
| `firebase_options.dart` | Команда `flutterfire configure` в папке `spa` | Создаётся в `spa/lib/firebase_options.dart` |
| FCM v1 (бэкенд)        | Project ID + Service account JSON (Project settings → Service accounts) | В `backend/.env`: `FCM_PROJECT_ID` + `GOOGLE_APPLICATION_CREDENTIALS` или `FCM_CREDENTIALS_JSON` |
| Legacy Server Key     | Firebase → Project settings → Cloud Messaging (Legacy) | В `backend/.env` как `FCM_SERVER_KEY=...` (если не используете v1) |

---

## Дополнительно в Firebase Console

- **Authentication** (Build → Authentication): включите способы входа (Email/Password, Google и т.д.), если используете авторизацию.
- **Cloud Messaging**: для пушей достаточно добавить Android и iOS приложения; для бэкенда настройте FCM v1 (сервисный аккаунт) или Legacy Server Key.

Подробный сценарий — **FIREBASE_SETUP.md**. По платформам: **FIREBASE_IOS.md**, **FIREBASE_ANDROID.md**.
