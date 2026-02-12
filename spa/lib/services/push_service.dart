import 'dart:io' if (dart.library.html) 'dart:html' as io;
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';
import 'api_service.dart';
import 'auth_service.dart';

class PushService {
  static final PushService _instance = PushService._internal();
  factory PushService() => _instance;
  PushService._internal();

  final FirebaseMessaging _messaging = FirebaseMessaging.instance;
  final _api = ApiService();

  String get _platform {
    if (kIsWeb) return 'android'; // fallback для веба
    if (io.Platform.isAndroid) return 'android';
    if (io.Platform.isIOS) return 'ios';
    return 'android'; // fallback
  }

  Future<void> init() async {
    try {
      // Проверяем, что Firebase инициализирован
      if (Firebase.apps.isEmpty) {
        debugPrint('⚠️ Firebase not initialized, skipping PushService init');
        return;
      }

      // Запрос разрешений на уведомления (особенно важно для iOS)
      final settings = await _messaging.requestPermission(
        alert: true,
        badge: true,
        sound: true,
      );
      
      debugPrint('📱 Push permissions: ${settings.authorizationStatus}');

      // Получаем initial токен и регистрируем устройство, если юзер залогинен
      await _syncToken();

      // Слушаем обновления токена
      _messaging.onTokenRefresh.listen((token) {
        debugPrint('🔄 FCM token refreshed: $token');
        _registerToken(token);
      });

      // Обработка уведомлений в форграунде
      FirebaseMessaging.onMessage.listen((RemoteMessage message) {
        debugPrint('📬 Push notification received (foreground):');
        debugPrint('   Title: ${message.notification?.title}');
        debugPrint('   Body: ${message.notification?.body}');
        debugPrint('   Data: ${message.data}');
        // TODO: Показать локальное уведомление через flutter_local_notifications
      });

      // Обработка нажатий по уведомлению
      FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
        debugPrint('👆 Push notification opened:');
        debugPrint('   Data: ${message.data}');
        final campaignId = message.data['campaign_id'];
        if (campaignId != null) {
          // TODO: Навигация на экран кампании/акции
        }
      });

      // Проверяем, было ли приложение открыто из уведомления
      final initialMessage = await _messaging.getInitialMessage();
      if (initialMessage != null) {
        debugPrint('🚀 App opened from notification:');
        debugPrint('   Data: ${initialMessage.data}');
      }
    } catch (e) {
      debugPrint('❌ Error initializing PushService: $e');
    }
  }

  Future<void> _syncToken() async {
    try {
      final token = await _messaging.getToken();
      if (token != null) {
        debugPrint('🔑 FCM token obtained: $token');
        await _registerToken(token);
      } else {
        debugPrint('⚠️ FCM token is null');
      }
    } catch (e) {
      debugPrint('❌ Error getting FCM token: $e');
    }
  }

  Future<void> _registerToken(String token) async {
    final isAuth = AuthService().isAuthenticated;
    if (!isAuth) {
      debugPrint('⏸️ User not authenticated, skipping token registration');
      return;
    }

    try {
      debugPrint('📤 Registering device token...');
      await _api.post('/devices/register', {
        'token': token,
        'platform': _platform,
      });
      debugPrint('✅ Device token registered successfully');
    } catch (e) {
      debugPrint('❌ Error registering device token: $e');
      // Не игнорируем ошибки, чтобы видеть проблемы
    }
  }

  Future<void> unregister() async {
    try {
      final token = await _messaging.getToken();
      if (token != null) {
        debugPrint('📤 Unregistering device token...');
        await _api.post('/devices/unregister', {'token': token});
        debugPrint('✅ Device token unregistered');
      }
    } catch (e) {
      debugPrint('❌ Error unregistering device token: $e');
    }
  }
}


