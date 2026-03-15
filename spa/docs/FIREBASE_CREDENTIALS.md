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

## 4. Server Key для бэкенда (push-рассылки)

**Откуда:**  
Firebase Console → **Project settings** → вкладка **Cloud Messaging**.

- В блоке **«Cloud Messaging API (Legacy)»** скопируйте **Server key** (длинная строка).
- Если блока нет: перейдите в [Google Cloud Console](https://console.cloud.google.com/) → выберите тот же проект, что и в Firebase → **APIs & Services** → **Library** → найдите **Cloud Messaging API** → **Enable**. После этого Server key появится во вкладке Cloud Messaging в Firebase.

**Куда положить:**  
В `.env` бэкенда (в папке `backend/`):

```env
FCM_SERVER_KEY=скопированный_server_key_без_пробелов
```

Перезапустите бэкенд после сохранения `.env`.

---

## Краткая таблица

| Что нужно              | Где взять                          | Куда положить |
|------------------------|------------------------------------|----------------|
| `google-services.json` | Firebase → Project settings → Android app → скачать | `spa/android/app/google-services.json` |
| `GoogleService-Info.plist` | Firebase → Project settings → iOS app → скачать | `spa/ios/Runner/` + добавить в target Runner |
| `firebase_options.dart` | Команда `flutterfire configure` в папке `spa` | Создаётся в `spa/lib/firebase_options.dart` |
| Server Key (FCM)       | Firebase → Project settings → Cloud Messaging | В `backend/.env` как `FCM_SERVER_KEY=...` |

---

## Дополнительно в Firebase Console

- **Authentication** (Build → Authentication): включите способы входа (Email/Password, Google и т.д.), если используете авторизацию.
- **Cloud Messaging**: для пушей достаточно добавить Android и iOS приложения и взять Server Key; отдельно включать FCM в консоли не нужно.

Подробный сценарий настройки и проверки — в **FIREBASE_SETUP.md** в этой же папке.
