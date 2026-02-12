import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'dart:ui';

import 'app.dart';
import 'firebase_options.dart';
import 'services/auth_service.dart';
import 'services/storage_service.dart';
import 'services/push_service.dart';

// Условный импорт для Firebase Messaging (только для мобильных)
import 'package:firebase_messaging/firebase_messaging.dart' if (dart.library.html) 'services/firebase_messaging_stub.dart' as messaging;

Future<void> _firebaseMessagingBackgroundHandler(messaging.RemoteMessage message) async {
  // Инициализация Firebase в бекграунде
  if (!kIsWeb) {
    await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
  }
}

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Глобальный обработчик ошибок Flutter
  FlutterError.onError = (FlutterErrorDetails details) {
    FlutterError.presentError(details);
    debugPrint('Flutter Error: ${details.exception}');
    debugPrint('Stack trace: ${details.stack}');
  };

  // Обработчик ошибок в async функциях
  PlatformDispatcher.instance.onError = (error, stack) {
    debugPrint('Platform Error: $error');
    debugPrint('Stack trace: $stack');
    return true;
  };

  // Критичная инициализация - только StorageService
  // Остальное делаем в фоне, чтобы не блокировать запуск приложения
  try {
    await StorageService().init();
  } catch (e) {
    debugPrint('⚠️ Ошибка инициализации StorageService: $e');
  }

  // Запускаем приложение сразу, не ждем остальную инициализацию
  runApp(
    const MyApp(),
  );

  // Инициализация в фоне (не блокирует запуск)
  _initInBackground();
}

Future<void> _initInBackground() async {
  try {
    // Инициализация Firebase (может не работать на веб без правильной конфигурации)
    if (Firebase.apps.isEmpty) {
      await Firebase.initializeApp(
        options: DefaultFirebaseOptions.currentPlatform,
      );
      debugPrint('✅ Firebase initialized');
    }

    // Push-уведомления работают только на мобильных платформах
    if (!kIsWeb) {
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
    if (!kIsWeb && Firebase.apps.isNotEmpty && !AuthService().isAuthenticated) {
      await PushService().init();
      debugPrint('✅ PushService initialized (user not authenticated)');
    }
  } catch (e) {
    debugPrint('⚠️ Ошибка инициализации PushService: $e');
  }
}

