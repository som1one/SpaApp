# 🔑 Полное руководство: Создание App Store Connect API ключей с нуля

## 📋 Содержание
1. [Введение](#введение)
2. [Шаг 1: Вход в App Store Connect](#шаг-1-вход-в-app-store-connect)
3. [Шаг 2: Создание API ключа](#шаг-2-создание-api-ключа)
4. [Шаг 3: Скачивание и сохранение ключа](#шаг-3-скачивание-и-сохранение-ключа)
5. [Шаг 4: Кодирование ключа в Base64](#шаг-4-кодирование-ключа-в-base64)
6. [Шаг 5: Настройка переменных в Codemagic](#шаг-5-настройка-переменных-в-codemagic)
7. [Шаг 6: Проверка и тестирование](#шаг-6-проверка-и-тестирование)
8. [Частые ошибки и решения](#частые-ошибки-и-решения)

---

## Введение

**Важно:** App Store Connect API ключи — это НЕ то же самое, что APNs ключи!

- ✅ **App Store Connect API** — для загрузки приложений, управления метаданными
- ❌ **APNs (Apple Push Notification service)** — только для push-уведомлений

Мы создаем ключ для **App Store Connect API**.

---

## Шаг 1: Вход в App Store Connect

1. Откройте браузер и перейдите на:
   ```
   https://appstoreconnect.apple.com
   ```

2. Войдите с вашим Apple ID (который имеет доступ к Developer Account)

3. Убедитесь, что у вас есть права **Admin** или **App Manager** в команде разработчиков

---

## Шаг 2: Создание API ключа

### 2.1. Переход в раздел Keys

1. В верхнем меню нажмите **"Users and Access"** (или **"Пользователи и доступ"**)

2. В левом меню выберите **"Keys"** (или **"Ключи"**)

3. Нажмите на вкладку **"App Store Connect API"** (НЕ "APNs Auth Key"!)

   ⚠️ **КРИТИЧЕСКИ ВАЖНО:** Должна быть выбрана именно вкладка **"App Store Connect API"**, а не "APNs Auth Key"!

### 2.2. Создание нового ключа

1. Нажмите кнопку **"+"** (плюс) в правом верхнем углу

2. Заполните форму:
   - **Name** (Имя): `Codemagic Upload Key` (или любое другое понятное имя)
   - **Access** (Доступ): Выберите **"App Manager"** или **"Admin"**
     - ⚠️ **ВАЖНО:** Минимум "App Manager", "Developer" недостаточно!

3. Нажмите **"Generate"** (или **"Создать"**)

### 2.3. Сохранение данных ключа

**⚠️ КРИТИЧЕСКИ ВАЖНО: Скачать ключ можно ТОЛЬКО ОДИН РАЗ!**

После создания ключа вы увидите:

1. **Issuer ID** (UUID формат, например: `4fbfcedf-2756-4b8e-8fc3-b17978e9532a`)
   - Скопируйте это значение и сохраните в безопасном месте
   - Это значение для переменной `APP_STORE_ISSUER_ID`

2. **Key ID** (10 символов, например: `2N2LSDXR7U`)
   - Скопируйте это значение и сохраните в безопасном месте
   - Это значение для переменной `APP_STORE_KEY_ID`

3. Кнопка **"Download API Key"** (или **"Скачать ключ API"**)
   - ⚠️ **НАЖМИТЕ СЕЙЧАС!** Вы больше не сможете скачать этот файл!
   - Файл будет называться: `AuthKey_<KEY_ID>.p8`
   - Например: `AuthKey_2N2LSDXR7U.p8`

---

## Шаг 3: Скачивание и сохранение ключа

1. Сохраните файл `.p8` в безопасное место на вашем компьютере

2. Рекомендуется сохранить в папку проекта:
   ```
   ios_certs_2026/AuthKey_<KEY_ID>.p8
   ```

3. **НЕ ДЕЛАЙТЕ:**
   - ❌ Не коммитьте файл `.p8` в Git (он уже в `.gitignore`)
   - ❌ Не отправляйте файл по email
   - ❌ Не загружайте в облако без шифрования

4. **Проверьте файл:**
   - Откройте файл в текстовом редакторе
   - Он должен начинаться с: `-----BEGIN PRIVATE KEY-----`
   - И заканчиваться: `-----END PRIVATE KEY-----`
   - Размер файла обычно около 250-300 байт

---

## Шаг 4: Кодирование ключа в Base64

### Вариант 1: Использование готового скрипта (рекомендуется)

1. Убедитесь, что файл `.p8` находится в папке `ios_certs_2026/`

2. Запустите скрипт:

   **Если в папке только один файл `.p8`:**
   ```bash
   python ios_certs_2026/encode_key.py
   ```
   Скрипт автоматически найдет файл!

   **Если в папке несколько файлов `.p8`:**
   ```bash
   python ios_certs_2026/encode_key.py AuthKey_<ВАШ_KEY_ID>.p8
   ```
   Например:
   ```bash
   python ios_certs_2026/encode_key.py AuthKey_2N2LSDXR7U.p8
   ```

3. Скрипт выведет:

   **Windows (PowerShell):**
   ```powershell
   python ios_certs_2026/encode_key.py
   ```

   **macOS/Linux:**
   ```bash
   python3 ios_certs_2026/encode_key.py
   ```

4. Скрипт выведет:
   - ✅ Key ID (извлеченный из имени файла)
   - ✅ Длину Base64 строки
   - ✅ Полную Base64 строку для копирования
   - ✅ Сохранит результат в `ios_certs_2026/key_base64.txt`

5. **Скопируйте всю Base64 строку** (она будет очень длинной, без переносов строк)
   
   Пример вывода:
   ```
   ======================================================================
   ✅ Key encoded successfully!
   ======================================================================
   
   📋 Key Information:
      • Key ID: 2N2LSDXR7U
      • Base64 length: 344 characters
      • Output file: key_base64.txt
   
   📝 Codemagic Environment Variables:
      • APP_STORE_KEY_ID = 2N2LSDXR7U
      • APP_STORE_ISSUER_ID = <Get from App Store Connect>
      • APP_STORE_PRIVATE_KEY = <Copy Base64 string below>
   
   ======================================================================
   📋 Copy this ENTIRE string (without line breaks) to APP_STORE_PRIVATE_KEY:
   ======================================================================
   LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCi4uLi (очень длинная строка)
   ======================================================================
   ```

### Вариант 2: Ручное кодирование (если нет Python)

**Windows (PowerShell):**
```powershell
$content = Get-Content -Path "ios_certs_2026/AuthKey_<KEY_ID>.p8" -Raw -Encoding UTF8
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$base64 = [Convert]::ToBase64String($bytes)
$base64
```

**macOS/Linux:**
```bash
base64 -i ios_certs_2026/AuthKey_<KEY_ID>.p8 | tr -d '\n'
```

---

## Шаг 5: Настройка переменных в Codemagic

### 5.1. Открытие настроек проекта

1. Войдите в [Codemagic](https://codemagic.io)

2. Выберите ваш проект **Spa**

3. Перейдите в **"Settings"** → **"Environment variables"**

### 5.2. Добавление переменных

Создайте **3 переменные** в группе **"1"** (или любой другой группе):

#### Переменная 1: `APP_STORE_KEY_ID`

- **Variable name:** `APP_STORE_KEY_ID`
- **Variable value:** Ваш Key ID (10 символов, например: `2N2LSDXR7U`)
- **Group:** `1`
- **Secure:** ❌ Нет (это не секрет)

#### Переменная 2: `APP_STORE_ISSUER_ID`

- **Variable name:** `APP_STORE_ISSUER_ID`
- **Variable value:** Ваш Issuer ID (UUID, например: `4fbfcedf-2756-4b8e-8fc3-b17978e9532a`)
- **Group:** `1`
- **Secure:** ❌ Нет (это не секрет)

#### Переменная 3: `APP_STORE_PRIVATE_KEY`

- **Variable name:** `APP_STORE_PRIVATE_KEY`
- **Variable value:** Вся Base64 строка из шага 4 (без переносов строк!)
- **Group:** `1`
- **Secure:** ✅ **ДА!** (это секрет)

⚠️ **ВАЖНО для `APP_STORE_PRIVATE_KEY`:**
- Вставьте ВСЮ Base64 строку целиком
- БЕЗ переносов строк
- БЕЗ пробелов в начале/конце
- Должна быть одна длинная строка (обычно ~344 символа)

### 5.3. Проверка переменных

После добавления всех трех переменных:

1. Убедитесь, что все переменные в одной группе (например, группа `1`)

2. Проверьте, что `APP_STORE_PRIVATE_KEY` помечена как **Secure**

3. Сохраните изменения

---

## Шаг 6: Проверка и тестирование

### 6.1. Запуск билда

1. В Codemagic запустите новый билд

2. В логах найдите секцию **"ENVIRONMENT VARIABLES CHECK"**

3. Проверьте вывод:
   ```
   🔑 APP_STORE_KEY_ID:
      Value: 2N2LSDXR7U
      Length: 10 characters
      Expected: 10 characters ✅
   
   🏢 APP_STORE_ISSUER_ID:
      Value: 4fbfcedf-2756-4b8e-8fc3-b17978e9532a
      Length: 36 characters
      Expected: UUID format ✅
   
   🔐 APP_STORE_PRIVATE_KEY:
      Length: 344 characters
      Expected: ~344 characters ✅
      Format: ✅ Looks like Base64
   ```

### 6.2. Проверка декодированного ключа

В логах должна быть секция **"DECODED API KEY VERIFICATION"**:

```
📋 DECODED API KEY VERIFICATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 Key file path: /Users/builder/private_keys/AuthKey_2N2LSDXR7U.p8
📏 Key file size: 258 bytes
📄 Key file lines: 4

✅ Key file format verified:
   First line: -----BEGIN PRIVATE KEY-----
   Last line:  -----END PRIVATE KEY-----

🔍 Key ID verification:
   Expected Key ID (from filename): 2N2LSDXR7U
   Environment Key ID: 2N2LSDXR7U
   Status: ✅ Match
```

### 6.3. Успешная загрузка

Если все правильно, вы увидите:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Upload successful!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏳ Processing usually takes 10-30 minutes
📱 Check App Store Connect -> TestFlight after processing
```

---

## Частые ошибки и решения

### ❌ Ошибка 401: NOT_AUTHORIZED

**Причина:**
- API ключ не имеет правильных прав доступа
- Ключ создан для APNs вместо App Store Connect API
- Ключ отозван или истек

**Решение:**
1. Проверьте в App Store Connect:
   - Users and Access → Keys → App Store Connect API
   - Найдите ваш ключ по Key ID
   - Убедитесь, что:
     - Status: **Active** (не Revoked)
     - Access: **App Manager** или **Admin** (не Developer!)
     - Service: **App Store Connect API** (не APNs!)

2. Если ключ неправильный:
   - Создайте новый ключ (см. Шаг 2)
   - Обновите все 3 переменные в Codemagic

### ❌ Ошибка: "Failed to determine the Apple ID from Bundle ID"

**Причина:**
- Приложение не создано в App Store Connect

**Решение:**
1. Откройте https://appstoreconnect.apple.com
2. My Apps → "+" → New App
3. Заполните:
   - Platform: iOS
   - Name: PRIRODA SPA
   - Primary Language: Russian
   - Bundle ID: ru.prirodaspa.app
   - SKU: prirodaspa-ios-001
4. Создайте приложение
5. Подождите 2-3 минуты
6. Запустите билд снова

### ❌ Ошибка: "Key file format incorrect"

**Причина:**
- Base64 строка неправильно закодирована
- В строке есть переносы строк или пробелы

**Решение:**
1. Убедитесь, что Base64 строка:
   - Одна длинная строка без переносов
   - Без пробелов в начале/конце
   - Начинается с букв/цифр (не с `-----BEGIN`)

2. Перекодируйте ключ заново (см. Шаг 4)

### ❌ Ошибка: "Key ID mismatch"

**Причина:**
- Key ID в имени файла не совпадает с переменной `APP_STORE_KEY_ID`

**Решение:**
1. Проверьте переменную `APP_STORE_KEY_ID` в Codemagic
2. Убедитесь, что она точно совпадает с Key ID из App Store Connect
3. Убедитесь, что файл `.p8` называется `AuthKey_<KEY_ID>.p8`

---

## 📝 Чек-лист перед запуском билда

- [ ] API ключ создан в разделе **"App Store Connect API"** (не APNs!)
- [ ] Ключ имеет доступ **"App Manager"** или **"Admin"**
- [ ] Файл `.p8` скачан и сохранен
- [ ] Key ID скопирован (10 символов)
- [ ] Issuer ID скопирован (UUID формат)
- [ ] Ключ закодирован в Base64
- [ ] Все 3 переменные добавлены в Codemagic:
  - [ ] `APP_STORE_KEY_ID` (не Secure)
  - [ ] `APP_STORE_ISSUER_ID` (не Secure)
  - [ ] `APP_STORE_PRIVATE_KEY` (Secure!)
- [ ] Все переменные в одной группе
- [ ] Приложение создано в App Store Connect (если нужно)

---

## 🔗 Полезные ссылки

- **App Store Connect:** https://appstoreconnect.apple.com
- **API Keys:** https://appstoreconnect.apple.com/access/api
- **Документация Apple:** https://developer.apple.com/documentation/appstoreconnectapi
- **Codemagic:** https://codemagic.io

---

## 💡 Советы

1. **Храните резервные копии:**
   - Сохраните файл `.p8` в безопасном месте
   - Сохраните Key ID и Issuer ID в менеджере паролей

2. **Один ключ на проект:**
   - Создайте отдельный ключ для каждого проекта
   - Не используйте один ключ для всех проектов

3. **Регулярная проверка:**
   - Периодически проверяйте статус ключа в App Store Connect
   - Убедитесь, что ключ не отозван

4. **Если ключ скомпрометирован:**
   - Немедленно отзовите его в App Store Connect
   - Создайте новый ключ
   - Обновите все переменные в Codemagic

---

**Последнее обновление:** 2026-02-08
