# 🔐 Скрипты для проверки и подготовки сертификатов

## 📋 Доступные скрипты

### 1. `test_api_key.py` - Проверка API ключа

Проверяет валидность `.p8` файла App Store Connect API ключа.

```bash
python test_api_key.py
```

**Что проверяет:**
- ✅ Формат PEM ключа
- ✅ Base64 декодирование
- ✅ Извлечение Key ID из имени файла
- ✅ Проверка Base64 закодированных ключей

---

### 2. `test_certificates.py` - Проверка сертификатов

Проверяет валидность `.p12` сертификатов и `.mobileprovision` профилей.

```bash
python test_certificates.py
```

**С паролем:**
```bash
python test_certificates.py --password YOUR_PASSWORD
```

**Что проверяет:**
- ✅ Формат PKCS12 сертификата
- ✅ Bundle ID в provisioning profile
- ✅ Тип профиля (App Store / Development)
- ✅ Срок действия профиля
- ✅ Base64 кодирование

---

### 3. `encode_certificates.py` - Кодирование в Base64

Кодирует сертификаты и профили в Base64 для использования в Codemagic.

```bash
python encode_certificates.py
```

**Результат:**
- Создает `*_base64.txt` файлы
- Готовые для копирования в Codemagic Environment Variables

---

### 4. `encode_key.py` - Кодирование API ключа

Кодирует `.p8` файл в Base64 для Codemagic.

```bash
python encode_key.py
```

**Результат:**
- Создает `key_base64.txt` файл
- Готов для копирования в `APP_STORE_PRIVATE_KEY`

---

## 🚀 Быстрый старт

### Шаг 1: Проверьте API ключ

```bash
cd ios_certs_2026
python test_api_key.py
```

### Шаг 2: Проверьте сертификаты

```bash
python test_certificates.py
```

### Шаг 3: Закодируйте файлы для Codemagic

```bash
python encode_certificates.py
python encode_key.py
```

### Шаг 4: Скопируйте значения в Codemagic

1. Откройте `*_base64.txt` файлы
2. Скопируйте содержимое (одной строкой)
3. Вставьте в Codemagic Environment Variables:
   - `CM_CERTIFICATE` - из `.p12_base64.txt`
   - `CM_PROVISIONING_PROFILE` - из `.mobileprovision_base64.txt`
   - `APP_STORE_PRIVATE_KEY` - из `key_base64.txt`

---

## 📝 Требуемые переменные в Codemagic

### Группа "1":

1. **`APP_STORE_KEY_ID`**
   - Key ID из имени файла (например: `2N2LSDXR7U`)

2. **`APP_STORE_ISSUER_ID`**
   - Issuer ID из App Store Connect (например: `4fbfcedf-2756-4b8e-8fc3-b17978e9532a`)

3. **`APP_STORE_PRIVATE_KEY`**
   - Base64 закодированный `.p8` файл (из `key_base64.txt`)

4. **`CM_CERTIFICATE`**
   - Base64 закодированный `.p12` файл (из `*_base64.txt`)

5. **`CM_PROVISIONING_PROFILE`**
   - Base64 закодированный `.mobileprovision` файл (из `*_base64.txt`)

6. **`CM_CERTIFICATE_PASSWORD`** (опционально)
   - Пароль от `.p12` файла (по умолчанию: `12345`)

---

## 🔍 Troubleshooting

### Ошибка: "File not found"

**Решение:** Убедитесь, что файлы находятся в той же директории, что и скрипты.

### Ошибка: "Invalid PEM format"

**Решение:** Проверьте, что `.p8` файл начинается с `-----BEGIN PRIVATE KEY-----`

### Ошибка: "Profile expired"

**Решение:** Создайте новый provisioning profile в Apple Developer Portal.

### Ошибка: "Certificate expired"

**Решение:** Создайте новый Distribution Certificate в Apple Developer Portal.

---

## 📚 Полезные ссылки

- [Codemagic Documentation](https://docs.codemagic.io)
- [App Store Connect API](https://developer.apple.com/documentation/appstoreconnectapi)
- [Apple Developer Portal](https://developer.apple.com/account)
