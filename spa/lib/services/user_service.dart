import '../models/user.dart';
import 'api_service.dart';
import 'auth_service.dart';

class UserService {
  static final UserService _instance = UserService._internal();
  factory UserService() => _instance;
  UserService._internal();

  final _apiService = ApiService();
  final _authService = AuthService();

  User? _cachedUser;

  User? get cachedUser => _cachedUser;

  Future<User?> getCurrentUser({bool forceRefresh = false}) async {
    if (!forceRefresh && _cachedUser != null) {
      return _cachedUser;
    }

    final token = _authService.token;
    if (token == null) {
      return _cachedUser;
    }

    try {
      _apiService.token = token;
      final response = await _apiService.get('/auth/me');
      if (response is Map<String, dynamic>) {
        final user = User.fromJson(response);
        _cachedUser = user;
        return user;
      }
      return _cachedUser;
    } catch (e) {
      // При ошибке возвращаем кешированного пользователя или null
      return _cachedUser;
    }
  }

  Future<User?> refreshUser() async {
    return getCurrentUser(forceRefresh: true);
  }

  void updateCachedUser(User user) {
    _cachedUser = user;
  }

  void clearCache() {
    _cachedUser = null;
  }
}


