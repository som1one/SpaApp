import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/foundation.dart'
    show defaultTargetPlatform, kIsWeb, TargetPlatform;

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
    apiKey: 'AIzaSyCVK2ZT6vK2rTWFH0nPWO5rEu1K-JLLf_o',
    appId: '1:1083357348512:android:c0193f7597881ccc1bbfc5',
    messagingSenderId: '1083357348512',
    projectId: 'spaapp-c870f',
    storageBucket: 'spaapp-c870f.firebasestorage.app',
  );

  static const FirebaseOptions ios = FirebaseOptions(
    apiKey: 'AIzaSyBEgP7CCT0Q5_aW6g4dXkyVYfW5FeIsLco',
    appId: '1:1083357348512:ios:e809ee1a3ba7803c1bbfc5',
    messagingSenderId: '1083357348512',
    projectId: 'spaapp-c870f',
    storageBucket: 'spaapp-c870f.firebasestorage.app',
    iosBundleId: 'ru.prirodaspa.app',
  );

  static const FirebaseOptions macos = FirebaseOptions(
    apiKey: 'AIzaSyBEgP7CCT0Q5_aW6g4dXkyVYfW5FeIsLco',
    appId: '1:1083357348512:ios:fde0ffc924e5dca31bbfc5',
    messagingSenderId: '1083357348512',
    projectId: 'spaapp-c870f',
    storageBucket: 'spaapp-c870f.firebasestorage.app',
    iosBundleId: 'com.example.spa',
  );
}
