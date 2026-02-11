# 🎨 Настройка Workflow через UI Codemagic

## ✅ Да, можно настроить через UI!

В Codemagic можно создать workflow двумя способами:
1. **Через `codemagic.yaml`** (уже настроено)
2. **Через UI** (визуальный редактор)

---

## 📋 Настройка через UI

### Шаг 1: Создайте новый workflow в UI

1. В Codemagic откройте ваш проект
2. Перейдите: **Settings** → **Workflows**
3. Нажмите **"Add workflow"** или **"Create workflow"**
4. Выберите тип: **"iOS"** или **"Flutter"**

### Шаг 2: Настройте базовые параметры

**Workflow name:**
```
iOS Release
```

**Instance type:**
```
Mac mini M2
```

**Max build duration:**
```
120 minutes
```

**Working directory:**
```
spa
```

---

### Шаг 3: Настройте Environment

**Flutter version:**
```
stable
```

**Xcode version:**
```
latest
```

**Environment variables:**
- Если используете переменные, добавьте их здесь
- Но при Manual Code Signing через UI переменные не нужны

---

### Шаг 4: Настройте iOS Code Signing

1. Найдите раздел **"iOS code signing"** или **"Code signing"**
2. Включите **"Manual code signing"**
3. Выберите:
   - **Certificate:** "Priroda Spa Distribution Certificate" (из загруженных)
   - **Provisioning Profile:** "Priroda Spa App Store Profile" (из загруженных)
   - **Bundle identifier:** `ru.prirodaspa.app`

**Или используйте автоматическую настройку:**
- Включите **"Automatic code signing"**
- Codemagic автоматически использует сертификаты из UI

---

### Шаг 5: Настройте Build scripts

Добавьте скрипты (если UI позволяет):

1. **Get Flutter packages:**
   ```bash
   flutter packages pub get
   ```

2. **Install pods:**
   ```bash
   cd ios
   pod install
   cd ..
   ```

3. **Build IPA:**
   ```bash
   flutter build ipa --release
   ```

**Примечание:** В UI может быть упрощенный вариант - просто выберите "Build iOS app" или "Build IPA".

---

### Шаг 6: Настройте Publishing

1. Найдите раздел **"Publishing"** или **"Distribution"**
2. Включите **"App Store Connect"**
3. Выберите интеграцию: **"Priroda Spa"**
4. Включите **"Submit to TestFlight"**

**Email notifications:**
- Включите уведомления
- Email: `farm49595@gmail.com`

---

### Шаг 7: Сохраните workflow

1. Нажмите **"Save"** или **"Create workflow"**
2. Workflow появится в списке

---

## 🔄 Сравнение: UI vs YAML

### Преимущества UI:
- ✅ Визуальный редактор - проще для новичков
- ✅ Не нужно знать YAML синтаксис
- ✅ Меньше ошибок в синтаксисе
- ✅ Легче менять настройки

### Преимущества YAML:
- ✅ Версионирование в Git
- ✅ Легче копировать между проектами
- ✅ Больше контроля над скриптами
- ✅ Можно использовать условную логику

---

## 💡 Рекомендация

**Для вашего случая:**

1. **Если хотите быстро запустить** → Используйте UI
   - Проще настроить
   - Меньше ошибок
   - Быстрее начать

2. **Если хотите версионирование** → Используйте YAML
   - Уже настроен `codemagic.yaml`
   - Все изменения в Git
   - Легче откатить изменения

**Можно использовать оба подхода одновременно:**
- UI workflow для быстрых тестов
- YAML workflow для production сборок

---

## 📝 Что нужно проверить в UI

Перед запуском через UI workflow:

- [ ] ✅ Сертификат загружен: "Priroda Spa Distribution Certificate"
- [ ] ✅ Provisioning Profile загружен (Bundle ID: `ru.prirodaspa.app`)
- [ ] ✅ Интеграция "Priroda Spa" создана
- [ ] ✅ Bundle ID совпадает везде: `ru.prirodaspa.app`
- [ ] ✅ Workflow настроен правильно

---

## 🚀 Запуск UI Workflow

1. Откройте проект в Codemagic
2. Выберите созданный UI workflow (например, "iOS Release UI")
3. Нажмите **"Start new build"**
4. Выберите ветку: `master`
5. Нажмите **"Start build"**

---

## ⚠️ Важно

**Если используете UI workflow:**
- Убедитесь, что выбрали правильный workflow при запуске
- Проверьте, что все настройки совпадают с YAML версией
- UI workflow может иметь ограничения по сравнению с YAML

**Если используете YAML workflow:**
- Убедитесь, что файл `codemagic.yaml` в корне репозитория
- Выберите workflow "iOS Release" при запуске
- Проверьте, что все пути правильные

---

## 🎯 Итог

**Да, можно настроить через UI!** Это даже проще для начала.

**Рекомендую:**
1. Создайте UI workflow для тестирования
2. Используйте YAML workflow для production
3. Или выберите один подход и придерживайтесь его

**Главное:** При запуске сборки выбирайте правильный workflow (UI или YAML)!
