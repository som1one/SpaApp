# 🔐 Настройка Manual Code Signing в Codemagic

## ✅ Что изменилось

Поддержка Codemagic обновила workflow для использования **Manual Code Signing**. Теперь не нужно вручную импортировать сертификаты через скрипты — Codemagic сделает это автоматически.

---

## 📋 Шаги настройки

### 1. Загрузите сертификаты в Codemagic UI

1. Войдите в [Codemagic](https://codemagic.io)
2. Перейдите: **Teams** → **Personal Account** → **Code Signing Identities**
3. Загрузите файлы:

   **iOS Certificate:**
   - Нажмите **"Add certificate"**
   - Загрузите ваш `.p12` файл
   - Введите пароль от сертификата (если есть)

   **iOS Provisioning Profile:**
   - Нажмите **"Add provisioning profile"**
   - Загрузите ваш `.mobileprovision` файл

---

### 2. Проверьте интеграцию App Store Connect

1. Перейдите: **Teams** → **Personal Account** → **Integrations**
2. Найдите интеграцию **"Priroda Spa"** (или создайте новую)
3. Если интеграции нет, создайте её:
   - Нажмите **"Add integration"**
   - Выберите **"App Store Connect"**
   - Название: `Priroda Spa`
   - Настройте API ключ (Key ID, Issuer ID, Private Key)

---

### 3. Обновите email в codemagic.yaml

В файле `codemagic.yaml` найдите строку:
```yaml
recipients:
  - your-email@example.com
```

Замените на ваш реальный email:
```yaml
recipients:
  - ваш-email@gmail.com
```

---

### 4. Проверьте Bundle ID

В `codemagic.yaml` указан Bundle ID: `ru.prirodaspa.app`

Убедитесь, что он совпадает с:
- Bundle ID в вашем Xcode проекте
- Bundle ID в Provisioning Profile
- Bundle ID в App Store Connect

---

## 🚀 Запуск сборки

После настройки:

1. Запушьте обновленный `codemagic.yaml` в Git
2. Запустите сборку в Codemagic
3. Codemagic автоматически:
   - Импортирует сертификаты из UI
   - Настроит подпись через `xcode-project use-profiles`
   - Соберет IPA
   - Загрузит в TestFlight (если `submit_to_testflight: true`)

---

## 🔍 Что делает новый workflow

1. **`ios_signing`** — автоматически использует сертификаты из UI
2. **`xcode-project use-profiles`** — настраивает подпись в Xcode проекте
3. **`integrations: app_store_connect: Priroda Spa`** — использует интеграцию для загрузки
4. **`submit_to_testflight: true`** — автоматически отправляет в TestFlight

---

## ⚠️ Важно

- **НЕ нужно** больше использовать переменные `CM_CERTIFICATE` и `CM_PROVISIONING_PROFILE`
- **НЕ нужно** вручную импортировать сертификаты через скрипты
- Сертификаты должны быть загружены **только через UI Codemagic**

---

## 📝 Проверка перед запуском

- [ ] Сертификат загружен в Codemagic UI
- [ ] Provisioning Profile загружен в Codemagic UI
- [ ] Интеграция "Priroda Spa" настроена в Codemagic
- [ ] Email обновлен в `codemagic.yaml`
- [ ] Bundle ID совпадает везде (`ru.prirodaspa.app`)
- [ ] `codemagic.yaml` запушен в Git

---

## 🆘 Если что-то не работает

1. Проверьте логи сборки в Codemagic
2. Убедитесь, что сертификаты загружены правильно
3. Проверьте, что Bundle ID совпадает
4. Убедитесь, что интеграция App Store Connect настроена

---

**Готово!** Теперь workflow должен работать автоматически. 🎉
