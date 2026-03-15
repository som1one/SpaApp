# Исправление белого экрана в TestFlight

## Что исправлено

1. **Добавлен `initState()` в `MyApp`** - теперь локаль загружается при запуске приложения
2. **Добавлена обработка ошибок в `_loadLocale()`** - приложение не упадет, если загрузка локали не удалась
3. **Добавлены глобальные обработчики ошибок** - все ошибки Flutter теперь логируются

## Дополнительные проверки

### 1. Проверь логи в TestFlight

В TestFlight можно посмотреть логи:
- Открой приложение в TestFlight
- Нажми на версию сборки
- Прокрути вниз до "Crash Logs" или "Diagnostics"
- Ищи ошибки связанные с:
  - Firebase инициализацией
  - StorageService
  - LanguageService

### 2. Проверь GoogleService-Info.plist

Убедись, что файл `ios/Runner/GoogleService-Info.plist` есть в проекте и правильно настроен.

### 3. Проверь Info.plist

Убедись, что в `Info.plist` есть все необходимые разрешения.

### 4. Проверь Firebase конфигурацию

Убедись, что:
- `firebase_options.dart` содержит правильные данные для iOS
- Bundle ID совпадает: `ru.prirodaspa.app`
- GoogleService-Info.plist соответствует iOS приложению в Firebase Console

## Если проблема осталась

### Вариант 1: Временное отключение Firebase

Если проблема в Firebase, можно временно отключить его для теста:

```dart
// В main.dart закомментируй блок Firebase
// try {
//   if (Firebase.apps.isEmpty) {
//     await Firebase.initializeApp(...);
//   }
// } catch (e) {
//   ...
// }
```

### Вариант 2: Упрощенная инициализация

Можно сделать инициализацию более безопасной:

```dart
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Только критичные инициализации
  try {
    await StorageService().init();
  } catch (e) {
    debugPrint('StorageService init failed: $e');
  }
  
  // Запускаем приложение сразу
  runApp(const MyApp());
  
  // Остальное инициализируем в фоне
  _initInBackground();
}

Future<void> _initInBackground() async {
  // Firebase, AuthService и т.д.
}
```

### Вариант 3: Проверка через Xcode

Если есть доступ к Mac:
1. Открой проект в Xcode
2. Подключи iPhone
3. Запусти в режиме Debug
4. Посмотри логи в консоли Xcode

## Следующие шаги

1. Запушь изменения в Git
2. Запусти новый билд в Codemagic
3. Загрузи в TestFlight
4. Проверь логи в TestFlight
5. Если проблема осталась - пришли логи
