# 🎯 Точная настройка Codemagic для загрузки IPA

## ✅ Все значения для копирования

---

## 📋 ШАГ 1: Откройте Codemagic

1. Перейдите на **https://codemagic.io**
2. Войдите в аккаунт
3. Выберите проект **Spa** (или создайте новый)

---

## 🔑 ШАГ 2: Настройте Environment Variables

### 2.1. Откройте настройки переменных

1. В проекте перейдите: **Settings** → **Environment variables**
2. Убедитесь, что группа **"1"** существует
   - Если нет → нажмите **"Add group"** → введите **"1"** (без кавычек)

### 2.2. Добавьте переменные в группу "1"

**ВАЖНО:** Все переменные должны быть в группе **"1"** (именно так, как указано в `codemagic.yaml`)

#### Переменная 1: `APP_STORE_KEY_ID`

- **Name:** `APP_STORE_KEY_ID`
- **Value:** `BR88FM6FGQ`
- **Secure:** ✅ Да (галочка)
- **Group:** `1`

#### Переменная 2: `APP_STORE_ISSUER_ID`

- **Name:** `APP_STORE_ISSUER_ID`
- **Value:** `4fbfcedf-2756-4b8e-8fc3-b17978e9532a`
- **Secure:** ✅ Да (галочка)
- **Group:** `1`

#### Переменная 3: `APP_STORE_PRIVATE_KEY`

- **Name:** `APP_STORE_PRIVATE_KEY`
- **Value:** Скопируйте из файла `ios_certs_2026/key_base64.txt`
  - Откройте файл `ios_certs_2026/key_base64.txt`
  - Скопируйте **ВСЮ строку** (одной строкой, без переносов)
  - Текущее значение: `LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JR1RBZ0VBTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEJIa3dkd0lCQVFRZ2RFTktUb0RHck8vK0RKVDIKRDBtL2lFZzRRa091Q282NDdOd0oydWVRQk1xZ0NnWUlLb1pJemowREFRZWhSQU5DQUFSaUZGbUVIa3BEYW1MeApzODgvZDZva1RvRkFXTWJTdStyQkNZeU42eTlUOFl1UlN4RWNjR2E1QmlaTm5nOW5ZY3Nqd0trb3B6NGxiNUNCCjRwdG96TXN2Ci0tLS0tRU5EIFBSSVZBVEUgS0VZLS0tLS0=`
- **Secure:** ✅ Да (галочка)
- **Group:** `1`

#### Переменная 4: `CM_CERTIFICATE`

- **Name:** `CM_CERTIFICATE`
- **Value:** Скопируйте из файла `ios_certs_2026/certificate_base64.txt`
  - Откройте файл `ios_certs_2026/certificate_base64.txt`
  - Скопируйте **ВСЮ строку** (одной строкой, без переносов)
- **Secure:** ✅ Да (галочка)
- **Group:** `1`

#### Переменная 5: `CM_PROVISIONING_PROFILE`

- **Name:** `CM_PROVISIONING_PROFILE`
- **Value:** Скопируйте из файла `ios_certs_2026/profile_base64.txt`
  - Откройте файл `ios_certs_2026/profile_base64.txt`
  - Скопируйте **ВСЮ строку** (одной строкой, без переносов)
- **Secure:** ✅ Да (галочка)
- **Group:** `1`

#### Переменная 6: `CM_CERTIFICATE_PASSWORD` (опционально)

- **Name:** `CM_CERTIFICATE_PASSWORD`
- **Value:** `12345`
- **Secure:** ✅ Да (галочка)
- **Group:** `1`

**Примечание:** Если пароль другой, укажите правильный.

---

## 📝 ШАГ 3: Проверьте codemagic.yaml

### 3.1. Убедитесь, что файл в репозитории

Файл `codemagic.yaml` должен быть в **корне репозитория** (не в папке `spa/`)

### 3.2. Проверьте группу переменных

В `codemagic.yaml` должно быть:

```yaml
environment:
  groups:
    - "1"  # Группа с переменными
```

**ВАЖНО:** Группа должна быть **"1"** (в кавычках, строка)

### 3.3. Проверьте working_directory

```yaml
working_directory: spa
```

Это правильно — проект находится в папке `spa/`

---

