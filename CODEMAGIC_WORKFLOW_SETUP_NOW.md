# 🚀 Настройка Workflow в Codemagic - Пошаговая инструкция

## 📋 Что нужно перед началом

- [x] ✅ Сертификат загружен: "Priroda Spa Distribution Certificate"
- [ ] ⬜ Provisioning Profile загружен (если нет - загрузите сейчас)
- [ ] ⬜ Интеграция "Priroda Spa" создана (если нет - создайте сейчас)

---

## 🎯 Шаг 1: Откройте настройки Workflows

1. Войдите в [Codemagic](https://codemagic.io)
2. Откройте ваш проект **"SpaApp"**
3. Перейдите: **Settings** (вверху справа) → **Workflows**
4. Нажмите **"Add workflow"** или **"Create workflow"**

---

## 🎯 Шаг 2: Выберите тип проекта

1. Выберите тип: **"Flutter"** или **"iOS"**
2. Рекомендую: **"Flutter"** (так как у вас Flutter проект)

---

## 🎯 Шаг 3: Настройте базовые параметры

### 3.1. Основные настройки

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
120
```
(минут)

**Working directory:**
```
spa
```

---

## 🎯 Шаг 4: Настройте Environment

### 4.1. Flutter и Xcode

**Flutter version:**
- Выберите: **"stable"** или **"Latest stable"**

**Xcode version:**
- Выберите: **"latest"** или **"Latest"**

### 4.2. Environment variables

**Если есть группа переменных:**
- Можно добавить группу (например, "1")
- Но при Manual Code Signing через UI переменные не обязательны

---

## 🎯 Шаг 5: Настройте iOS Code Signing

### 5.1. Включите Manual Code Signing

1. Найдите раздел **"iOS code signing"** или **"Code signing"**
2. Включите переключатель **"Manual code signing"** или выберите **"Manual"**

### 5.2. Выберите сертификаты

**Certificate:**
- Выберите из списка: **"Priroda Spa Distribution Certificate"**
- (Должен быть в списке, если вы его загрузили)

**Provisioning Profile:**
- Выберите из списка: **"Priroda Spa App Store Profile"**
- Если его нет в списке → загрузите сейчас:
  1. Teams → Personal Account → Code Signing Identities
  2. Вкладка "iOS provisioning profiles"
  3. Загрузите: `ios_certs_2026\profile.mobileprovision`

**Bundle identifier:**
```
ru.prirodaspa.app
```

**Distribution type:**
- Выберите: **"App Store"**

---

## 🎯 Шаг 6: Настройте Build Scripts

### 6.1. Добавьте скрипты (если UI позволяет)

**Script 1: Get Flutter packages**
```bash
flutter packages pub get
```

**Script 2: Install CocoaPods**
```bash
cd ios
pod install
cd ..
```

**Script 3: Build IPA**
```bash
flutter build ipa --release
```

**Примечание:** В некоторых UI версиях Codemagic эти скрипты могут быть предустановлены. Проверьте, что они есть.

---

## 🎯 Шаг 7: Настройте Publishing

### 7.1. App Store Connect

1. Найдите раздел **"Publishing"** или **"Distribution"**
2. Включите **"App Store Connect"**

**Integration:**
- Выберите из списка: **"Priroda Spa"**
- Если его нет → создайте сейчас:
  1. Teams → Personal Account → Integrations
  2. Add integration → App Store Connect
  3. Name: `Priroda Spa`
  4. Key ID: `BR88FM6FGQ`
  5. Issuer ID: (из App Store Connect)
  6. Private Key: (содержимое `AuthKey_BR88FM6FGQ.p8`)

**Submit to TestFlight:**
- Включите переключатель ✅

### 7.2. Email notifications

**Recipients:**
```
farm49595@gmail.com
```

**Notify on:**
- ✅ Success
- ✅ Failure (опционально)

---

## 🎯 Шаг 8: Сохраните Workflow

1. Нажмите **"Save"** или **"Create workflow"**
2. Workflow появится в списке с названием **"iOS Release"**

---

## 🎯 Шаг 9: Запустите сборку

1. Вернитесь на главную страницу проекта
2. Нажмите **"Start new build"**
3. Выберите workflow: **"iOS Release"** (ваш новый UI workflow)
4. Выберите ветку: **"master"**
5. Нажмите **"Start build"**

---

## ✅ Проверка перед запуском

Перед запуском убедитесь:

- [ ] ✅ Workflow создан: "iOS Release"
- [ ] ✅ Сертификат выбран: "Priroda Spa Distribution Certificate"
- [ ] ✅ Provisioning Profile выбран: "Priroda Spa App Store Profile"
- [ ] ✅ Bundle ID: `ru.prirodaspa.app`
- [ ] ✅ Интеграция выбрана: "Priroda Spa"
- [ ] ✅ Submit to TestFlight включен
- [ ] ✅ Email указан: `farm49595@gmail.com`

---

## 🆘 Если что-то не работает

### Ошибка: "Certificate not found"
- **Решение:** Убедитесь, что сертификат загружен в Teams → Personal Account → Code Signing Identities

### Ошибка: "Provisioning Profile not found"
- **Решение:** Загрузите профиль в Teams → Personal Account → Code Signing Identities → iOS provisioning profiles

### Ошибка: "Integration not found"
- **Решение:** Создайте интеграцию "Priroda Spa" в Teams → Personal Account → Integrations

### Ошибка: "Bundle identifier mismatch"
- **Решение:** Проверьте, что Bundle ID везде одинаковый: `ru.prirodaspa.app`

---

## 📝 Альтернатива: Использовать YAML workflow

Если UI workflow не работает, используйте уже настроенный YAML workflow:

1. Убедитесь, что `codemagic.yaml` в корне репозитория
2. При запуске выберите workflow: **"iOS Release"** (из YAML)
3. НЕ выбирайте "Default Workflow"

---

## 🎯 Итог

После настройки UI workflow:

1. ✅ Workflow создан и сохранен
2. ✅ Все параметры настроены
3. ✅ Запустите сборку
4. ✅ IPA автоматически загрузится в TestFlight

**Готово! 🚀**
