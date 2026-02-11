# 🔧 Исправление: "No valid code signing certificates were found"

## ❌ Проблема

```
No valid code signing certificates were found
No development certificates available to code sign app for device deployment
```

**Причина:** Codemagic не может найти сертификаты, даже если они загружены в UI.

---

## ✅ Решение

### Вариант 1: Исправить YAML workflow (рекомендуется)

Проблема в том, что команда `xcode-project use-profiles` должна выполняться **ПЕРЕД** сборкой, но сертификаты должны быть импортированы в keychain.

Обновите `codemagic.yaml`:

```yaml
workflows:
  ios-release:
    name: iOS Release
    instance_type: mac_mini_m2
    max_build_duration: 120
    working_directory: spa
    integrations:
      app_store_connect: Priroda Spa
    environment:
      flutter: stable
      xcode: latest
    ios_signing:
      distribution_type: app_store
      bundle_identifier: ru.prirodaspa.app

    scripts:
      - name: Get Flutter packages
        script: |
          flutter packages pub get
      
      - name: Install pods
        script: |
          cd ios
          pod install
          cd ..
      
      - name: Set up code signing settings on Xcode project
        script: |
          xcode-project use-profiles
      
      - name: Verify code signing setup
        script: |
          echo "🔍 Проверка сертификатов..."
          security find-identity -v -p codesigning || true
          echo ""
          echo "🔍 Проверка provisioning profiles..."
          ls -la ~/Library/MobileDevice/Provisioning\ Profiles/ || true
      
      - name: Versioning
        script: |
          cd ./ios
          agvtool new-version -all $(($BUILD_NUMBER))
          agvtool new-marketing-version 1.0.$(($BUILD_NUMBER))
      
      - name: Flutter build IPA
        script: |
          flutter build ipa --release

    artifacts:
      - build/ios/ipa/*.ipa

    publishing:
      email:
        recipients:
          - farm49595@gmail.com
        notify:
          success: true
          failure: false
      app_store_connect:
        auth: integration
        submit_to_testflight: true
```

---

### Вариант 2: Проверить настройки в UI

Если используете UI workflow:

1. **Проверьте Code Signing:**
   - Settings → Workflows → ваш workflow
   - Раздел "iOS code signing"
   - Должно быть: **"Manual code signing"** (НЕ Automatic)
   - Certificate: "Priroda Spa Distribution Certificate"
   - Provisioning Profile: "Priroda Spa App Store Profile"

2. **Проверьте, что сертификаты загружены:**
   - Teams → Personal Account → Code Signing Identities
   - iOS certificates: должен быть "Priroda Spa Distribution Certificate"
   - iOS provisioning profiles: должен быть профиль с Bundle ID `ru.prirodaspa.app`

---

## 🔍 Диагностика

### Проверка 1: Загружены ли сертификаты?

1. Codemagic → Teams → Personal Account → Code Signing Identities
2. Проверьте:
   - ✅ iOS certificates: "Priroda Spa Distribution Certificate" (Expires: February 01, 2027)
   - ✅ iOS provisioning profiles: профиль с Bundle ID `ru.prirodaspa.app`

### Проверка 2: Правильный ли workflow?

При запуске сборки:
- ✅ Выберите workflow: **"iOS Release"** (из YAML)
- ❌ НЕ выбирайте "Default Workflow"

### Проверка 3: Правильно ли настроен ios_signing?

В `codemagic.yaml` должно быть:
```yaml
ios_signing:
  distribution_type: app_store
  bundle_identifier: ru.prirodaspa.app
```

Это говорит Codemagic использовать Manual Code Signing с сертификатами из UI.

---

## 🛠️ Пошаговое исправление

### Шаг 1: Убедитесь, что Provisioning Profile загружен

1. Codemagic → Teams → Personal Account → Code Signing Identities
2. Вкладка "iOS provisioning profiles"
3. Если профиля нет → загрузите:
   - Файл: `ios_certs_2026\profile.mobileprovision`
   - Reference name: `Priroda Spa App Store Profile`
   - Bundle ID должен быть: `ru.prirodaspa.app`

### Шаг 2: Обновите codemagic.yaml

Добавьте скрипт проверки сертификатов (как в варианте 1 выше).

### Шаг 3: Запушьте изменения

```bash
git add codemagic.yaml
git commit -m "Fix: add certificate verification script"
git push origin master
```

### Шаг 4: Запустите сборку заново

1. Codemagic → ваш проект
2. "Start new build"
3. Выберите workflow: **"iOS Release"**
4. Ветка: `master`
5. "Start build"

---

## 🆘 Если все еще не работает

### Ошибка: "Certificate not found" после исправлений

**Решение:**
1. Удалите сертификат из Codemagic UI
2. Загрузите заново: `ios_certs_2026\certificate.p12`
3. Пароль: `12345`
4. Запустите сборку снова

### Ошибка: "Provisioning Profile not found"

**Решение:**
1. Проверьте Bundle ID в профиле:
   ```bash
   # На Windows можно открыть .mobileprovision в текстовом редакторе
   # Или используйте Python скрипт:
   cd ios_certs_2026
   python test_certificates.py
   ```
2. Убедитесь, что Bundle ID = `ru.prirodaspa.app`
3. Если Bundle ID другой → создайте новый профиль в Apple Developer Portal

### Ошибка: "Bundle identifier mismatch"

**Решение:**
Проверьте Bundle ID везде:
- ✅ `codemagic.yaml`: `ru.prirodaspa.app`
- ✅ Provisioning Profile: `ru.prirodaspa.app`
- ✅ Xcode проекте: `ru.prirodaspa.app`
- ✅ App Store Connect: `ru.prirodaspa.app`

---

## 📝 Чеклист перед следующей сборкой

- [ ] ✅ Сертификат загружен: "Priroda Spa Distribution Certificate"
- [ ] ✅ Provisioning Profile загружен (Bundle ID: `ru.prirodaspa.app`)
- [ ] ✅ Интеграция "Priroda Spa" создана
- [ ] ✅ `codemagic.yaml` обновлен (добавлен скрипт проверки)
- [ ] ✅ Изменения запушены в Git
- [ ] ✅ Выбрать workflow "iOS Release" (НЕ "Default Workflow")

---

## 🎯 Итог

**Главная проблема:** Codemagic не импортирует сертификаты из UI автоматически при использовании `ios_signing`.

**Решение:** 
1. Убедитесь, что Provisioning Profile загружен
2. Добавьте скрипт проверки сертификатов в `codemagic.yaml`
3. Используйте правильный workflow при запуске

**После исправлений:** IPA должен собираться успешно! 🚀
