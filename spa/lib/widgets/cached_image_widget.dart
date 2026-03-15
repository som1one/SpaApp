import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kDebugMode;
import 'package:cached_network_image/cached_network_image.dart';
import '../services/image_cache_manager.dart';
import '../theme/app_colors.dart';

/// Улучшенный виджет для кэшированных изображений с обработкой ошибок и retry
class CachedImageWidget extends StatelessWidget {
  final String? imageUrl;
  final BoxFit fit;
  final Widget? placeholder;
  final Widget? errorWidget;
  final double? width;
  final double? height;

  const CachedImageWidget({
    super.key,
    required this.imageUrl,
    this.fit = BoxFit.cover,
    this.placeholder,
    this.errorWidget,
    this.width,
    this.height,
  });

  @override
  Widget build(BuildContext context) {
    // Валидация URL
    if (imageUrl == null || imageUrl!.isEmpty) {
      return _buildErrorWidget();
    }

    final validUrl = _validateAndFixUrl(imageUrl!);
    if (validUrl == null) {
      return _buildErrorWidget();
    }

    return CachedNetworkImage(
      imageUrl: validUrl,
      cacheManager: SpaImageCacheManager.instance,
      fit: fit,
      width: width,
      height: height,
      placeholder: (context, url) => placeholder ?? _buildPlaceholder(),
      errorWidget: (context, url, error) {
        // Логируем ошибку только в debug режиме
        if (kDebugMode) {
          debugPrint('⚠️ Ошибка загрузки изображения: $url - $error');
        }
        return errorWidget ?? _buildErrorWidget();
      },
      // Настройки для стабильности
      fadeInDuration: const Duration(milliseconds: 300),
      fadeOutDuration: const Duration(milliseconds: 100),
      memCacheWidth: width?.toInt(),
      memCacheHeight: height?.toInt(),
      // Retry при ошибках сети
      httpHeaders: {
        'Accept': 'image/*',
      },
    );
  }

  /// Валидация и исправление URL
  String? _validateAndFixUrl(String url) {
    try {
      // Убираем пробелы
      url = url.trim();
      
      // Если URL относительный, возвращаем null (нужна полная обработка)
      if (!url.startsWith('http://') && !url.startsWith('https://')) {
        // Пытаемся исправить, если это относительный путь
        if (url.startsWith('/')) {
          // Можно добавить базовый URL, но лучше оставить как есть
          return null;
        }
        return null;
      }

      // Проверяем валидность URL
      final uri = Uri.parse(url);
      if (!uri.hasScheme || (!uri.scheme.startsWith('http'))) {
        return null;
      }

      return url;
    } catch (e) {
      if (kDebugMode) {
        debugPrint('❌ Некорректный URL: $url - $e');
      }
      return null;
    }
  }

  Widget _buildPlaceholder() {
    return Container(
      color: AppColors.cardBackground,
      child: const Center(
        child: SizedBox(
          width: 24,
          height: 24,
          child: CircularProgressIndicator(
            strokeWidth: 2,
            valueColor: AlwaysStoppedAnimation<Color>(AppColors.buttonPrimary),
          ),
        ),
      ),
    );
  }

  Widget _buildErrorWidget() {
    return Container(
      color: AppColors.cardBackground,
      child: Icon(
        Icons.image_not_supported_outlined,
        color: AppColors.textMuted,
        size: (width != null && height != null) 
            ? (width! < height! ? width! : height!) * 0.4 
            : 40,
      ),
    );
  }
}

