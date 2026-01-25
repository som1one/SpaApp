# 🚀 Сборка iOS приложения без Xcode и загрузка в App Store

## ✅ Да, это возможно!

Вы можете собрать iOS приложение и загрузить его в App Store **без использования Xcode на вашем компьютере**.

---

## 🎯 Способ 1: Codemagic (УЖЕ НАСТРОЕН В ПРОЕКТЕ)

Codemagic — это CI/CD сервис, который собирает iOS приложения на своих Mac серверах.

### Что уже готово:

✅ Файл `codemagic.yaml` настроен  
✅ Bundle ID: `ru.prirodaspa.app`  
✅ Конфигурация для автоматической подписи

### Что нужно сделать:

#### Шаг 1: Создайте API ключ в App Store Connect

1. Откройте: https://appstoreconnect.apple.com
2. Перейдите: **Users and Access** → **Keys** → **App Store Connect API**
3. Нажмите **"+"** (создать новый ключ)
4. **Имя:** `Codemagic iOS Signing`
5. **Access:** App Manager или Admin
6. Нажмите **Generate**
7. **Скачайте файл `.p8`** (можно скачать только один раз!)
8. **Запишите:**
   - **Key ID** (10 символов)
   - **Issuer ID** (UUID)

#### Шаг 2: Настройте Codemagic

1. Откройте: https://codemagic.io
2. Войдите или зарегистрируйтесь
3. Подключите ваш GitHub репозиторий
4. Выберите проект

#### Шаг 3: Добавьте переменные окружения

1. В Codemagic: **Settings** → **Environment variables**
2. Создайте группу: `app_store_credentials`
3. Добавьте переменные:

   **APP_STORE_ISSUER_ID:**
   - Value: ваш Issuer ID (UUID)

   **APP_STORE_KEY_ID:**
   - Value: ваш Key ID (10 символов)

   **APP_STORE_PRIVATE_KEY:**
   - Value: содержимое файла `.p8` (весь текст с BEGIN/END)

#### Шаг 4: Запустите сборку

1. В Codemagic нажмите **"Start new build"**
2. Выберите workflow: `ios-release`
3. Выберите ветку (обычно `main` или `master`)
4. Нажмите **"Start build"**

#### Шаг 5: Codemagic автоматически:

- ✅ Соберет приложение на Mac сервере
- ✅ Создаст сертификат подписи
- ✅ Создаст provisioning profile
- ✅ Подпишет приложение
- ✅ Соберет IPA файл
- ✅ Загрузит в App Store Connect (если настроено)

#### Шаг 6: Получите IPA

После успешной сборки:
1. IPA файл будет в разделе **Artifacts**
2. Скачайте файл
3. Или загрузите в App Store Connect вручную

---

## 📤 Автоматическая загрузка в App Store Connect

Чтобы Codemagic автоматически загружал IPA в App Store Connect, добавьте в `codemagic.yaml`:

```yaml
publishing:
  app_store_connect:
    auth: integration
    
    # Опционально: автоматическая загрузка
    submit_to_testflight: false  # или true, если нужно
    submit_to_app_store: false   # или true, если нужно
```

Но для этого нужны дополнительные настройки в App Store Connect.

---

## 🔄 Способ 2: GitHub Actions с Mac Runner

Можно настроить GitHub Actions, но нужен Mac runner (платный).

### Пример workflow:

```yaml
name: iOS Build

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: 'stable'
      - run: |
          cd spa
          flutter pub get
          cd ios && pod install && cd ..
          flutter build ipa --release
      - uses: actions/upload-artifact@v3
        with:
          name: ipa
          path: spa/build/ios/ipa/*.ipa
```

---

## 🎯 Способ 3: Другие CI/CD сервисы

- **Bitrise** — есть бесплатный план
- **AppCircle** — бесплатный план
- **GitLab CI** — если используете GitLab
- **CircleCI** — с Mac runner

---

## ✅ Преимущества Codemagic:

1. ✅ **Уже настроен** в вашем проекте
2. ✅ **Бесплатный план** — 500 минут сборки в месяц
3. ✅ **Автоматическая подпись** через App Store Connect API
4. ✅ **Не нужен Mac** — всё на серверах Codemagic
5. ✅ **Простая настройка** — только переменные окружения

---

## 📋 Что нужно для Codemagic:

- [ ] Аккаунт в Codemagic (бесплатно)
- [ ] API ключ App Store Connect (бесплатно)
- [ ] GitHub репозиторий с проектом
- [ ] Переменные окружения в Codemagic (5 минут настройки)

---

## 🚀 Быстрый старт с Codemagic:

1. **Создайте API ключ** в App Store Connect (5 минут)
2. **Зарегистрируйтесь** в Codemagic (2 минуты)
3. **Подключите репозиторий** (1 минута)
4. **Добавьте переменные** (3 минуты)
5. **Запустите сборку** (1 минута)

**Итого: ~12 минут настройки, дальше всё автоматически!**

---

## 📚 Подробная инструкция:

См. файл: `CODEMAGIC_IOS_SIGNING_GUIDE.md`

Там есть:
- Пошаговая настройка App Store Connect API
- Настройка переменных в Codemagic
- Решение проблем
- Автоматизация через скрипт

---

## 💡 Рекомендация:

**Используйте Codemagic** — это самый простой способ собрать iOS приложение без Mac и загрузить в App Store.

Ваш проект уже настроен, нужно только:
1. Создать API ключ
2. Добавить переменные в Codemagic
3. Запустить сборку

**Всё!** 🎉

---

## ❓ FAQ

**Q: Нужен ли Mac для Codemagic?**  
A: Нет! Codemagic использует свои Mac серверы.

**Q: Сколько стоит Codemagic?**  
A: Есть бесплатный план — 500 минут сборки в месяц (обычно хватает).

**Q: Можно ли загрузить IPA вручную?**  
A: Да! После сборки скачайте IPA из Artifacts и загрузите через Transporter или Xcode.

**Q: Нужен ли Apple Developer аккаунт?**  
A: Да, нужен платный аккаунт ($99/год) для публикации в App Store.

---

**Готово! Теперь вы можете собирать iOS приложение без Xcode!** ✅
