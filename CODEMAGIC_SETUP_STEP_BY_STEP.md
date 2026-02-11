# 📋 Codemagic: Пошаговая настройка Manual Code Signing

## ✅ Что уже сделано

- [x] Сертификат загружен в Codemagic UI: **"Priroda Spa Distribution Certificate"**
- [x] `codemagic.yaml` обновлен для Manual Code Signing
- [x] Email обновлен в `codemagic.yaml`

---

## 📍 Шаг 1: Загрузите Provisioning Profile

### 1.1. Откройте страницу Code Signing Identities

1. Войдите в [Codemagic](https://codemagic.io)
2. Перейдите: **Teams** → **Personal Account** → **Code Signing Identities**
3. Откройте вкладку **"iOS provisioning profiles"**

### 1.2. Загрузите файл

1. Нажмите **"Add provisioning profile"** или перетащите файл
2. Выберите файл:
   ```
   D:\PycharmProjects\Spa\ios_certs_2026\profile.mobileprovision
   ```
   Или альтернативный:
   ```
   D:\PycharmProjects\Spa\Priroda_Spa.mobileprovision
   ```
3. Укажите **Reference name**: `Priroda Spa App Store Profile`
4. Нажмите **"Add provisioning profile"**

### 1.3. Проверка

- После загрузки профиль появится в списке "Code signing profiles"
- Убедитесь, что Bundle ID = `ru.prirodaspa.app`

---

## 📍 Шаг 2: Настройте интеграцию App Store Connect

### 2.1. Откройте страницу Integrations

1. В Codemagic перейдите: **Teams** → **Personal Account** → **Integrations**
2. Проверьте, есть ли интеграция **"Priroda Spa"**

### 2.2. Если интеграции НЕТ — создайте её

1. Нажмите **"Add integration"**
2. Выберите **"App Store Connect"**
3. Заполните форму:

   **Name:**
   ```
   Priroda Spa
   ```

   **Key ID:**
   ```
   BR88FM6FGQ
   ```

   **Issuer ID:**
   - Откройте [App Store Connect](https://appstoreconnect.apple.com)
   - Перейдите: **Users and Access** → **Keys**
   - Найдите ключ с Key ID `BR88FM6FGQ`
   - Скопируйте **Issuer ID** (формат: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

   **Private Key:**
   - Откройте файл: `D:\PycharmProjects\Spa\ios_certs_2026\AuthKey_BR88FM6FGQ.p8`
   - Скопируйте **ВСЁ содержимое** файла (включая строки `-----BEGIN PRIVATE KEY-----` и `-----END PRIVATE KEY-----`)
   - Вставьте в поле "Private Key"
   
   **Содержимое файла должно выглядеть так:**
   ```
   -----BEGIN PRIVATE KEY-----
   MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQgdENKToDGrO/+DJT2
   D0m/iEg4QkOuCo647NwJ2ueQBMqgCgYIKoZIzj0DAQehRANCAARiFFmEHkpDamLx
   s88/d6okToFAWMbSu+rBCYyN6y9T8YuRSxEccGa5BiZNng9nYcsjwKkopz4lb5CB
   4ptozMsv
   -----END PRIVATE KEY-----
   ```

4. Нажмите **"Add integration"**

### 2.3. Проверка

- Интеграция должна появиться в списке с названием **"Priroda Spa"**

---

## 📍 Шаг 3: Удалите старые переменные окружения (если есть)

### 3.1. Откройте Environment Variables

1. В Codemagic откройте ваш проект
2. Перейдите: **Settings** → **Environment variables**
3. Найдите группу переменных (обычно группа "1")

### 3.2. Удалите ненужные переменные

**Удалите эти переменные** (они больше не нужны при Manual Code Signing):

- ❌ `CM_CERTIFICATE` — удалите
- ❌ `CM_PROVISIONING_PROFILE` — удалите  
- ❌ `CM_CERTIFICATE_PASSWORD` — можно удалить (пароль уже в UI)

**Оставьте только** (если нужны для других целей):
- ✅ `APP_STORE_KEY_ID` = `BR88FM6FGQ` (если используется)
- ✅ `APP_STORE_ISSUER_ID` (если используется)
- ✅ `APP_STORE_PRIVATE_KEY` (если используется)

**Примечание:** Если интеграция "Priroda Spa" настроена в UI, эти переменные тоже не нужны.

---

## 📍 Шаг 4: Проверьте codemagic.yaml

### 4.1. Откройте файл

```
D:\PycharmProjects\Spa\codemagic.yaml
```

### 4.2. Проверьте настройки

Убедитесь, что файл содержит:

```yaml
workflows:
  ios-release:
    name: iOS Release
    instance_type: mac_mini_m2
    working_directory: spa
    integrations:
      app_store_connect: Priroda Spa  # ← Должно совпадать с названием интеграции
    ios_signing:
      distribution_type: app_store
      bundle_identifier: ru.prirodaspa.app  # ← Правильный Bundle ID
    publishing:
      app_store_connect:
        auth: integration
        submit_to_testflight: true
```

### 4.3. Проверьте email

Убедитесь, что email указан правильно (строка 47):
```yaml
recipients:
  - farm49595@gmail.com  # ← Ваш email
```

---

## 📍 Шаг 5: Запушьте изменения в Git (если обновляли)

Если вы обновляли `codemagic.yaml`:

```bash
cd D:\PycharmProjects\Spa
git add codemagic.yaml
git commit -m "Update codemagic.yaml"
git push origin master
```

---

## 📍 Шаг 6: Запустите сборку

### 6.1. Откройте проект в Codemagic

1. Войдите в [Codemagic](https://codemagic.io)
2. Откройте ваш проект

### 6.2. Запустите workflow

1. Выберите workflow **"iOS Release"**
2. Нажмите **"Start new build"**
3. Выберите ветку: `master` (или нужную вам)
4. Нажмите **"Start build"**

### 6.3. Что произойдет автоматически

- ✅ Codemagic импортирует сертификат из UI
- ✅ Codemagic импортирует provisioning profile из UI
- ✅ Настроит подпись через `xcode-project use-profiles`
- ✅ Соберет IPA файл
- ✅ Загрузит в TestFlight (если `submit_to_testflight: true`)

---

## ✅ Финальный чеклист перед запуском

Перед запуском сборки убедитесь:

- [ ] ✅ Сертификат загружен: **"Priroda Spa Distribution Certificate"**
- [ ] ⬜ Provisioning Profile загружен (Bundle ID: `ru.prirodaspa.app`)
- [ ] ⬜ Интеграция **"Priroda Spa"** настроена в Codemagic
- [ ] ⬜ Старые переменные `CM_CERTIFICATE` и `CM_PROVISIONING_PROFILE` удалены
- [ ] ⬜ Email обновлен в `codemagic.yaml`
- [ ] ⬜ Bundle ID совпадает везде: `ru.prirodaspa.app`
- [ ] ⬜ `codemagic.yaml` запушен в Git (если обновляли)

---

## 📁 Пути к файлам (для справки)

### Сертификат (.p12):
```
D:\PycharmProjects\Spa\ios_certs_2026\certificate.p12
```
**Пароль:** `12345`

### Provisioning Profile (.mobileprovision):
```
D:\PycharmProjects\Spa\ios_certs_2026\profile.mobileprovision
```
Или:
```
D:\PycharmProjects\Spa\Priroda_Spa.mobileprovision
```

### API ключ (.p8) - используйте этот файл:
```
D:\PycharmProjects\Spa\ios_certs_2026\AuthKey_BR88FM6FGQ.p8
```
**Для интеграции:** Скопируйте всё содержимое файла (текст с BEGIN/END) и вставьте в поле "Private Key"

### Base64 для API ключа (если нужен для переменных окружения):
```
D:\PycharmProjects\Spa\ios_certs_2026\key_base64.txt
```
**Примечание:** Base64 нужен только для переменных окружения, для интеграции в UI используйте оригинальный .p8 файл

---

## 🆘 Решение проблем

### Ошибка: "Integration not found"

**Решение:** 
- Проверьте, что интеграция "Priroda Spa" создана в Codemagic UI
- Убедитесь, что название в `codemagic.yaml` точно совпадает: `Priroda Spa`

### Ошибка: "No provisioning profile found"

**Решение:**
- Проверьте, что профиль загружен в Codemagic UI
- Убедитесь, что Bundle ID в профиле = `ru.prirodaspa.app`
- Проверьте Bundle ID в `codemagic.yaml`: `ru.prirodaspa.app`

### Ошибка: "Certificate not found"

**Решение:**
- Проверьте, что сертификат загружен в Codemagic UI
- Убедитесь, что сертификат не истек (Expires: February 01, 2027 ✅)

### Ошибка при загрузке в TestFlight

**Решение:**
- Проверьте, что интеграция App Store Connect настроена правильно
- Убедитесь, что API ключ имеет права на загрузку билдов
- Проверьте, что приложение создано в App Store Connect с Bundle ID `ru.prirodaspa.app`

---

## 📞 Полезные ссылки

- [Codemagic Documentation - iOS Code Signing](https://docs.codemagic.io/code-signing/ios-code-signing/)
- [App Store Connect](https://appstoreconnect.apple.com)
- [Apple Developer Portal](https://developer.apple.com/account)

---

## 🎯 Готово!

После выполнения всех шагов:

1. ✅ Загрузите Provisioning Profile
2. ✅ Настройте интеграцию App Store Connect
3. ✅ Удалите старые переменные (если есть)
4. ✅ Проверьте `codemagic.yaml`
5. ✅ Запустите сборку

**Удачи! 🚀**
