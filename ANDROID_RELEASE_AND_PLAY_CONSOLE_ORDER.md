# ✅ Android релиз по порядку (ru.prirodaspa.app): подпись → сборка → Google Play

## 0) Проверяем идентификатор приложения

У нас новый package/applicationId: **`ru.prirodaspa.app`**.  
В Google Play Console приложение **должно** быть создано с этим же package name.

---

## 1) Подпись (проверка, что release signing настроен)

1. Убедись, что есть файлы:
   - `spa/android/my-release-key.jks`
   - `spa/android/key.properties`
2. Проверь keystore (alias берём из `key.properties`):

```bash
cd spa/android
keytool -list -v -keystore my-release-key.jks -alias <ВАШ_ALIAS_ИЗ_key.properties>
```

Если `keytool` не найден — установи JDK/Android Studio (нужно для `keytool`).

> Подробно: `ANDROID_SIGNING_COMPLETE_GUIDE.md`

---

## 2) Сборка релиза (AAB для Google Play)

1. Увеличь версию в `spa/pubspec.yaml`:
   - число после `+` — это `versionCode` (должно **увеличиваться** каждый релиз)
2. Собери App Bundle:

```bash
cd spa
flutter clean
flutter pub get
flutter build appbundle --release
```

Готовый файл:
- `spa/build/app/outputs/bundle/release/app-release.aab`

> Быстро: `ANDROID_BUILD_QUICK_START.md`

---

## 3) Что делать дальше в Google Play Console

### 3.1 Создать приложение (если ещё не создано)
All apps → Create app → package будет автоматически привязан к **`ru.prirodaspa.app`** при первой загрузке.

### 3.2 Включить подпись Google (Play App Signing)
App integrity → App signing → включи **Play App Signing** (рекомендуется).

### 3.3 Заполнить обязательные разделы (иначе релиз не пропустит)
App content:
- Content rating
- Target audience
- Data safety

Store presence:
- Main store listing (описания, иконка, скриншоты, политика конфиденциальности)

### 3.4 Залить релиз (рекомендую начать с Internal testing)
Testing → Internal testing → Create new release → загрузи `app-release.aab` → Publish.

После проверки:
- Production → Create new release → staged rollout.

> Подробно: `PLAY_CONSOLE_PUBLISHING_GUIDE.md`

