/// Базовый класс для всех API исключений
class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final dynamic originalError;

  ApiException({
    required this.message,
    this.statusCode,
    this.originalError,
  });

  @override
  String toString() => message;
}

/// Ошибка сети (нет интернета, таймаут и т.д.)
class NetworkException extends ApiException {
  NetworkException({
    String? message,
    dynamic originalError,
  }) : super(
          message: message ?? 'Нет подключения к интернету. Проверьте соединение и попробуйте снова.',
          originalError: originalError,
        );
}

/// Ошибка таймаута
class TimeoutException extends ApiException {
  TimeoutException({
    String? message,
    dynamic originalError,
  }) : super(
          message: message ?? 'Превышено время ожидания. Проверьте соединение и попробуйте снова.',
          originalError: originalError,
        );
}

/// Ошибка авторизации (401)
class UnauthorizedException extends ApiException {
  UnauthorizedException({
    String? message,
    dynamic originalError,
  }) : super(
          message: message ?? 'Сессия истекла. Пожалуйста, войдите снова.',
          statusCode: 401,
          originalError: originalError,
        );
}

/// Ошибка доступа (403)
class ForbiddenException extends ApiException {
  ForbiddenException({
    String? message,
    dynamic originalError,
  }) : super(
          message: message ?? 'Доступ запрещен.',
          statusCode: 403,
          originalError: originalError,
        );
}

/// Ресурс не найден (404)
class NotFoundException extends ApiException {
  NotFoundException({
    String? message,
    dynamic originalError,
  }) : super(
          message: message ?? 'Запрашиваемый ресурс не найден.',
          statusCode: 404,
          originalError: originalError,
        );
}

/// Ошибка сервера (500+)
class ServerException extends ApiException {
  ServerException({
    String? message,
    int? statusCode,
    dynamic originalError,
  }) : super(
          message: message ?? 'Ошибка сервера. Попробуйте позже.',
          statusCode: statusCode,
          originalError: originalError,
        );
}

/// Ошибка валидации (400, 422)
class ValidationException extends ApiException {
  final Map<String, dynamic>? errors;

  ValidationException({
    String? message,
    this.errors,
    int? statusCode,
    dynamic originalError,
  }) : super(
          message: message ?? 'Ошибка валидации данных.',
          statusCode: statusCode,
          originalError: originalError,
        );
}

/// Неизвестная ошибка
class UnknownException extends ApiException {
  UnknownException({
    String? message,
    dynamic originalError,
  }) : super(
          message: message ?? 'Произошла неизвестная ошибка.',
          originalError: originalError,
        );
}

/// Вспомогательная функция для получения понятного сообщения об ошибке
String getErrorMessage(dynamic error) {
  if (error is ApiException) {
    return error.message;
  }

  if (error is Exception) {
    final errorString = error.toString().toLowerCase();
    
    // Ошибки сети
    if (errorString.contains('socketexception') ||
        errorString.contains('failed host lookup') ||
        errorString.contains('network is unreachable') ||
        errorString.contains('connection refused') ||
        errorString.contains('connection timed out')) {
      return 'Нет подключения к интернету. Проверьте соединение и попробуйте снова.';
    }
    
    // Таймауты
    if (errorString.contains('timeout')) {
      return 'Превышено время ожидания. Проверьте соединение и попробуйте снова.';
    }
    
    // Общие ошибки
    return error.toString().replaceFirst('Exception: ', '');
  }

  return 'Произошла ошибка. Попробуйте снова.';
}

