import 'package:shared_preferences/shared_preferences.dart';

/// Сервис для отслеживания состояния бронирования через YClients
class BookingTrackerService {
  static const String _keyPendingBooking = 'pending_booking';
  static const String _keyServiceId = 'pending_service_id';
  static const String _keyServiceName = 'pending_service_name';
  static const String _keyTimestamp = 'pending_timestamp';

  /// Сохранить информацию о попытке бронирования
  Future<void> setPendingBooking({
    required int serviceId,
    required String serviceName,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_keyPendingBooking, true);
    await prefs.setInt(_keyServiceId, serviceId);
    await prefs.setString(_keyServiceName, serviceName);
    await prefs.setInt(_keyTimestamp, DateTime.now().millisecondsSinceEpoch);
  }

  /// Проверить, есть ли ожидающее подтверждение бронирование
  Future<Map<String, dynamic>?> getPendingBooking() async {
    final prefs = await SharedPreferences.getInstance();
    final hasPending = prefs.getBool(_keyPendingBooking) ?? false;
    
    if (!hasPending) return null;

    final serviceId = prefs.getInt(_keyServiceId);
    final serviceName = prefs.getString(_keyServiceName);
    final timestamp = prefs.getInt(_keyTimestamp);

    if (serviceId == null || serviceName == null || timestamp == null) {
      await clearPendingBooking();
      return null;
    }

    // Проверяем, не прошло ли слишком много времени (например, 1 час)
    final bookingTime = DateTime.fromMillisecondsSinceEpoch(timestamp);
    final now = DateTime.now();
    if (now.difference(bookingTime).inHours > 1) {
      await clearPendingBooking();
      return null;
    }

    return {
      'service_id': serviceId,
      'service_name': serviceName,
      'timestamp': timestamp,
    };
  }

  /// Очистить информацию о ожидающем бронировании
  Future<void> clearPendingBooking() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_keyPendingBooking);
    await prefs.remove(_keyServiceId);
    await prefs.remove(_keyServiceName);
    await prefs.remove(_keyTimestamp);
  }
}