## 🚀 ШАГ 4: Запустите билд

### 4.1. Выберите workflow

1. В Codemagic перейдите в **Builds**
2. Нажмите **Start new build**
3. Выберите workflow: **iOS Release** (или как он называется в вашем `codemagic.yaml`)

### 4.2. Выберите ветку

- Выберите ветку: **master** (или нужную вам)

### 4.3. Запустите

- Нажмите **Start new build**

---

## ✅ ШАГ 5: Проверьте логи

### Что должно быть в логах:

#### ✅ Успешная сборка:

```
🔐 Декодирование сертификатов и профилей...
✅ Сертификат декодирован (3243 байт)
✅ Provisioning profile декодирован (XXXX байт)
🔑 Настройка keychain...
✅ Keychain настроен
🏗️ Сборка IPA...
🔑 Подготовка API ключа для загрузки...
✅ API ключ подготовлен
📋 Key ID: 2N2LSDXR7U
📋 Issuer ID: 4fbfcedf-2756-4b8e-8fc3-b17978e9532a
✅ Upload successful!
```

#### ❌ Если ошибка 401:

```
ERROR: 401 Unauthorized
```

**Решение:**
1. Проверьте `APP_STORE_KEY_ID` = `BR88FM6FGQ`
2. Проверьте `APP_STORE_ISSUER_ID` = `4fbfcedf-2756-4b8e-8fc3-b17978e9532a`
3. Проверьте `APP_STORE_PRIVATE_KEY` - должна быть полная Base64 строка
4. Проверьте в App Store Connect:
   - https://appstoreconnect.apple.com → Users and Access → Keys
   - Ключ `BR88FM6FGQ` должен иметь роль **App Manager** или **Admin**
   - Сервис **App Store Connect API** должен быть включен

#### ❌ Если ошибка "CM_CERTIFICATE не установлен":

**Решение:**
1. Проверьте, что переменная `CM_CERTIFICATE` добавлена в группу **"1"**
2. Убедитесь, что Base64 строка скопирована полностью (одной строкой)

#### ❌ Если ошибка "CM_PROVISIONING_PROFILE не установлен":

**Решение:**
1. Проверьте, что переменная `CM_PROVISIONING_PROFILE` добавлена в группу **"1"**
2. Убедитесь, что Base64 строка скопирована полностью (одной строкой)

---

## 📋 Чеклист перед запуском

- [ ] ✅ Группа **"1"** создана в Codemagic
- [ ] ✅ `APP_STORE_KEY_ID` = `BR88FM6FGQ` (в группе "1")
- [ ] ✅ `APP_STORE_ISSUER_ID` = `4fbfcedf-2756-4b8e-8fc3-b17978e9532a` (в группе "1")
- [ ] ✅ `APP_STORE_PRIVATE_KEY` = Base64 из `key_base64.txt` (в группе "1")
- [ ] ✅ `CM_CERTIFICATE` = Base64 из `certificate_base64.txt` (в группе "1")
- [ ] ✅ `CM_PROVISIONING_PROFILE` = Base64 из `profile_base64.txt` (в группе "1")
- [ ] ✅ `CM_CERTIFICATE_PASSWORD` = `12345` (в группе "1", если нужен)
- [ ] ✅ `codemagic.yaml` в корне репозитория
- [ ] ✅ В `codemagic.yaml` указана группа `"1"`
- [ ] ✅ Приложение `ru.prirodaspa.app` создано в App Store Connect
- [ ] ✅ API ключ `BR88FM6FGQ` активен и имеет роль App Manager/Admin

---

## 🔗 Полезные ссылки

- **Codemagic**: https://codemagic.io
- **App Store Connect**: https://appstoreconnect.apple.com
- **API Keys**: https://appstoreconnect.apple.com/access/api
- **My Apps**: https://appstoreconnect.apple.com/apps

---

## 📞 Если что-то не работает

1. **Проверьте логи Codemagic** — там будут детальные ошибки
2. **Проверьте переменные** — убедитесь, что все в группе **"1"**
3. **Проверьте API ключ** — в App Store Connect → Users and Access → Keys
4. **Проверьте приложение** — должно быть создано в App Store Connect

---

**Готово!** Теперь у вас есть точная инструкция для настройки Codemagic! 🎉
