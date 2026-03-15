import '../models/loyalty.dart';
import 'api_service.dart';
import 'auth_service.dart';

class LoyaltyService {
  final _apiService = ApiService();
  final _authService = AuthService();

  Future<LoyaltyInfo> getLoyaltyInfo() async {
    final token = _authService.token;
    if (token != null) {
      _apiService.token = token;
    }

    try {
      final response = await _apiService.get('/loyalty/info');
      if (response is Map<String, dynamic>) {
        return LoyaltyInfo.fromJson(response);
      }
      throw Exception('Неверный формат ответа от сервера');
    } catch (e) {
      throw Exception('Ошибка получения информации о лояльности: $e');
    }
  }

  Future<void> updateAutoApply(bool autoApply) async {
    final token = _authService.token;
    if (token != null) {
      _apiService.token = token;
    }

    try {
      await _apiService.patch('/loyalty/auto-apply', {
        'auto_apply': autoApply,
      });
    } catch (e) {
      throw Exception('Ошибка обновления настройки автоприменения: $e');
    }
  }
}

