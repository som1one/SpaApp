import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/foundation.dart' show defaultTargetPlatform, kIsWeb, TargetPlatform;

/// Настройки Firebase для проекта PrirodaSpa.
class DefaultFirebaseOptions {
  static FirebaseOptions get currentPlatform {
    if (kIsWeb) {
      throw UnsupportedError(
        'Конфигурация Firebase для Web не задана. Добавьте web-приложение в Firebase или '
        'обновите файл firebase_options.dart.',
      );
    }
    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        return android;
      case TargetPlatform.iOS:
        return ios;
      case TargetPlatform.macOS:
        return macos;
      case TargetPlatform.windows:
      case TargetPlatform.linux:
        throw UnsupportedError(
          'Конфигурация Firebase для платформы ${defaultTargetPlatform.name} не задана.',
        );
      default:
        throw UnsupportedError('Неизвестная платформа.');
    }
  }

  static const FirebaseOptions android = FirebaseOptions(
    apiKey: 'AIzaSyCC8JymziU3p-sgZjpr_6SV24Z_DGMxSAk',
    appId: '1:7382336719:android:b98838e7c83cb8143f63ba',
    messagingSenderId: '7382336719',
    projectId: 'prirodaspa-74540',
    storageBucket: 'prirodaspa-74540.firebasestorage.app',
  );

  static const FirebaseOptions ios = FirebaseOptions(
    apiKey: 'AIzaSyBHIxrt9s5l5vaAezbZ5XFwyr_HcCQqV34',
    appId: '1:7382336719:ios:02bac34d8ef384bc3f63ba',
    messagingSenderId: '7382336719',
    projectId: 'prirodaspa-74540',
    storageBucket: 'prirodaspa-74540.firebasestorage.app',
    iosClientId: '7382336719-nn6c6hpcfkkqk3s1c5i8f9poshiobcnp.apps.googleusercontent.com',
    iosBundleId: 'ru.prirodaspa.app',
  );

  static const FirebaseOptions macos = FirebaseOptions(
    apiKey: 'AIzaSyBHIxrt9s5l5vaAezbZ5XFwyr_HcCQqV34',
    appId: '1:7382336719:ios:02bac34d8ef384bc3f63ba',
    messagingSenderId: '7382336719',
    projectId: 'prirodaspa-74540',
    storageBucket: 'prirodaspa-74540.firebasestorage.app',
    iosClientId: '7382336719-nn6c6hpcfkkqk3s1c5i8f9poshiobcnp.apps.googleusercontent.com',
    iosBundleId: 'ru.prirodaspa.app',
  );
}
