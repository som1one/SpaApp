# 🔍 Проблемы со сборкой в Codemagic

## ❌ Проблема

Сборка завершилась успешно, но:
- ❌ Использовался "Default Workflow" вместо "iOS Release"
- ❌ В артефактах только `Runner.app.zip`, а не `.ipa` файл
- ❌ IPA не загружен в App Store Connect

---

## ✅ Решение

### 1. Используйте правильный workflow

**При запуске сборки:**
1. Нажмите **"Start new build"**
2. Выберите workflow: **"iOS Release"** (НЕ "Default Workflow")
3. Выберите ветку: `master`
4. Нажмите **"Start build"**

### 2. Проверьте настройки перед запуском

- [ ] ✅ Сертификат загружен в Codemagic UI
- [ ] ✅ Provisioning Profile загружен в Codemagic UI
- [ ] ✅ Интеграция "Priroda Spa" создана в Codemagic UI
- [ ] ✅ Bundle ID совпадает: `ru.prirodaspa.app`

### 3. Проверьте логи сборки

Если сборка все равно не создает IPA:

1. Откройте сборку в Codemagic
2. Нажмите на шаг **"Building iOS"** или **"Flutter build IPA"**
3. Проверьте ошибки в логах

**Типичные ошибки:**
- "No valid code signing certificates" → Проверьте, что сертификат загружен
- "No provisioning profile found" → Проверьте, что профиль загружен
- "Bundle identifier mismatch" → Проверьте Bundle ID

---

## 🔧 Исправления в codemagic.yaml

### Убрал проблемный путь к export_options.plist

Изменил:
```yaml
flutter build ipa --release \
  --export-options-plist=/Users/builder/export_options.plist
```

На:
```yaml
flutter build ipa --release
```

Codemagic автоматически создаст правильный `export_options.plist` при использовании `ios_signing`.

---

## 📋 Правильный процесс запуска

1. **Загрузите Provisioning Profile** (если еще не загружен):
   - Teams → Personal Account → Code Signing Identities
   - Вкладка "iOS provisioning profiles"
   - Файл: `ios_certs_2026\profile.mobileprovision`

2. **Создайте интеграцию App Store Connect** (если еще не создана):
   - Teams → Personal Account → Integrations
   - Название: `Priroda Spa`
   - Key ID: `BR88FM6FGQ`
   - Private Key: содержимое `AuthKey_BR88FM6FGQ.p8`

3. **Запустите сборку с правильным workflow**:
   - Выберите workflow: **"iOS Release"**
   - НЕ используйте "Default Workflow"

4. **Проверьте результат**:
   - В артефактах должен быть `.ipa` файл
   - IPA должен автоматически загрузиться в TestFlight

---

## 🆘 Если IPA все равно не создается

### Проверьте логи шага "Flutter build IPA"

**Ошибка: "No valid code signing certificates"**
- Решение: Убедитесь, что сертификат загружен в Codemagic UI

**Ошибка: "No provisioning profile found"**
- Решение: Убедитесь, что профиль загружен и Bundle ID совпадает

**Ошибка: "Bundle identifier mismatch"**
- Решение: Проверьте Bundle ID в:
  - `codemagic.yaml`: `ru.prirodaspa.app`
  - Provisioning Profile: должен быть `ru.prirodaspa.app`
  - Xcode проекте: должен быть `ru.prirodaspa.app`

### Проверьте шаг "Set up code signing settings"

Если шаг `xcode-project use-profiles` завершается с ошибкой:
- Проверьте, что сертификат и профиль загружены в UI
- Проверьте, что Bundle ID совпадает

---

## 📝 Чеклист перед следующей сборкой

- [ ] ✅ Сертификат загружен: "Priroda Spa Distribution Certificate"
- [ ] ✅ Provisioning Profile загружен (Bundle ID: `ru.prirodaspa.app`)
- [ ] ✅ Интеграция "Priroda Spa" создана
- [ ] ✅ `codemagic.yaml` обновлен (убрал проблемный export-options-plist)
- [ ] ✅ Выбрать workflow "iOS Release" (НЕ "Default Workflow")
- [ ] ✅ Ветка: `master`

---

**После исправлений запустите сборку заново с правильным workflow!**
