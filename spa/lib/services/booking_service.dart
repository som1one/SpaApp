import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/staff.dart';
import '../models/time_slot.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';

/// Сервис для работы с новым booking flow
class BookingService {
  final _apiService = ApiService();
  final _authService = AuthService();

  /// Получить список доступных мастеров для услуги
  Future<List<StaffMember>> getAvailableStaff(int serviceId) async {
    final token = _authService.token;
    if (token != null) {
      _apiService.token = token;
    }

    final response = await _apiService.get('/booking/staff/$serviceId');
    
    if (response is List) {
      return response.map((json) => StaffMember.fromJson(json as Map<String, dynamic>)).toList();
    }
    
    return [];
  }

  /// Получить список доступных дней
  Future<List<String>> getAvailableDays({
    required int serviceId,
    required int staffId,
    int daysAhead = 60,
  }) async {
    final token = _authService.token;
    if (token != null) {
      _apiService.token = token;
    }

    final url = '/booking/available-days/$serviceId?staff_id=$staffId&days_ahead=$daysAhead';
    final response = await _apiService.get(url);
    
    if (response is List) {
      return response.map((date) => date.toString()).toList();
    }
    
    return [];
  }

  /// Получить доступные временные слоты
  Future<List<TimeSlot>> getAvailableTimeSlots({
    required int serviceId,
    required int staffId,
    String? dateStr,
  }) async {
    final token = _authService.token;
    if (token != null) {
      _apiService.token = token;
    }

    // Формируем URL с query параметрами вручную
    var url = '/booking/time-slots/$serviceId?staff_id=$staffId';
    if (dateStr != null) {
      url += '&date_str=$dateStr';
    }

    final response = await _apiService.get(url);
    
    if (response is List) {
      return response.map((json) => TimeSlot.fromJson(json as Map<String, dynamic>)).toList();
    }
    
    return [];
  }

  /// Создать запись
  Future<Map<String, dynamic>> createBooking({
    required int serviceId,
    required int staffId,
    required String datetimeStr,
    bool useBonuses = false,
    int bonusesAmount = 0,
    String? comment,
  }) async {
    final token = _authService.token;
    if (token != null) {
      _apiService.token = token;
    }

    final body = {
      'service_id': serviceId,
      'staff_id': staffId,
      'datetime_str': datetimeStr,
      'use_bonuses': useBonuses,
      'bonuses_amount': bonusesAmount,
      if (comment != null) 'comment': comment,
    };

    // ApiService.post принимает позиционный параметр data
    final response = await _apiService.post('/booking/create', body);
    
    return response;
  }

  /// Отменить запись
  Future<void> cancelBooking({
    required int bookingId,
    String? reason,
  }) async {
    final token = _authService.token;
    if (token != null) {
      _apiService.token = token;
    }

    final body = {
      'status': 'cancelled',
      'cancelled_reason': reason ?? 'Отменено пользователем',
    };

    await _apiService.put('/bookings/$bookingId', body);
  }
}

