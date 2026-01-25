# 🔧 Исправление проблем с подписью iOS в Xcode

## ✅ Что исправлено:

1. ✅ Добавлен `CODE_SIGN_STYLE = Automatic;` в конфигурации **Debug**
2. ✅ Добавлен `CODE_SIGN_STYLE = Automatic;` в конфигурации **Release**
3. ✅ Добавлен `CODE_SIGN_STYLE = Automatic;` в конфигурации **Profile**

## 🔍 Проверка в Xcode:

### 1. Откройте проект в Xcode:
```bash
cd spa/ios
open Runner.xcworkspace
```
⚠️ **Важно:** Открывайте `.xcworkspace`, а не `.xcodeproj`!

### 2. Проверьте настройки подписи:

1. В Xcode выберите проект **Runner** в левой панели
2. Выберите target **Runner**
3. Перейдите на вкладку **"Signing & Capabilities"**
4. Проверьте:

   ✅ **"Automatically manage signing"** — должно быть **включено** (галочка)
   
   ✅ **Team** — должен быть выбран ваш Apple Developer Team
   
   ✅ **Bundle Identifier** — должен быть `com.prirodaspa.app`

### 3. Выберите правильную схему:

1. Вверху Xcode выберите схему: **Runner**
2. Выберите устройство: **Any iOS Device (arm64)**
   - ⚠️ **НЕ выбирайте симулятор!** Для подписи нужен реальный device

### 4. Проверьте конфигурацию сборки:

1. Product → Scheme → Edit Scheme
2. Выберите **Archive** слева
3. Build Configuration должен быть: **Release** или **Profile**

---

## 🚀 Попробуйте собрать:

### Вариант 1: Через Flutter (рекомендуется)

```bash
cd spa

# Очистите предыдущую сборку
flutter clean

# Установите зависимости
flutter pub get

# Обновите CocoaPods
cd ios
pod install
cd ..

# Соберите IPA
flutter build ipa --release
```

### Вариант 2: Через Xcode

1. В Xcode выберите схему: **Runner** → **Any iOS Device**
2. Product → **Archive**
3. Дождитесь завершения сборки

---

## ❌ Частые ошибки и решения:

### Ошибка 1: "No signing certificate found"

**Решение:**
1. Xcode → Settings → Accounts
2. Добавьте ваш Apple ID (если еще не добавлен)
3. Выберите команду → Download Manual Profiles
4. Вернитесь в проект → Signing & Capabilities
5. Выберите Team

### Ошибка 2: "No provisioning profile found"

**Решение:**
1. В Signing & Capabilities нажмите **"Automatically manage signing"** (включите)
2. Xcode автоматически создаст provisioning profile
3. Если не получается — проверьте, что Bundle ID правильный: `com.prirodaspa.app`

### Ошибка 3: "Code signing is required"

**Решение:**
1. Signing & Capabilities → включите "Automatically manage signing"
2. Выберите Team
3. Убедитесь, что CODE_SIGN_STYLE = Automatic (уже исправлено в project.pbxproj)

### Ошибка 4: "Invalid Bundle Identifier"

**Решение:**
1. Проверьте Bundle Identifier: должен быть `com.prirodaspa.app`
2. Убедитесь, что нет пробелов или лишних символов
3. В Signing & Capabilities → Bundle Identifier

### Ошибка 5: "No profiles for 'com.prirodaspa.app' were found"

**Решение:**
1. Включите "Automatically manage signing"
2. Выберите Team
3. Если проблема осталась — Xcode → Preferences → Accounts → Download Manual Profiles

---

## ✅ Чеклист перед сборкой:

- [ ] Xcode обновлен до последней версии
- [ ] Проект открыт через `.xcworkspace` (не `.xcodeproj`)
- [ ] CocoaPods зависимости установлены (`pod install`)
- [ ] Apple ID добавлен в Xcode (Settings → Accounts)
- [ ] Team выбран в Signing & Capabilities
- [ ] "Automatically manage signing" включено
- [ ] Bundle ID = `com.prirodaspa.app`
- [ ] Схема: **Runner** → **Any iOS Device** (не симулятор)
- [ ] Build Configuration: **Release** или **Profile**

---

## 🔍 Дополнительная диагностика:

### Проверьте настройки в project.pbxproj:

После исправлений в конфигурациях должно быть:
- Debug: `CODE_SIGN_STYLE = Automatic;`
- Release: `CODE_SIGN_STYLE = Automatic;`
- Profile: `CODE_SIGN_STYLE = Automatic;`

### Проверьте через командную строку:

```bash
# Проверьте настройки проекта
cd spa/ios
grep -A 5 "97C147071CF9000F007C117D" Runner.xcodeproj/project.pbxproj | grep CODE_SIGN_STYLE
# Должно показать: CODE_SIGN_STYLE = Automatic;
```

---

## 💡 Рекомендации:

1. **Используйте автоматическую подпись** — это проще и надежнее
2. **Собирайте через Flutter** (`flutter build ipa`) — он автоматически настроит всё правильно
3. **Проверяйте в Xcode** — если ошибки, они будут видны в Signing & Capabilities

---

## 📞 Если всё равно не работает:

1. Очистите проект:
   ```bash
   cd spa
   flutter clean
   cd ios
   rm -rf Pods Podfile.lock
   pod install
   cd ..
   ```

2. Перезапустите Xcode

3. Проверьте логи сборки в Xcode (View → Navigators → Show Report Navigator)

4. Убедитесь, что у вас есть активный Apple Developer аккаунт

---

**Готово!** Теперь попробуйте собрать проект снова. ✅
