import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';

/// Сервис для локального управления записями без API
class LocalBookingService {
  static const String _keyCancelledBookings = 'cancelled_bookings';
  static const String _keyLocalBookings = 'local_bookings';

  /// Сохранить отмененную запись локально
  Future<void> cancelBooking(int bookingId) async {
    final prefs = await SharedPreferences.getInstance();
    final cancelledIds = await getCancelledBookingIds();
    cancelledIds.add(bookingId);
    await prefs.setStringList(
      _keyCancelledBookings,
      cancelledIds.map((id) => id.toString()).toList(),
    );
  }

  /// Получить список ID отмененных записей
  Future<Set<int>> getCancelledBookingIds() async {
    final prefs = await SharedPreferences.getInstance();
    final cancelledList = prefs.getStringList(_keyCancelledBookings) ?? [];
    return cancelledList.map((id) => int.parse(id)).toSet();
  }

  /// Проверить, отменена ли запись
  Future<bool> isBookingCancelled(int bookingId) async {
    final cancelledIds = await getCancelledBookingIds();
    return cancelledIds.contains(bookingId);
  }

  /// Сохранить локальную запись (созданную через диалог подтверждения)
  Future<void> saveLocalBooking(Map<String, dynamic> bookingData) async {
    final prefs = await SharedPreferences.getInstance();
    final bookings = await getLocalBookings();
    
    // Генерируем временный ID (отрицательный, чтобы не конфликтовать с реальными)
    final tempId = -(DateTime.now().millisecondsSinceEpoch ~/ 1000);
    bookingData['id'] = tempId;
    bookingData['created_at'] = DateTime.now().toIso8601String();
    bookingData['updated_at'] = DateTime.now().toIso8601String();
    
    bookings.add(bookingData);
    await prefs.setString(_keyLocalBookings, jsonEncode(bookings));
  }

  /// Получить все локальные записи
  Future<List<Map<String, dynamic>>> getLocalBookings() async {
    final prefs = await SharedPreferences.getInstance();
    final bookingsJson = prefs.getString(_keyLocalBookings);
    if (bookingsJson == null || bookingsJson.isEmpty) {
      return [];
    }
    try {
      final List<dynamic> decoded = jsonDecode(bookingsJson);
      return decoded.map((item) => item as Map<String, dynamic>).toList();
    } catch (e) {
      return [];
    }
  }

  /// Удалить локальную запись
  Future<void> deleteLocalBooking(int bookingId) async {
    final bookings = await getLocalBookings();
    bookings.removeWhere((booking) => booking['id'] == bookingId);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyLocalBookings, jsonEncode(bookings));
  }

  /// Очистить все локальные данные
  Future<void> clearAll() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_keyCancelledBookings);
    await prefs.remove(_keyLocalBookings);
  }
}

