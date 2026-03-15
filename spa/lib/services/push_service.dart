import 'dart:convert';

import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart' show kIsWeb, defaultTargetPlatform, TargetPlatform, debugPrint;
import 'package:flutter/scheduler.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

import 'api_service.dart';
import 'auth_service.dart';
import '../routes/route_names.dart';

/// Канал для пуш-уведомлений (Android).
const String _channelId = 'priroda_push';
const String _channelName = 'Уведомления PRIRODA';

class PushService {
  static final PushService _instance = PushService._internal();
  factory PushService() => _instance;
  PushService._internal();

  final FirebaseMessaging _messaging = FirebaseMessaging.instance;
  final FlutterLocalNotificationsPlugin _localNotifications = FlutterLocalNotificationsPlugin();
  final _api = ApiService();

  GlobalKey<NavigatorState>? _navigatorKey;
  int _notificationId = 0;

  String get _platform {
    if (kIsWeb) return 'web';
    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        return 'android';
      case TargetPlatform.iOS:
        return 'ios';
      default:
        return 'web';
    }
  }

  /// Вызвать из [MyApp.initState] после создания [GlobalKey<NavigatorState>].
  void setNavigatorKey(GlobalKey<NavigatorState>? key) {
    _navigatorKey = key;
  }

  Future<void> init() async {
    try {
      if (Firebase.apps.isEmpty) {
        debugPrint('⚠️ Firebase not initialized, skipping PushService init');
        return;
      }

      await _initLocalNotifications();

      final settings = await _messaging.requestPermission(
        alert: true,
        badge: true,
        sound: true,
      );
      debugPrint('📱 Push permissions: ${settings.authorizationStatus}');

      // На iOS отключаем автоматический показ в foreground — показываем через локальные
      await _messaging.setForegroundNotificationPresentationOptions(
        alert: false,
        badge: true,
        sound: true,
      );

      await _syncToken();

      _messaging.onTokenRefresh.listen((token) {
        debugPrint('🔄 FCM token refreshed: $token');
        _registerToken(token);
      });

      // Пуш в foreground — показываем локальное уведомление
      FirebaseMessaging.onMessage.listen((RemoteMessage message) {
        debugPrint('📬 Push (foreground): ${message.notification?.title}');
        _showLocalNotification(
          title: message.notification?.title ?? 'PRIRODA SPA',
          body: message.notification?.body ?? '',
          data: message.data,
        );
      });

      // Тап по пушу (приложение в background или открыто)
      FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
        debugPrint('👆 Push opened: ${message.data}');
        _navigateFromNotification(message.data);
      });

      // Приложение запущено из пуша (terminated state)
      final initialMessage = await _messaging.getInitialMessage();
      if (initialMessage != null) {
        debugPrint('🚀 App launched from notification: ${initialMessage.data}');
        SchedulerBinding.instance.addPostFrameCallback((_) {
          _navigateFromNotification(initialMessage.data);
        });
      }
    } catch (e) {
      debugPrint('❌ Error initializing PushService: $e');
    }
  }

  Future<void> _initLocalNotifications() async {
    const android = AndroidInitializationSettings('@mipmap/ic_launcher');
    const ios = DarwinInitializationSettings(
      requestAlertPermission: false,
      requestBadgePermission: true,
    );
    const settings = InitializationSettings(android: android, iOS: ios);

    await _localNotifications.initialize(
      settings,
      onDidReceiveNotificationResponse: _onNotificationTapped,
    );

    if (defaultTargetPlatform == TargetPlatform.android) {
      final plugin = _localNotifications.resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>();
      await plugin?.createNotificationChannel(
        const AndroidNotificationChannel(
          _channelId,
          _channelName,
          description: 'Рассылки и акции PRIRODA SPA',
          importance: Importance.high,
          playSound: true,
        ),
      );
    }
  }

  void _onNotificationTapped(NotificationResponse response) {
    if (response.payload == null || response.payload!.isEmpty) return;
    try {
      final data = Map<String, String>.from(jsonDecode(response.payload!) as Map);
      _navigateFromNotification(data);
    } catch (_) {
      _navigateToHome();
    }
  }

  void _showLocalNotification({
    required String title,
    required String body,
    Map<String, dynamic> data = const {},
  }) {
    final payload = data.isEmpty ? null : jsonEncode(Map<String, String>.from(data));
    final id = _notificationId++;
    final details = NotificationDetails(
      android: AndroidNotificationDetails(
        _channelId,
        _channelName,
        channelDescription: 'Рассылки и акции PRIRODA SPA',
        importance: Importance.high,
        priority: Priority.high,
      ),
      iOS: const DarwinNotificationDetails(
        presentAlert: true,
        presentBadge: true,
        presentSound: true,
      ),
    );
    _localNotifications.show(id, title, body, details, payload: payload);
  }

  void _navigateFromNotification(Map<String, dynamic> data) {
    final key = _navigatorKey;
    if (key?.currentContext == null) {
      debugPrint('⚠️ Navigator not ready for push navigation');
      return;
    }
    // Пока всегда открываем главную; campaign_id можно использовать для глубокой ссылки позже
    _navigateToHome();
  }

  void _navigateToHome() {
    final key = _navigatorKey;
    if (key?.currentContext == null) return;
    Navigator.of(key!.currentContext!).pushNamedAndRemoveUntil(
      RouteNames.home,
      (route) => false,
    );
  }

  Future<void> _syncToken() async {
    try {
      final token = await _messaging.getToken();
      if (token != null) {
        debugPrint('🔑 FCM token obtained');
        await _registerToken(token);
      } else {
        debugPrint('⚠️ FCM token is null');
      }
    } catch (e) {
      debugPrint('❌ Error getting FCM token: $e');
    }
  }

  Future<void> _registerToken(String token) async {
    if (!AuthService().isAuthenticated) {
      debugPrint('⏸️ User not authenticated, skipping token registration');
      return;
    }
    try {
      await _api.post('/devices/register', {
        'token': token,
        'platform': _platform,
      });
      debugPrint('✅ Device token registered');
    } catch (e) {
      debugPrint('❌ Error registering device token: $e');
    }
  }

  Future<void> unregister() async {
    try {
      final token = await _messaging.getToken();
      if (token != null) {
        await _api.post('/devices/unregister', {'token': token});
        debugPrint('✅ Device token unregistered');
      }
    } catch (e) {
      debugPrint('❌ Error unregistering device token: $e');
    }
  }
}
