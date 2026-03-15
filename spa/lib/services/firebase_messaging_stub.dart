// Stub для Firebase Messaging на веб
class RemoteMessage {
  final Map<String, dynamic>? data;
  RemoteMessage({this.data});
}

class FirebaseMessaging {
  static FirebaseMessaging get instance => FirebaseMessaging();
  static void onBackgroundMessage(Future<void> Function(RemoteMessage) handler) {}
  Future<String?> getToken() => Future.value(null);
  Stream<String> get onTokenRefresh => const Stream.empty();
  Stream<RemoteMessage> get onMessage => const Stream.empty();
  Stream<RemoteMessage> get onMessageOpenedApp => const Stream.empty();
  Future<NotificationSettings> requestPermission({
    bool? alert,
    bool? badge,
    bool? sound,
  }) => Future.value(NotificationSettings());
}

class NotificationSettings {
  AuthorizationStatus get authorizationStatus => AuthorizationStatus.notDetermined;
}

enum AuthorizationStatus { notDetermined, denied, authorized, provisional }

