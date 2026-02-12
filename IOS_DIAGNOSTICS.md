# Полная диагностика iOS - Найденные проблемы

## 🔴 КРИТИЧЕСКИЕ ПРОБЛЕМЫ:

### 1. Race Condition в initialRoute
**Файл:** `spa/lib/app.dart:90-92`
**Проблема:**
```dart
initialRoute: AuthService().isAuthenticated
    ? RouteNames.home
    : RouteNames.registration,
```
`isAuthenticated` проверяется ДО того, как `restoreSession()` выполнился в фоне. При первом запуске всегда `false`, даже если токен есть.

**Решение:** Использовать FutureBuilder или сделать проверку после restoreSession.

### 2. Синтаксическая ошибка в builder
**Файл:** `spa/lib/app.dart:96-108`
**Проблема:** Отсутствует `return` перед `MediaQuery`.

### 3. Потенциальный null child
**Файл:** `spa/lib/app.dart:106`
**Проблема:** `child ?? const SizedBox()` - если child null, показывается пустой виджет (белый экран).

## ✅ Что проверено и работает:

1. **Info.plist** - все настройки корректны
2. **AppDelegate.swift** - правильная инициализация
3. **Runner.entitlements** - production environment
4. **GoogleService-Info.plist** - правильно настроен
5. **Main.storyboard** - белый фон нормален (это placeholder)
6. **LaunchScreen.storyboard** - правильно настроен
7. **NSAppTransportSecurity** - исключение для HTTP API добавлено

## 🔧 Что нужно исправить:

1. Исправить `initialRoute` - сделать его динамическим
2. Исправить `builder` - добавить return
3. Добавить fallback для случая, когда child null
