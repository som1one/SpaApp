# 🚀 Что делать дальше после загрузки сертификата

## ✅ Что уже сделано

- [x] Сертификат **"Priroda Spa Distribution Certificate"** загружен в Codemagic
- [x] `codemagic.yaml` обновлен для Manual Code Signing
- [x] Изменения запушены в Git

---

## 📋 Следующие шаги

### Шаг 1: Загрузите Provisioning Profile

1. В Codemagic перейдите: **Teams** → **Personal Account** → **Code Signing Identities**
2. Откройте вкладку **"iOS provisioning profiles"**
3. Нажмите **"Add provisioning profile"** или перетащите файл
4. Загрузите файл:
   ```
   D:\PycharmProjects\Spa\ios_certs_2026\profile.mobileprovision
   ```
   Или альтернативный:
   ```
   D:\PycharmProjects\Spa\Priroda_Spa.mobileprovision
   ```
5. Укажите **Reference name**: `Priroda Spa App Store Profile`
6. Нажмите **"Add provisioning profile"**

**Проверка:**
- После загрузки вы увидите профиль в списке "Code signing profiles"
- Убедитесь, что Bundle ID совпадает: `ru.prirodaspa.app`

---

### Шаг 2: Проверьте интеграцию App Store Connect

1. В Codemagic перейдите: **Teams** → **Personal Account** → **Integrations**
2. Найдите интеграцию **"Priroda Spa"**

**Если интеграции НЕТ:**

1. Нажмите **"Add integration"**
2. Выберите **"App Store Connect"**
3. Заполните данные:
   - **Name:** `Priroda Spa`
   - **Key ID:** `BR88FM6FGQ`
   - **Issuer ID:** (ваш Issuer ID из App Store Connect)
   - **Private Key:** (Base64 строка из `ios_certs_2026/key_base64.txt`)

**Где найти данные:**
- **Key ID:** `BR88FM6FGQ` (из имени файла `AuthKey_BR88FM6FGQ.p8`)
- **Issuer ID:** App Store Connect → Users and Access → Keys → ваш ключ
- **Private Key:** Откройте `ios_certs_2026/key_base64.txt` и скопируйте всю строку

**Проверка:**
- Интеграция должна появиться в списке с названием **"Priroda Spa"**

---

### Шаг 3: Обновите email в codemagic.yaml

1. Откройте файл `codemagic.yaml`
2. Найдите строку 47:
   ```yaml
   recipients:
     - your-email@example.com
   ```
3. Замените на ваш реальный email:
   ```yaml
   recipients:
     - ваш-email@gmail.com
   ```
4. Сохраните файл

**Важно:** Если не обновите email, уведомления о сборке не придут.

---

### Шаг 4: Запушьте изменения (если обновляли email)

Если вы обновили email в `codemagic.yaml`:

```bash
git add codemagic.yaml
git commit -m "Обновлен email для уведомлений Codemagic"
git push origin master
```

---

### Шаг 5: Запустите сборку

1. В Codemagic откройте ваш проект
2. Выберите workflow **"iOS Release"**
3. Нажмите **"Start new build"**
4. Дождитесь завершения сборки

**Что произойдет автоматически:**
- ✅ Codemagic импортирует сертификат из UI
- ✅ Codemagic импортирует provisioning profile из UI
- ✅ Настроит подпись через `xcode-project use-profiles`
- ✅ Соберет IPA файл
- ✅ Загрузит в TestFlight (если `submit_to_testflight: true`)

---

## 🔍 Проверка перед запуском

Перед запуском сборки убедитесь:

- [ ] ✅ Сертификат загружен: **"Priroda Spa Distribution Certificate"**
- [ ] ⬜ Provisioning Profile загружен (Bundle ID: `ru.prirodaspa.app`)
- [ ] ⬜ Интеграция **"Priroda Spa"** настроена в Codemagic
- [ ] ⬜ Email обновлен в `codemagic.yaml`
- [ ] ⬜ Изменения запушены в Git (если обновляли email)

---

## 📝 Текущий статус workflow

Ваш `codemagic.yaml` настроен следующим образом:

```yaml
workflows:
  ios-release:
    name: iOS Release
    instance_type: mac_mini_m2
    integrations:
      app_store_connect: Priroda Spa  # ← Проверьте, что интеграция существует
    ios_signing:
      distribution_type: app_store
      bundle_identifier: ru.prirodaspa.app  # ← Правильный Bundle ID
    publishing:
      app_store_connect:
        auth: integration
        submit_to_testflight: true  # ← Автоматическая загрузка в TestFlight
```

---

## ⚠️ Важные моменты

### Bundle ID должен совпадать везде:

- ✅ В `codemagic.yaml`: `ru.prirodaspa.app`
- ⬜ В Provisioning Profile: должен быть `ru.prirodaspa.app`
- ⬜ В Xcode проекте: должен быть `ru.prirodaspa.app`
- ⬜ В App Store Connect: должен быть `ru.prirodaspa.app`

### Если Bundle ID не совпадает:

1. Проверьте Provisioning Profile:
   ```bash
   # На Windows можно открыть .mobileprovision в текстовом редакторе
   # Или использовать Python скрипт:
   cd ios_certs_2026
   python test_certificates.py
   ```

2. Если Bundle ID в профиле другой, создайте новый профиль в Apple Developer Portal с правильным Bundle ID.

---

## 🆘 Если что-то не работает

### Ошибка: "Integration not found"

**Решение:** Убедитесь, что интеграция "Priroda Spa" создана в Codemagic UI.

### Ошибка: "No provisioning profile found"

**Решение:** 
- Проверьте, что профиль загружен в Codemagic UI
- Убедитесь, что Bundle ID в профиле = `ru.prirodaspa.app`

### Ошибка: "Certificate not found"

**Решение:**
- Проверьте, что сертификат загружен в Codemagic UI
- Убедитесь, что сертификат не истек (Expires: February 01, 2027 ✅)

### Ошибка при загрузке в TestFlight

**Решение:**
- Проверьте, что интеграция App Store Connect настроена правильно
- Убедитесь, что API ключ имеет права на загрузку билдов

---

## 📞 Полезные ссылки

- [Codemagic Documentation - iOS Code Signing](https://docs.codemagic.io/code-signing/ios-code-signing/)
- [App Store Connect](https://appstoreconnect.apple.com)
- [Apple Developer Portal](https://developer.apple.com/account)

---

## ✅ Готово к запуску!

После выполнения всех шагов:

1. Загрузите Provisioning Profile
2. Проверьте интеграцию App Store Connect
3. Обновите email (если нужно)
4. Запустите сборку в Codemagic

**Удачи! 🎉**
