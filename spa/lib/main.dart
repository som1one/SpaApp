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

  try {
    // Инициализация StorageService (работает на всех платформах)
    await StorageService().init();
  } catch (e) {
    debugPrint('⚠️ Ошибка инициализации StorageService: $e');
  }

  try {
    // Инициализация Firebase (может не работать на веб без правильной конфигурации)
    if (Firebase.apps.isEmpty) {
      await Firebase.initializeApp(
        options: DefaultFirebaseOptions.currentPlatform,
      );
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
    await AuthService().restoreSession();
  } catch (e) {
    debugPrint('⚠️ Ошибка восстановления сессии: $e');
  }

  try {
    // Инициализация Push-сервиса (только для мобильных)
    if (!kIsWeb) {
      await PushService().init();
    }
  } catch (e) {
    debugPrint('⚠️ Ошибка инициализации PushService: $e');
  }

  // Включаем поддержку высокой частоты обновления (120 Гц)
  runApp(
    const MyApp(),
  );
}

