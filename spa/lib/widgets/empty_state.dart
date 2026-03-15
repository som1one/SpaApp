import 'package:flutter/material.dart';
import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';
import '../utils/api_exceptions.dart';

enum EmptyStateType {
  noData, // Нет данных
  noSearchResults, // Нет результатов поиска
  noBookings, // Нет записей
  noUpcomingBookings, // Нет предстоящих записей
  error, // Ошибка
}

class EmptyState extends StatelessWidget {
  final EmptyStateType type;
  final String? title;
  final String? message;
  final IconData? icon;
  final Color? iconColor;
  final String? buttonText;
  final VoidCallback? onButtonPressed;
  final bool compact; // Компактный вариант (без больших отступов)
  final dynamic error; // Ошибка для автоматического определения типа

  const EmptyState({
    super.key,
    required this.type,
    this.title,
    this.message,
    this.icon,
    this.iconColor,
    this.buttonText,
    this.onButtonPressed,
    this.compact = false,
    this.error,
  });

  @override
  Widget build(BuildContext context) {
    final config = _getConfig();

    return SingleChildScrollView(
      child: Container(
        width: double.infinity,
        padding: compact
            ? const EdgeInsets.symmetric(horizontal: 16, vertical: 24)
            : const EdgeInsets.symmetric(horizontal: 32, vertical: 48),
        child: Column(
          mainAxisAlignment:
              compact ? MainAxisAlignment.start : MainAxisAlignment.center,
          mainAxisSize: MainAxisSize.min,
          children: [
          // Иконка
          if (config.icon != null) ...[
            Container(
              width: compact ? 80 : 120,
              height: compact ? 80 : 120,
              decoration: BoxDecoration(
                color: Colors.white,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 20,
                    offset: const Offset(0, 10),
                  ),
                ],
              ),
              child: Icon(
                config.icon,
                size: compact ? 40 : 64,
                color: config.iconColor ?? AppColors.textMuted,
              ),
            ),
            SizedBox(height: compact ? 16 : 32),
          ],

          // Заголовок
          if (config.title != null) ...[
            Text(
              config.title!,
              style: AppTextStyles.heading3.copyWith(
                fontWeight: FontWeight.w700,
                color: AppColors.textPrimary,
                fontSize: compact ? 18 : 20,
              ),
              textAlign: TextAlign.center,
            ),
            SizedBox(height: compact ? 8 : 16),
          ],

          // Сообщение
          if (config.message != null) ...[
            Text(
              config.message!,
              style: AppTextStyles.bodyMedium.copyWith(
                color: AppColors.textSecondary,
                fontSize: compact ? 14 : 16,
              ),
              textAlign: TextAlign.center,
            ),
            SizedBox(height: compact ? 16 : 24),
          ],

          // Кнопка
          if (config.buttonText != null && onButtonPressed != null) ...[
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: onButtonPressed,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.buttonPrimary,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(18),
                  ),
                  padding: EdgeInsets.symmetric(
                    vertical: compact ? 12 : 16,
                  ),
                  elevation: 0,
                ),
                child: Text(
                  config.buttonText!,
                  style: AppTextStyles.bodyLarge.copyWith(
                    fontWeight: FontWeight.w600,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
          ],
        ],
        ),
      ),
    );
  }

  _EmptyStateConfig _getConfig() {
    // Если передан error, автоматически определяем тип и сообщение
    if (error != null && type == EmptyStateType.error) {
      return _getErrorConfig();
    }

    switch (type) {
      case EmptyStateType.noData:
        return _EmptyStateConfig(
          icon: icon ?? Icons.spa_outlined,
          iconColor: iconColor,
          title: title ?? 'Здесь пока ничего нет',
          message: message,
          buttonText: buttonText,
        );

      case EmptyStateType.noSearchResults:
        return _EmptyStateConfig(
          icon: icon ?? Icons.search_off,
          iconColor: iconColor,
          title: title ?? 'Ничего не найдено',
          message: message ?? 'Попробуйте другой запрос',
          buttonText: buttonText,
        );

      case EmptyStateType.noBookings:
        return _EmptyStateConfig(
          icon: icon ?? Icons.calendar_today_outlined,
          iconColor: iconColor,
          title: title ?? 'Нет записей',
          message: message ?? 'У вас пока нет записей на услуги',
          buttonText: buttonText ?? 'Записаться на услугу',
        );

      case EmptyStateType.noUpcomingBookings:
        return _EmptyStateConfig(
          icon: null, // Компактный вариант без иконки
          title: null,
          message: message ?? 'Нет ближайших записей',
          buttonText: null,
        );

      case EmptyStateType.error:
        return _EmptyStateConfig(
          icon: icon ?? Icons.error_outline,
          iconColor: iconColor ?? AppColors.error,
          title: title ?? 'Ошибка загрузки',
          message: message,
          buttonText: buttonText ?? 'Повторить',
        );
    }
  }

  _EmptyStateConfig _getErrorConfig() {
    if (error is NetworkException) {
      return _EmptyStateConfig(
        icon: icon ?? Icons.wifi_off_rounded,
        iconColor: iconColor ?? AppColors.textSecondary,
        title: title ?? 'Нет подключения',
        message: message ?? error.message,
        buttonText: buttonText ?? 'Повторить',
      );
    }

    if (error is TimeoutException) {
      return _EmptyStateConfig(
        icon: icon ?? Icons.timer_off,
        iconColor: iconColor ?? AppColors.warning,
        title: title ?? 'Превышено время ожидания',
        message: message ?? error.message,
        buttonText: buttonText ?? 'Повторить',
      );
    }

    if (error is UnauthorizedException) {
      return _EmptyStateConfig(
        icon: icon ?? Icons.lock_outline,
        iconColor: iconColor ?? AppColors.error,
        title: title ?? 'Сессия истекла',
        message: message ?? error.message,
        buttonText: buttonText ?? 'Войти снова',
      );
    }

    if (error is ServerException) {
      return _EmptyStateConfig(
        icon: icon ?? Icons.cloud_off,
        iconColor: iconColor ?? AppColors.error,
        title: title ?? 'Ошибка сервера',
        message: message ?? error.message,
        buttonText: buttonText ?? 'Повторить',
      );
    }

    if (error is ValidationException) {
      return _EmptyStateConfig(
        icon: icon ?? Icons.error_outline,
        iconColor: iconColor ?? AppColors.warning,
        title: title ?? 'Ошибка валидации',
        message: message ?? error.message,
        buttonText: buttonText,
      );
    }

    // Общая ошибка
    return _EmptyStateConfig(
      icon: icon ?? Icons.error_outline,
      iconColor: iconColor ?? AppColors.error,
      title: title ?? 'Ошибка загрузки',
      message: message ?? getErrorMessage(error),
      buttonText: buttonText ?? 'Повторить',
    );
  }
}

class _EmptyStateConfig {
  final IconData? icon;
  final Color? iconColor;
  final String? title;
  final String? message;
  final String? buttonText;

  _EmptyStateConfig({
    this.icon,
    this.iconColor,
    this.title,
    this.message,
    this.buttonText,
  });
}

// Компактный вариант для встроенных пустых состояний (например, в карточках)
class CompactEmptyState extends StatelessWidget {
  final String message;
  final Color? backgroundColor;

  const CompactEmptyState({
    super.key,
    required this.message,
    this.backgroundColor,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: backgroundColor ?? const Color(0xFFF7F7F2),
        borderRadius: BorderRadius.circular(18),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.03),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Text(
        message,
        style: AppTextStyles.bodyMedium.copyWith(
          color: AppColors.textSecondary,
        ),
        textAlign: TextAlign.center,
      ),
    );
  }
}

