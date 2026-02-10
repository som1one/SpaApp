# 🔧 Настройка интеграции App Store Connect в Codemagic

## ⚠️ Важно!

Codemagic требует `auth: integration`, но для этого нужно **настроить интеграцию в UI Codemagic**.

---

## 📋 ШАГ 1: Настройка интеграции в Codemagic UI

### 1.1. Откройте настройки интеграций

1. В Codemagic перейдите: **Settings** → **Integrations**
2. Найдите **App Store Connect**
3. Нажмите **"Add integration"** или **"Connect"**

### 1.2. Настройте интеграцию

1. **Название:** `App Store Connect` (или любое)
2. **Тип:** App Store Connect API
3. **Key ID:** `BR88FM6FGQ`
4. **Issuer ID:** `4fbfcedf-2756-4b8e-8fc3-b17978e9532a`
5. **Private Key:** 
   - Загрузите файл `AuthKey_BR88FM6FGQ.p8`
   - Или вставьте содержимое файла (весь текст с BEGIN/END)

6. Нажмите **"Save"** или **"Connect"**

---

## 📋 ШАГ 2: Обновите codemagic.yaml

После настройки интеграции в UI, `codemagic.yaml` должен использовать:

```yaml
publishing:
  app_store_connect:
    auth: integration
    submit_to_testflight: true
```

**Важно:** Не указывайте `api_key` в YAML, если используете `auth: integration` — Codemagic возьмет данные из настроенной интеграции.

---

## 🔄 Альтернатива: Использовать только переменные (без интеграции)

Если не хотите настраивать интеграцию в UI, можно использовать другой подход:

### Вариант 1: Убрать publishing (только сборка)

```yaml
publishing:
  # Убираем app_store_connect, загружаем IPA вручную
```

### Вариант 2: Использовать скрипт для загрузки

Добавить скрипт, который загрузит IPA через `xcrun altool` или API.

---

## ✅ Рекомендация

**Настройте интеграцию в UI Codemagic** — это самый простой и надежный способ.

После настройки интеграции:
1. `codemagic.yaml` будет использовать `auth: integration`
2. Codemagic автоматически возьмет данные из интеграции
3. IPA будет автоматически загружен в App Store Connect

---

## 📝 Чеклист

- [ ] ✅ Интеграция App Store Connect создана в Codemagic UI
- [ ] ✅ Key ID: `BR88FM6FGQ` указан в интеграции
- [ ] ✅ Issuer ID: `4fbfcedf-2756-4b8e-8fc3-b17978e9532a` указан
- [ ] ✅ Private Key загружен в интеграцию
- [ ] ✅ `codemagic.yaml` использует `auth: integration`
- [ ] ✅ Переменные в группе "1" настроены (для сертификатов)

---

**Готово!** После настройки интеграции в UI, билд должен работать! 🎉
