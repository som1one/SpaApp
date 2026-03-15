import '../utils/constants.dart';

class Helpers {
  /// Форматирование даты и времени
  static String formatDateTime(DateTime date) {
    return '${date.day}.${date.month}.${date.year} ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
  }

  /// Форматирование даты
  static String formatDate(DateTime date) {
    return '${date.day}.${date.month}.${date.year}';
  }

  /// Форматирование валюты
  static String formatCurrency(double amount) {
    return '${amount.toStringAsFixed(0)} ₽';
  }

  /// Обрезка текста
  static String truncate(String text, int maxLength) {
    if (text.length <= maxLength) return text;
    return '${text.substring(0, maxLength)}...';
  }

  /// Проверка интернета
  static Future<bool> checkInternetConnection() async {
    // TODO: Реализовать проверку подключения к интернету
    return true;
  }

  /// Преобразование относительного URL картинки в абсолютный
  /// - Если начинается с http/https — возвращаем как есть
  /// - Если начинается с / — добавляем baseUrl
  /// - Иначе добавляем / и baseUrl
  static String? resolveImageUrl(String? url) {
    if (url == null || url.isEmpty) return null;
    
    try {
      final trimmed = url.trim();
      if (trimmed.isEmpty) return null;

      // Валидация и исправление URL
      if (trimmed.startsWith('http://') || trimmed.startsWith('https://')) {
        // Проверяем валидность абсолютного URL
        try {
          final uri = Uri.parse(trimmed);
          if (uri.hasScheme && uri.hasAuthority) {
            return trimmed;
          }
        } catch (e) {
          // Некорректный URL, возвращаем null
          return null;
        }
      }

      if (trimmed.startsWith('file://')) {
        // file://uploads/... -> http://host/uploads/...
        final withoutScheme = trimmed.replaceFirst('file://', '');
        if (withoutScheme.startsWith('/')) {
          return '${AppConstants.baseUrl}$withoutScheme';
        }
        return '${AppConstants.baseUrl}/$withoutScheme';
      }

      if (trimmed.startsWith('/')) {
        return '${AppConstants.baseUrl}$trimmed';
      }

      return '${AppConstants.baseUrl}/$trimmed';
    } catch (e) {
      // В случае любой ошибки возвращаем null
      return null;
    }
  }
}

