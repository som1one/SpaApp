import 'package:flutter_cache_manager/flutter_cache_manager.dart';
import 'package:flutter/foundation.dart';

/// Улучшенный менеджер кэша изображений с обработкой ошибок и retry
class SpaImageCacheManager {
  SpaImageCacheManager._();

  static final CacheManager instance = CacheManager(
    Config(
      'spaImageCache',
      stalePeriod: const Duration(days: 30), // Изображения актуальны 30 дней
      maxNrOfCacheObjects: 400, // Максимум 400 изображений в кэше
      repo: JsonCacheInfoRepository(databaseName: 'spaImageCache'),
      fileService: _CustomHttpFileService(),
    ),
  );

  /// Очистка кэша при необходимости
  static Future<void> clearCache() async {
    try {
      await instance.emptyCache();
      if (kDebugMode) {
        debugPrint('✅ Кэш изображений очищен');
      }
    } catch (e) {
      if (kDebugMode) {
        debugPrint('⚠️ Ошибка очистки кэша: $e');
      }
    }
  }

  /// Получение размера кэша
  /// Примечание: В новых версиях flutter_cache_manager API изменился,
  /// поэтому используем упрощенный подход - возвращаем 0
  /// Для получения реального размера можно использовать path_provider
  static Future<int> getCacheSize() async {
    // Упрощенная реализация - возвращаем 0
    // Если нужен реальный размер, можно использовать path_provider
    // для получения директории кэша и подсчета размера файлов
    return 0;
  }
}

/// Кастомный HTTP сервис с retry механизмом и улучшенной обработкой ошибок
class _CustomHttpFileService extends HttpFileService {
  @override
  Future<FileServiceResponse> get(String url, {Map<String, String>? headers}) async {
    // Валидация URL
    if (url.isEmpty) {
      throw ArgumentError('URL не может быть пустым');
    }

    int attempts = 0;
    const maxAttempts = 3;
    const baseDelay = Duration(seconds: 1);
    Exception? lastException;

    while (attempts < maxAttempts) {
      try {
        return await super.get(url, headers: headers);
      } catch (e) {
        lastException = e is Exception ? e : Exception(e.toString());
        attempts++;
        
        if (attempts >= maxAttempts) {
          if (kDebugMode) {
            debugPrint('❌ Не удалось загрузить изображение после $maxAttempts попыток: $url');
          }
          rethrow;
        }
        
        if (kDebugMode) {
          debugPrint('⚠️ Попытка $attempts/$maxAttempts загрузки изображения: $url');
        }
        
        // Экспоненциальная задержка: 1s, 2s, 4s
        await Future.delayed(baseDelay * (1 << (attempts - 1)));
      }
    }
    
    throw lastException ?? Exception('Не удалось загрузить изображение');
  }
}


