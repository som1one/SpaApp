import 'dart:async';
import 'dart:ui';

import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb, defaultTargetPlatform, TargetPlatform;

import 'app.dart';
import 'firebase_options.dart';
import 'services/auth_service.dart';
import 'services/storage_service.dart';
import 'services/push_service.dart';

// Условный импорт для Firebase Messaging (только для мобильных)
import 'package:firebase_messaging/firebase_messaging.dart' if (dart.library.html) 'services/firebase_messaging_stub.dart' as messaging;

bool get _isFirebaseSupportedPlatform {
  if (kIsWeb) return false;
  switch (defaultTargetPlatform) {
    case TargetPlatform.android:
    case TargetPlatform.iOS:
    case TargetPlatform.macOS:
      return true;
    default:
      return false;
  }
}

Future<void> _firebaseMessagingBackgroundHandler(messaging.RemoteMessage message) async {
  if (_isFirebaseSupportedPlatform && Firebase.apps.isEmpty) {
    await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
  }
}

Future<void> main() async {
  runZonedGuarded(() async {
    WidgetsFlutterBinding.ensureInitialized();

    // Глобальный обработчик ошибок Flutter
    FlutterError.onError = (FlutterErrorDetails details) {
      FlutterError.presentError(details);
      debugPrint('Flutter Error: ${details.exception}');
      debugPrint('Stack trace: ${details.stack}');
    };

    // Показываем явный экран ошибки вместо "белого экрана" в релизе.
    ErrorWidget.builder = (FlutterErrorDetails details) {
      return Material(
        color: const Color(0xFFF7F6F2),
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: const [
                Icon(Icons.error_outline, size: 44, color: Color(0xFFE53935)),
                SizedBox(height: 12),
                Text(
                  'Произошла ошибка при запуске приложения',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                ),
                SizedBox(height: 8),
                Text(
                  'Попробуйте перезапустить приложение.',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 14),
                ),
              ],
            ),
          ),
        ),
      );
    };

    // Обработчик ошибок в async функциях
    PlatformDispatcher.instance.onError = (error, stack) {
      debugPrint('Platform Error: $error');
      debugPrint('Stack trace: $stack');
      return true;
    };

    // Важно: ничего не ждём до runApp(), чтобы не получить бесконечный белый экран
    // на устройствах/версиях iOS, где SharedPreferences может подвиснуть.
    unawaited(
      StorageService().init().catchError((e) {
        debugPrint('⚠️ Ошибка инициализации StorageService (background): $e');
      }),
    );

    runApp(const MyApp());

    // Инициализация в фоне (не блокирует запуск)
    unawaited(_initInBackground());
  }, (error, stack) {
    debugPrint('Zone Error: $error');
    debugPrint('Stack trace: $stack');
  });
}

Future<void> _initInBackground() async {
  try {
    // Инициализация Firebase только на Android, iOS, macOS (на Windows/Linux currentPlatform бросает UnsupportedError)
    if (_isFirebaseSupportedPlatform && Firebase.apps.isEmpty) {
      await Firebase.initializeApp(
        options: DefaultFirebaseOptions.currentPlatform,
      );
      debugPrint('✅ Firebase initialized');
    }

    // Push-уведомления работают только на мобильных платформах
    if (_isFirebaseSupportedPlatform) {
      try {
        messaging.FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
      } catch (e) {
        debugPrint('⚠️ Ошибка инициализации Firebase Messaging: $e');
      }
    }
  } catch (e) {
    debugPrint('⚠️ Ошибка инициализации Firebase: $e');
    // Продолжаем работу даже если Firebase не инициализирован
  }

  try {
    // Восстановление сессии пользователя
    // restoreSession сам вызовет PushService().init() если нужно
    await AuthService().restoreSession();
    debugPrint('✅ Session restored');
  } catch (e) {
    debugPrint('⚠️ Ошибка восстановления сессии: $e');
  }

  // PushService инициализируется в restoreSession() если пользователь залогинен
  // Если пользователь не залогинен, инициализируем PushService отдельно
  try {
    if (_isFirebaseSupportedPlatform && Firebase.apps.isNotEmpty && !AuthService().isAuthenticated) {
      await PushService().init();
      debugPrint('✅ PushService initialized (user not authenticated)');
    }
  } catch (e) {
    debugPrint('⚠️ Ошибка инициализации PushService: $e');
  }
}

