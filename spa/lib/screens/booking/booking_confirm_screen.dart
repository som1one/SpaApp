import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../models/service.dart';
import '../../services/booking_service.dart';
import '../../routes/route_names.dart';

class BookingConfirmScreen extends StatefulWidget {
  final int serviceId;
  final Service? service;
  final int staffId;
  final String staffName;
  final String datetime;

  const BookingConfirmScreen({
    super.key,
    required this.serviceId,
    this.service,
    required this.staffId,
    required this.staffName,
    required this.datetime,
  });

  @override
  State<BookingConfirmScreen> createState() => _BookingConfirmScreenState();
}

class _BookingConfirmScreenState extends State<BookingConfirmScreen> {
  final _bookingService = BookingService();
  bool _isCreatingBooking = false;

  double get _servicePrice => widget.service?.price ?? 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.backgroundLight,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new,
              color: AppColors.textPrimary, size: 20),
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Text(
          'Подтверждение',
          style: AppTextStyles.heading3.copyWith(
            fontFamily: 'Inter24',
            color: AppColors.textPrimary,
            fontWeight: FontWeight.w700,
          ),
        ),
        centerTitle: true,
      ),
      body: Column(
        children: [
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildBookingDetails(),
                  const SizedBox(height: 24),
                  _buildPriceSection(),
                ],
              ),
            ),
          ),
          _buildFooter(),
        ],
      ),
    );
  }

  Widget _buildBookingDetails() {
    final datetime = DateTime.parse(widget.datetime);
    final dateStr = DateFormat('d MMMM yyyy', 'ru').format(datetime);
    final timeStr = DateFormat('HH:mm').format(datetime);

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.borderLight),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Детали записи',
            style: AppTextStyles.heading4.copyWith(
              fontFamily: 'Inter24',
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 16),
          _buildDetailRow(
              Icons.spa_outlined, 'Услуга', widget.service?.name ?? 'Услуга'),
          const SizedBox(height: 12),
          _buildDetailRow(
              Icons.person_outline, 'Спа-терапевт', widget.staffName),
          const SizedBox(height: 12),
          _buildDetailRow(Icons.calendar_today_outlined, 'Дата', dateStr),
          const SizedBox(height: 12),
          _buildDetailRow(Icons.access_time_outlined, 'Время', timeStr),
          if (widget.service?.duration != null) ...[
            const SizedBox(height: 12),
            _buildDetailRow(Icons.timer_outlined, 'Длительность',
                '${widget.service!.duration} минут'),
          ],
        ],
      ),
    );
  }

  Widget _buildDetailRow(IconData icon, String label, String value) {
    return Row(
      children: [
        Icon(icon, color: AppColors.buttonPrimary, size: 20),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: AppTextStyles.bodySmall.copyWith(
                  color: AppColors.textSecondary,
                  fontSize: 12,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                value,
                style: AppTextStyles.bodyMedium.copyWith(
                  fontFamily: 'Inter24',
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildPriceSection() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            AppColors.buttonPrimary.withOpacity(0.1),
            AppColors.buttonPrimary.withOpacity(0.05),
          ],
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.buttonPrimary.withOpacity(0.2)),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Стоимость услуги',
                style: AppTextStyles.bodyMedium.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
              Text(
                '${_servicePrice.toStringAsFixed(0)} ₽',
                style: AppTextStyles.bodyLarge.copyWith(
                  fontFamily: 'Inter24',
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          const Divider(height: 1),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'К оплате',
                style: AppTextStyles.bodyLarge.copyWith(
                  fontFamily: 'Inter24',
                  fontWeight: FontWeight.w700,
                ),
              ),
              Text(
                '${_servicePrice.toStringAsFixed(0)} ₽',
                style: AppTextStyles.heading2.copyWith(
                  fontFamily: 'Inter24',
                  fontWeight: FontWeight.w700,
                  color: AppColors.buttonPrimary,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildFooter() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        top: false,
        child: SizedBox(
          width: double.infinity,
          height: 56,
          child: ElevatedButton(
            onPressed: _isCreatingBooking ? null : _handleCreateBooking,
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.buttonPrimary,
              foregroundColor: Colors.white,
              disabledBackgroundColor: AppColors.buttonPrimary.withOpacity(0.5),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16)),
              elevation: 0,
            ),
            child: _isCreatingBooking
                ? const SizedBox(
                    width: 24,
                    height: 24,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                    ),
                  )
                : Text(
                    'Записаться',
                    style: AppTextStyles.bodyLarge.copyWith(
                      fontFamily: 'Inter24',
                      fontWeight: FontWeight.w600,
                      fontSize: 16,
                      color: Colors.white,
                    ),
                  ),
          ),
        ),
      ),
    );
  }

  Future<void> _handleCreateBooking() async {
    setState(() => _isCreatingBooking = true);

    try {
      final result = await _bookingService.createBooking(
        serviceId: widget.serviceId,
        staffId: widget.staffId,
        datetimeStr: widget.datetime,
      );

      if (!mounted) return;

      if (result['success'] == true) {
        // Показываем успех и возвращаемся на главный экран
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                const Icon(Icons.check_circle, color: Colors.white),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'Запись успешно создана!',
                    style: const TextStyle(fontWeight: FontWeight.w600),
                  ),
                ),
              ],
            ),
            backgroundColor: AppColors.success,
            behavior: SnackBarBehavior.floating,
            shape:
                RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          ),
        );

        // Возвращаемся на главный экран
        Navigator.of(context).pushNamedAndRemoveUntil(
          RouteNames.home,
          (route) => false,
        );
      } else {
        throw Exception(result['message'] ?? 'Неизвестная ошибка');
      }
    } catch (e) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Ошибка: ${e.toString()}'),
          backgroundColor: AppColors.error,
        ),
      );

      setState(() => _isCreatingBooking = false);
    }
  }
}
