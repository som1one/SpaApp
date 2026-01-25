# 📦 Android: подпись, сборка и публикация в Google Play (PRIRODA SPA)

## ✅ Что уже есть в проекте

- **Package name / applicationId**: `ru.prirodaspa.app`
- **Keystore**: `spa/android/my-release-key.jks`
- **Настройки подписи**: `spa/android/key.properties`
- **Gradle настроен**: `spa/android/app/build.gradle.kts` читает `key.properties` и включает release signing

> ⚠️ Важно: `key.properties` и `*.jks` **нельзя** коммитить в git. Держите их в безопасном месте (бэкап + менеджер паролей).

---

## 1) Проверка подписи (перед релизом)

### 1.1 Проверь, что файлы на месте

- `spa/android/my-release-key.jks`
- `spa/android/key.properties`

### 1.2 Проверь, что alias/пароль корректные (через keytool)

Из папки `spa/android`:

```bash
keytool -list -v -keystore my-release-key.jks -alias <ТВОЙ_ALIAS>
```

Где `<ТВОЙ_ALIAS>` должен совпадать с `keyAlias` в `spa/android/key.properties`.

Если не уверен в alias, можно посмотреть список alias:

```bash
keytool -list -keystore my-release-key.jks
```

---

## 2) Сборка релиза (подписанный AAB для Google Play)

### 2.1 Обнови версию (обязательно для каждого нового релиза)

Файл: `spa/pubspec.yaml`

- `version: 1.0.0+1`
- где **`+1`** — это `versionCode` (должен **строго увеличиваться** для каждого апдейта в Google Play)

Пример:

- было: `version: 1.0.0+1`
- стало: `version: 1.0.1+2`

### 2.2 Собери App Bundle

Из папки `spa`:

```bash
flutter clean
flutter pub get
flutter build appbundle --release
```

Готовый файл:

- `spa/build/app/outputs/bundle/release/app-release.aab`

---

## 3) Публикация в Google Play Console (коротко и по шагам)

### 3.1 Создай приложение

Google Play Console → **All apps** → **Create app**

- **App name**: PRIRODA SPA
- **Default language**: Russian
- **App or game**: App
- **Free/Paid**: выбери (внимание: Paid → Free нельзя вернуть)

### 3.2 Включи Play App Signing (рекомендуется)

Play Console → **App integrity** → **App signing**

- Включи **Play App Signing**
- Ты загружаешь `.aab`, подписанный **upload key** (твой keystore). Это норма.

> ⚠️ Критично: upload keystore нельзя терять. Без него обновления будут болью.

### 3.3 Заполни “карточку” приложения (Store listing)

Play Console → **Store presence** → **Main store listing**

- **Short description**
- **Full description**
- **App icon** (512×512)
- **Feature graphic**
- **Screenshots**
- **Privacy policy URL** (очень желательно/часто обязательно)

Если у вас уже есть тексты — см. `GOOGLE_PLAY_DESCRIPTION_FINAL.md`.

### 3.4 Заполни обязательные анкеты (иначе релиз не пройдет)

Play Console → **App content**:

- **Content rating**
- **Target audience**
- **Data safety**

> Если приложение требует логин, часто нужно заполнить **App access** (как тестировать/дать доступ).

### 3.5 Залей релиз (рекомендую начать с Internal testing)

Play Console → **Testing** → **Internal testing** → **Create new release**

- Загрузи `app-release.aab`
- Заполни “Release notes”
- Сохрани → Review → Publish

После проверки на внутренних тестах:

- **Closed testing** (если нужно)
- **Production** → Create new release → загрузить `.aab` → staged rollout (например 10% → 100%)

---

## 4) Быстрая проверка, что релиз действительно подписан

После сборки можно проверить APK-подпись (если собирал APK):

```bash
jarsigner -verify -verbose -certs spa/build/app/outputs/flutter-apk/app-release.apk
```

Для Google Play обычно достаточно того, что `.aab` собрался и Play Console принял загрузку без ошибок подписи.

---

## 5) Частые ошибки и что делать

- **Play Console ругается на versionCode**: увеличь `+N` в `spa/pubspec.yaml`, пересобери `.aab`.
- **Gradle пишет “Release signing не настроен”**: проверь, что `spa/android/key.properties` существует и `storeFile` указывает на реальный путь (обычно `../my-release-key.jks`).
- **Wrong password / alias not found**: проверь `keyAlias` и пароли; прогоняй `keytool -list`.
- **Package name не совпадает**: в Play Console приложение должно быть **`ru.prirodaspa.app`** (в проекте уже так).

---

## 6) Мини-чеклист перед Production

- [ ] Internal testing установилось и работает
- [ ] `versionCode` увеличен
- [ ] Store listing заполнен (иконки/скрины/описания)
- [ ] Data safety / Content rating / Target audience заполнены
- [ ] Privacy policy URL добавлен
- [ ] `.aab` успешно загружается и проходит pre-launch checks

