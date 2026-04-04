import 'dart:async';

import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:google_sign_in/google_sign_in.dart';
import 'api_service.dart';
import 'storage_service.dart';
import 'push_service.dart';

class AuthService {
  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;
  AuthService._internal();

  String? _token;
  bool _isAuthenticated = false;
  final _apiService = ApiService();
  final _storageService = StorageService();
  GoogleSignIn? _googleSignIn;

  bool get isAuthenticated => _isAuthenticated;

  String? get token => _token;

  FirebaseAuth get _firebaseAuth => FirebaseAuth.instance;

  GoogleSignIn _getGoogleSignIn() {
    return _googleSignIn ??= GoogleSignIn(
      scopes: const ['email'],
    );
  }

  Future<bool> login(String email, String password) async {
    try {
      final response = await _apiService.post('/auth/login', {
        'email': email,
        'password': password,
      });

      _token = response['access_token'];
      if (_token == null || _token!.isEmpty) {
        throw Exception('Токен не получен от сервера');
      }
      _apiService.token = _token;
      _isAuthenticated = true;
      await _storageService.saveToken(_token!);

      if (Firebase.apps.isNotEmpty) {
        unawaited(PushService().init());
      }

      return true;
    } catch (e) {
      _isAuthenticated = false;
      _token = null;
      _apiService.token = null;
      await _storageService.removeToken();
      return false;
    }
  }

  Future<bool> register({
    required String email,
    required String password,
    required String name,
    required String surname,
    required String phone,
    required String code,
  }) async {
    try {
      // Регистрация через API (после подтверждения email)
      // Требует код подтверждения email
      final Map<String, dynamic> requestData = {
        'email': email,
        'password': password,
        'name': name,
        'surname': surname,
        'phone': phone,
        'code': code,
      };

      await _apiService.post('/auth/register', requestData);

      // После успешной регистрации нужно войти, чтобы получить токен
      // Выполняем автоматический вход
      final loginSuccess = await login(email, password);

      if (loginSuccess) {
        return true;
      } else {
        // Если автоматический вход не удался, регистрация всё равно успешна
        // Пользователь может войти вручную
        _isAuthenticated = false;
        _token = null;
        return true;
      }
    } catch (e) {
      _isAuthenticated = false;
      _token = null;
      rethrow;
    }
  }

  Future<void> logout() async {
    _token = null;
    _isAuthenticated = false;
    await _storageService.removeToken();
    // Отвязываем push-токен
    try {
      await PushService().unregister();
    } catch (_) {}
  }

  Future<void> restoreSession() async {
    final storedToken = await _storageService.getToken();
    if (storedToken != null && storedToken.isNotEmpty) {
      _token = storedToken;
      _apiService.token = _token;
      _isAuthenticated = true;
    }
  }

  Future<bool> signInWithGoogle() async {
    try {
      final googleSignIn = _getGoogleSignIn();

      // Запускаем Google Sign-In
      final GoogleSignInAccount? googleUser = await googleSignIn.signIn();

      if (googleUser == null) {
        // Пользователь отменил вход
        return false;
      }

      // Получаем auth детали от Google
      final GoogleSignInAuthentication googleAuth =
          await googleUser.authentication;

      // Создаем credential
      final credential = GoogleAuthProvider.credential(
        accessToken: googleAuth.accessToken,
        idToken: googleAuth.idToken,
      );

      // Входим в Firebase
      final UserCredential userCredential =
          await _firebaseAuth.signInWithCredential(credential);

      // Получаем токен для вашего бэкенда
      final idToken = await userCredential.user?.getIdToken();

      if (idToken != null && userCredential.user != null) {
        // Отправляем токен на ваш бэкенд для создания/обновления пользователя
        final user = userCredential.user!;
        final response = await _apiService.post('/auth/google', {
          'id_token': idToken,
          'email': user.email,
          'name': user.displayName ?? '',
          'photo_url': user.photoURL,
        });

        _token = response['access_token'];
        if (_token == null || _token!.isEmpty) {
          throw Exception('Токен не получен от сервера');
        }
        _apiService.token = _token;
        _isAuthenticated = true;
        await _storageService.saveToken(_token!);

        if (Firebase.apps.isNotEmpty) {
          unawaited(PushService().init());
        }

        return true;
      }

      return false;
    } catch (e) {
      print('Ошибка Google Sign-In: $e');
      _isAuthenticated = false;
      _token = null;
      _apiService.token = null;
      await _storageService.removeToken();
      return false;
    }
  }

  Future<void> signOutGoogle() async {
    if (_googleSignIn != null) {
      await _googleSignIn!.signOut();
    } else if (kIsWeb) {
      // На web не инициализируем GoogleSignIn без необходимости, чтобы не падать на старте.
    }
    await _firebaseAuth.signOut();
    await logout();
  }

  /// Вход через VK ID
  /// Использует WebView для OAuth авторизации
  Future<bool> signInWithVK({
    required String vkAppId,
    required Function(String accessToken, int userId, String? email,
            String? firstName, String? lastName, String? photoUrl)
        onSuccess,
  }) async {
    try {
      // Этот метод будет вызываться из WebView после успешной авторизации
      // Параметры передаются через callback
      return true;
    } catch (e) {
      print('Ошибка VK Sign-In: $e');
      return false;
    }
  }

  /// Обработка данных от VK ID после авторизации
  Future<bool> handleVkAuthData({
    required String accessToken,
    required int userId,
    String? email,
    String? firstName,
    String? lastName,
    String? photoUrl,
  }) async {
    try {
      // Отправляем данные на бэкенд
      final response = await _apiService.post('/auth/vk', {
        'access_token': accessToken,
        'user_id': userId,
        'email': email,
        'first_name': firstName,
        'last_name': lastName,
        'photo_url': photoUrl,
      });

      _token = response['access_token'];
      if (_token == null || _token!.isEmpty) {
        throw Exception('Токен не получен от сервера');
      }
      _apiService.token = _token;
      _isAuthenticated = true;
      await _storageService.saveToken(_token!);

      return true;
    } catch (e) {
      print('Ошибка обработки VK данных: $e');
      _isAuthenticated = false;
      _token = null;
      _apiService.token = null;
      await _storageService.removeToken();
      return false;
    }
  }
}
