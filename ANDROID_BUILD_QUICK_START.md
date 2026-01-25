# 🚀 Быстрый старт: Сборка Android приложения

## ✅ Текущее состояние

У вас уже всё настроено:
- ✅ Keystore: `spa/android/my-release-key.jks`
- ✅ Конфигурация: `spa/android/key.properties`
- ✅ Package name: `ru.prirodaspa.app`
- ✅ Build.gradle.kts настроен правильно

---

## 🎯 Сборка для Google Play (App Bundle)

### Команда:

```bash
cd spa
flutter build appbundle --release
```

### Результат:

Файл будет здесь:
```
spa/build/app/outputs/bundle/release/app-release.aab
```

### Загрузка в Google Play:

1. Откройте: https://play.google.com/console
2. Выберите приложение
3. **Production** → **Create new release**
4. Загрузите файл `app-release.aab`
5. Заполните информацию о релизе
6. **Review release**

---

## 📦 Сборка APK (для тестирования)

### Один APK:

```bash
cd spa
flutter build apk --release
```

Результат: `spa/build/app/outputs/flutter-apk/app-release.apk`

### Split APK (по архитектурам):

```bash
cd spa
flutter build apk --split-per-abi --release
```

Результат:
- `app-armeabi-v7a-release.apk` (32-bit)
- `app-arm64-v8a-release.apk` (64-bit)
- `app-x86_64-release.apk` (x86_64)

---

## ✅ Проверка перед сборкой

- [x] Keystore существует: `spa/android/my-release-key.jks`
- [x] Конфигурация существует: `spa/android/key.properties`
- [x] Package name: `ru.prirodaspa.app`
- [ ] Flutter зависимости установлены (`flutter pub get`)

---

## 🔧 Если что-то не работает

### Ошибка: "Release signing не настроен"

**Решение:**
1. Проверьте, что `spa/android/key.properties` существует
2. Проверьте путь к keystore в файле (должен быть `../my-release-key.jks`)

### Ошибка: "Wrong password"

**Решение:**
Проверьте пароли в `key.properties` (не публикуйте их в чат/репозиторий).

### Ошибка: "Keystore file not found"

**Решение:**
Убедитесь, что файл `my-release-key.jks` находится в `spa/android/`

---

## 📝 Обновление версии

Перед каждым новым релизом обновите версию в `pubspec.yaml`:

```yaml
version: 1.0.1+2  # +2 — это versionCode (должен увеличиваться)
```

Затем соберите новый App Bundle:
```bash
flutter build appbundle --release
```

---

## 🔐 Безопасность

⚠️ **ВАЖНО:**
- Сохраните `my-release-key.jks` в безопасном месте
- Сохраните пароли (значения из `key.properties`)
- Без keystore нельзя обновлять приложение в Google Play!

---

## 📚 Подробная инструкция

См. файл: `ANDROID_SIGNING_COMPLETE_GUIDE.md`

---

## ✅ Готово к сборке!

Просто выполните:
```bash
cd spa
flutter build appbundle --release
```

**И всё!** 🎉
