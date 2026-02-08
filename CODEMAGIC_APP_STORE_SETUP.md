# 🚀 Настройка Codemagic для загрузки в App Store Connect

## ✅ Текущие данные (обновлено 2026-02-06)

### API ключ App Store Connect:
- **Key ID**: `2N2LSDXR7U`
- **Issuer ID**: `4fbfcedf-2756-4b8e-8fc3-b17978e9532a`
- **Файл**: `ios_certs_2026/AuthKey_2N2LSDXR7U.p8`
- **Доступ**: Администратор ✅

### Bundle ID:
- **Bundle ID**: `ru.prirodaspa.app`
- **Приложение**: Создано в App Store Connect ✅

---

## 📋 ШАГ 1: Настройка переменных в Codemagic

### Открой Codemagic:
1. Зайди на https://codemagic.io
2. Выбери проект **Spa**
3. Перейди: **Settings** → **Environment variables**
4. Убедись, что группа **"1"** существует (или создай её)

### Добавь/Обнови 3 переменные в группе "1":

#### 1. `APP_STORE_KEY_ID`
```
2N2LSDXR7U
```

#### 2. `APP_STORE_ISSUER_ID`
```
4fbfcedf-2756-4b8e-8fc3-b17978e9532a
```

#### 3. `APP_STORE_PRIVATE_KEY`
```
LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JR1RBZ0VBTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEJIa3dkd0lCQVFRZ2c3cE1mU1gwbjBVNlpZWU0KalB5VkdZWUpnVW9TY3lXeVVyVzc4SDAwb0JXZ0NnWUlLb1pJemowREFRZWhSQU5DQUFTRE9yOFZ3M3JhUnZBdgo2WWc0UkFDUW5yQ1hPc25xdVFyaSttYmhqcXBHMlFwYUkwb25YRmw3Qk83VjBEbG9wcTYweGVMQ1paWTRqVzJtCmVWcFRwWUpSCi0tLS0tRU5EIFBSSVZBVEUgS0VZLS0tLS0=
```

**⚠️ ВАЖНО:**
- Вставляй Base64 **одной строкой** (без переносов)
- Не добавляй кавычки
- Не добавляй пробелы в начале/конце

---

## 📋 ШАГ 2: Проверка сертификатов

### Убедись, что в группе "1" также есть:

#### `CM_CERTIFICATE`
- Base64-кодированный `.p12` сертификат
- Пароль: `12345` (указан в `codemagic.yaml`)

#### `CM_PROVISIONING_PROFILE`
- Base64-кодированный `.mobileprovision` профиль
- Должен быть для Bundle ID: `ru.prirodaspa.app`
- Тип: **App Store**

---

## 📋 ШАГ 3: Запуск билда

1. В Codemagic перейди в **Builds**
2. Выбери workflow: **iOS Manual Signing 2026**
3. Нажми **Start new build**
4. Выбери ветку: **master** (или нужную)

---

## 🔍 ШАГ 4: Проверка логов

### Что должно быть в логах:

#### ✅ Успешная загрузка:
```
✅ API key file found
✅ API key file format looks correct
📦 Bundle ID: ru.prirodaspa.app
🔑 Key ID: 2N2LSDXR7U
🏢 Issuer ID: 4fbfcedf-2756-4b8e-8fc3-b17978e9532a
...
✅ Upload successful!
```

#### ❌ Если ошибка CryptoKit:
```
ERROR: [altool] Auth context delegate failed to get headers. CryptoKit.CryptoKitError.underlyingCoreCryptoError(error: -7)
```

**Решение:**
1. Проверь, что `APP_STORE_KEY_ID` = `2N2LSDXR7U`
2. Проверь, что `APP_STORE_PRIVATE_KEY` - это **точная** Base64 строка из шага 1.3
3. Проверь, что ключ активен в App Store Connect: https://appstoreconnect.apple.com → Users and Access → Keys → API App Store Connect

#### ❌ Если ошибка "Failed to determine Apple ID":
```
ERROR: Failed to determine the Apple ID from Bundle ID 'ru.prirodaspa.app'
```

**Решение:**
1. Убедись, что приложение создано в App Store Connect:
   - https://appstoreconnect.apple.com → My Apps
   - Должно быть приложение с Bundle ID `ru.prirodaspa.app`
2. Если нет - создай его:
   - Нажми "+" → "New App"
   - Bundle ID: выбери `ru.prirodaspa.app` из списка
   - Заполни остальные поля и создай

---

## 📝 Чеклист перед билдом

- [ ] `APP_STORE_KEY_ID` = `2N2LSDXR7U`
- [ ] `APP_STORE_ISSUER_ID` = `4fbfcedf-2756-4b8e-8fc3-b17978e9532a`
- [ ] `APP_STORE_PRIVATE_KEY` = Base64 строка (одной строкой, без пробелов)
- [ ] `CM_CERTIFICATE` = Base64 `.p12` файла
- [ ] `CM_PROVISIONING_PROFILE` = Base64 `.mobileprovision` файла
- [ ] Приложение `ru.prirodaspa.app` существует в App Store Connect
- [ ] API ключ `2N2LSDXR7U` активен в App Store Connect

---

## 🔗 Полезные ссылки

- **App Store Connect**: https://appstoreconnect.apple.com
- **API Keys**: https://appstoreconnect.apple.com/access/api
- **My Apps**: https://appstoreconnect.apple.com/apps
- **Codemagic**: https://codemagic.io

---

## 📞 Если что-то не работает

1. **Проверь логи Codemagic** - там будут детальные ошибки
2. **Проверь переменные** - убедись, что все 3 переменные установлены в группе "1"
3. **Проверь API ключ** - зайди в App Store Connect и убедись, что ключ активен
4. **Проверь приложение** - убедись, что оно создано в App Store Connect

---

**Последнее обновление**: 2026-02-06  
**Key ID**: `2N2LSDXR7U`  
**Status**: ✅ Готов к использованию
