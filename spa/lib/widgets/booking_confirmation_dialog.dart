import 'package:flutter/material.dart';
import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';

/// Диалог подтверждения бронирования после возврата из YClients
class BookingConfirmationDialog extends StatelessWidget {
  final String serviceName;
  final VoidCallback onConfirmed;
  final VoidCallback onCancelled;
  final VoidCallback onSkip;

  const BookingConfirmationDialog({
    super.key,
    required this.serviceName,
    required this.onConfirmed,
    required this.onCancelled,
    required this.onSkip,
  });

  @override
  Widget build(BuildContext context) {
    return Dialog(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(24),
      ),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Иконка
            Container(
              width: 64,
              height: 64,
              decoration: BoxDecoration(
                color: AppColors.buttonPrimary.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(
                Icons.check_circle_outline,
                size: 32,
                color: AppColors.buttonPrimary,
              ),
            ),
            const SizedBox(height: 20),
            
            // Заголовок
            Text(
              'Давайте сверимся',
              style: AppTextStyles.heading2.copyWith(
                color: AppColors.textPrimary,
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            
            // Описание
            Text(
              'Вы записывались на услугу "$serviceName". Что произошло?',
              style: AppTextStyles.bodyMedium.copyWith(
                color: AppColors.textSecondary,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            
            // Кнопки
            Column(
              children: [
                // Кнопка "Я забронировал услугу"
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: onConfirmed,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.buttonPrimary,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      elevation: 0,
                    ),
                    child: Text(
                      'Я забронировал услугу',
                      style: AppTextStyles.bodyLarge.copyWith(
                        color: Colors.white,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                
                // Кнопка "Я отменил её"
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton(
                    onPressed: onCancelled,
                    style: OutlinedButton.styleFrom(
                      foregroundColor: AppColors.error,
                      side: BorderSide(color: AppColors.error, width: 1.5),
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: Text(
                      'Я отменил её',
                      style: AppTextStyles.bodyLarge.copyWith(
                        color: AppColors.error,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                
                // Кнопка "Пропустить"
                TextButton(
                  onPressed: onSkip,
                  child: Text(
                    'Пропустить',
                    style: AppTextStyles.bodyMedium.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  static Future<void> show({
    required BuildContext context,
    required String serviceName,
    required VoidCallback onConfirmed,
    required VoidCallback onCancelled,
    required VoidCallback onSkip,
  }) {
    return showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => BookingConfirmationDialog(
        serviceName: serviceName,
        onConfirmed: () {
          Navigator.of(context).pop();
          onConfirmed();
        },
        onCancelled: () {
          Navigator.of(context).pop();
          onCancelled();
        },
        onSkip: () {
          Navigator.of(context).pop();
          onSkip();
        },
      ),
    );
  }
}

