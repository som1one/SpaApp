# ✅ Финальная настройка Codemagic

## 🎯 Правильное решение

Добавлена секция `integrations` в `codemagic.yaml`:

```yaml
integrations:
  app_store_connect: appstore  # Имя интеграции из Codemagic UI
```

---

## 📋 ШАГ 1: Проверьте имя интеграции в Codemagic

1. Откройте **Codemagic** → **Settings** → **Integrations**
2. Найдите **App Store Connect** интеграцию
3. **Проверьте имя** интеграции (обычно `appstore` или как вы назвали)
4. Если имя другое — обновите в `codemagic.yaml` строку 9:
   ```yaml
   app_store_connect: ваше_имя_интеграции
   ```

---

## 📋 ШАГ 2: Настройте интеграцию (если еще не настроена)

1. **Settings** → **Integrations** → **App Store Connect**
2. Нажмите **"Add integration"** или **"Connect"**
3. Заполните:
   - **Key ID:** `BR88FM6FGQ`
   - **Issuer ID:** `4fbfcedf-2756-4b8e-8fc3-b17978e9532a`
   - **Private Key:** 
     - Загрузите файл `ios_certs_2026/AuthKey_BR88FM6FGQ.p8`
     - Или вставьте содержимое файла (весь текст с BEGIN/END)
4. **Название интеграции:** `appstore` (или любое другое, но тогда обновите в YAML)
5. Нажмите **"Save"**

---

## 📋 ШАГ 3: Переменные для сертификатов (группа "1")

Эти переменные все еще нужны для ручной подписи:

- `CM_CERTIFICATE` — Base64 из `certificate_base64.txt`
- `CM_PROVISIONING_PROFILE` — Base64 из `profile_base64.txt`
- `CM_CERTIFICATE_PASSWORD` — `12345`

**Примечание:** Переменные `APP_STORE_KEY_ID`, `APP_STORE_ISSUER_ID`, `APP_STORE_PRIVATE_KEY` больше **НЕ нужны** — данные берутся из интеграции.

---

## ✅ Что должно работать

После настройки:

- ✅ Ошибка валидации исчезнет
- ✅ Workflow станет кликабельным
- ✅ Сборка пойдет
- ✅ Загрузка в TestFlight заработает автоматически

---

## 🔍 Проверка

1. Обновите страницу в Codemagic (F5)
2. Нажмите кнопку обновления рядом с "Select file workflow"
3. Ошибка должна исчезнуть
4. Кнопка "Start new build" должна стать активной

---

**Готово!** Теперь все должно работать! 🎉
