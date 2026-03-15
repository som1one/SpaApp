import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';

class BookingDetailsResult {
  final String serviceName;
  final double priceRub;
  final String? masterName;
  final DateTime? appointmentDateTime;

  BookingDetailsResult({
    required this.serviceName,
    required this.priceRub,
    this.masterName,
    this.appointmentDateTime,
  });
}

class BookingDetailsSheet extends StatefulWidget {
  final String initialServiceName;

  const BookingDetailsSheet({
    super.key,
    required this.initialServiceName,
  });

  static Future<BookingDetailsResult?> show({
    required BuildContext context,
    required String initialServiceName,
  }) {
    return showModalBottomSheet<BookingDetailsResult>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) => BookingDetailsSheet(
        initialServiceName: initialServiceName,
      ),
    );
  }

  @override
  State<BookingDetailsSheet> createState() => _BookingDetailsSheetState();
}

class _BookingDetailsSheetState extends State<BookingDetailsSheet> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _serviceController;
  late final TextEditingController _priceController;
  late final TextEditingController _masterController;
  DateTime? _selectedDateTime;

  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();
    _serviceController = TextEditingController(text: widget.initialServiceName);
    _priceController = TextEditingController();
    _masterController = TextEditingController();
  }

  @override
  void dispose() {
    _serviceController.dispose();
    _priceController.dispose();
    _masterController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSubmitting = true);
    await Future.delayed(const Duration(milliseconds: 150));

    final serviceName = _serviceController.text.trim();
    // Валидатор уже проверил, что значение корректное, поэтому парсинг должен быть успешным
    final priceText = _priceController.text.replaceAll(',', '.');
    final price = double.parse(priceText); // Используем parse вместо tryParse, так как валидатор уже проверил
    final masterName = _masterController.text.trim().isEmpty
        ? null
        : _masterController.text.trim();

    Navigator.of(context).pop(
      BookingDetailsResult(
        serviceName: serviceName,
        priceRub: price,
        masterName: masterName,
        appointmentDateTime: _selectedDateTime,
      ),
    );
  }

  Future<void> _selectDateTime() async {
    final now = DateTime.now();
    final firstDate = DateTime(now.year, now.month, now.day);
    final lastDate = firstDate.add(const Duration(days: 365));

    // Сначала выбираем дату
    final pickedDate = await showDatePicker(
      context: context,
      initialDate: _selectedDateTime ?? now,
      firstDate: firstDate,
      lastDate: lastDate,
      locale: const Locale('ru', 'RU'),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: ColorScheme.light(
              primary: AppColors.buttonPrimary,
              onPrimary: Colors.white,
              surface: Colors.white,
              onSurface: AppColors.textPrimary,
            ),
            textButtonTheme: TextButtonThemeData(
              style: TextButton.styleFrom(
                foregroundColor: AppColors.buttonPrimary,
              ),
            ),
          ),
          child: child!,
        );
      },
    );

    if (pickedDate == null || !mounted) return;

    // Затем выбираем время
    final pickedTime = await showTimePicker(
      context: context,
      initialTime: _selectedDateTime != null
          ? TimeOfDay.fromDateTime(_selectedDateTime!)
          : TimeOfDay.now(),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: ColorScheme.light(
              primary: AppColors.buttonPrimary,
              onPrimary: Colors.white,
              surface: Colors.white,
              onSurface: AppColors.textPrimary,
            ),
            textButtonTheme: TextButtonThemeData(
              style: TextButton.styleFrom(
                foregroundColor: AppColors.buttonPrimary,
              ),
            ),
          ),
          child: child!,
        );
      },
    );

    if (pickedTime != null && mounted) {
      setState(() {
        _selectedDateTime = DateTime(
          pickedDate.year,
          pickedDate.month,
          pickedDate.day,
          pickedTime.hour,
          pickedTime.minute,
        );
      });
    }
  }

  String _formatDateTime(DateTime dateTime) {
    final weekdays = [
      'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'
    ];
    final months = [
      'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
      'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
    ];
    
    return '${weekdays[dateTime.weekday - 1]}, ${dateTime.day} ${months[dateTime.month - 1]} ${dateTime.year} в ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    final bottomInset = MediaQuery.of(context).viewInsets.bottom;

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 20,
            offset: const Offset(0, -4),
          ),
        ],
      ),
      child: Padding(
        padding: EdgeInsets.only(
          left: 20,
          right: 20,
          bottom: bottomInset + 20,
          top: 20,
        ),
        child: Form(
          key: _formKey,
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
              // Заголовок с иконкой
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      Container(
                        width: 40,
                        height: 40,
                        decoration: BoxDecoration(
                          color: AppColors.buttonPrimary.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: const Icon(
                          Icons.event_note,
                          color: AppColors.buttonPrimary,
                          size: 20,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Text(
                        'Детали записи',
                        style: AppTextStyles.heading3.copyWith(
                          fontFamily: 'Inter24',
                          color: AppColors.textPrimary,
                          fontWeight: FontWeight.w700,
                          fontSize: 20,
                        ),
                      ),
                    ],
                  ),
                  IconButton(
                    onPressed: () => Navigator.of(context).pop(),
                    icon: const Icon(Icons.close, size: 22),
                    color: AppColors.textSecondary,
                    style: IconButton.styleFrom(
                      backgroundColor: AppColors.textSecondary.withOpacity(0.1),
                      padding: const EdgeInsets.all(8),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppColors.buttonPrimary.withOpacity(0.05),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: AppColors.buttonPrimary.withOpacity(0.2),
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.info_outline,
                      color: AppColors.buttonPrimary,
                      size: 20,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Мы сохраним запись в приложении, чтобы начислить бонусы и помнить о визите.',
                        style: AppTextStyles.bodySmall.copyWith(
                          fontFamily: 'Inter18',
                          color: AppColors.textSecondary,
                          fontSize: 13,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              // Поле услуги
              _buildSectionLabel('Услуга'),
              const SizedBox(height: 10),
              TextFormField(
                controller: _serviceController,
                decoration: _buildInputDecoration(
                  hint: 'Например, Spa-путешествие',
                  icon: Icons.spa_outlined,
                ),
                style: AppTextStyles.bodyMedium.copyWith(
                  fontFamily: 'Inter24',
                  fontSize: 16,
                  color: AppColors.textPrimary,
                ),
                textInputAction: TextInputAction.next,
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return 'Укажите название услуги';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 20),
              
              // Поле цены
              _buildSectionLabel('Сумма'),
              const SizedBox(height: 10),
              TextFormField(
                controller: _priceController,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                decoration: _buildInputDecoration(
                  hint: 'Например, 7000',
                  icon: Icons.attach_money_outlined,
                  suffixText: '₽',
                ),
                style: AppTextStyles.bodyMedium.copyWith(
                  fontFamily: 'Inter24',
                  fontSize: 16,
                  color: AppColors.textPrimary,
                ),
                textInputAction: TextInputAction.next,
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return 'Укажите сумму услуги';
                  }
                  final number = double.tryParse(value.replaceAll(',', '.'));
                  if (number == null || number <= 0) {
                    return 'Введите корректную сумму';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 20),
              
              // Поле времени
              _buildSectionLabel('Дата и время'),
              const SizedBox(height: 10),
              GestureDetector(
                onTap: _selectDateTime,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 18),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: _selectedDateTime != null
                          ? AppColors.buttonPrimary.withOpacity(0.3)
                          : AppColors.buttonPrimary.withOpacity(0.2),
                      width: _selectedDateTime != null ? 1.5 : 1,
                    ),
                  ),
                  child: Row(
                    children: [
                      Container(
                        width: 40,
                        height: 40,
                        decoration: BoxDecoration(
                          color: AppColors.buttonPrimary.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Icon(
                          Icons.access_time,
                          color: _selectedDateTime != null
                              ? AppColors.buttonPrimary
                              : AppColors.textSecondary,
                          size: 20,
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              _selectedDateTime != null
                                  ? _formatDateTime(_selectedDateTime!)
                                  : 'Выберите дату и время',
                              style: AppTextStyles.bodyMedium.copyWith(
                                fontFamily: 'Inter24',
                                fontSize: 16,
                                color: _selectedDateTime != null
                                    ? AppColors.textPrimary
                                    : const Color(0xFFB6BAC4),
                                fontWeight: _selectedDateTime != null ? FontWeight.w500 : FontWeight.w400,
                              ),
                            ),
                            if (_selectedDateTime == null) ...[
                              const SizedBox(height: 2),
                              Text(
                                'Необязательно',
                                style: AppTextStyles.bodySmall.copyWith(
                                  fontFamily: 'Inter18',
                                  fontSize: 12,
                                  color: AppColors.textSecondary,
                                ),
                              ),
                            ],
                          ],
                        ),
                      ),
                      if (_selectedDateTime != null)
                        IconButton(
                          icon: const Icon(Icons.close, size: 18),
                          color: AppColors.textSecondary,
                          onPressed: () {
                            setState(() {
                              _selectedDateTime = null;
                            });
                          },
                        )
                      else
                        Icon(
                          Icons.arrow_forward_ios,
                          size: 16,
                          color: AppColors.textSecondary.withOpacity(0.5),
                        ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 20),
              
              // Поле мастера
              _buildSectionLabel('Мастер (необязательно)'),
              const SizedBox(height: 10),
              TextFormField(
                controller: _masterController,
                decoration: _buildInputDecoration(
                  hint: 'Имя мастера или специалиста',
                  icon: Icons.person_outline,
                ),
                style: AppTextStyles.bodyMedium.copyWith(
                  fontFamily: 'Inter24',
                  fontSize: 16,
                  color: AppColors.textPrimary,
                ),
                textInputAction: TextInputAction.done,
              ),
              const SizedBox(height: 32),
              Container(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(18),
                  boxShadow: [
                    BoxShadow(
                      color: AppColors.buttonPrimary.withOpacity(0.3),
                      blurRadius: 20,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: SizedBox(
                  width: double.infinity,
                  height: 56,
                  child: ElevatedButton(
                    onPressed: _isSubmitting ? null : _submit,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.buttonPrimary,
                      foregroundColor: Colors.white,
                      disabledBackgroundColor: AppColors.buttonPrimary.withOpacity(0.5),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(18),
                      ),
                      elevation: 0,
                    ),
                    child: _isSubmitting
                        ? const SizedBox(
                            width: 24,
                            height: 24,
                            child: CircularProgressIndicator(
                              strokeWidth: 2.5,
                              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                            ),
                          )
                        : Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text(
                                'Сохранить запись',
                                style: AppTextStyles.bodyLarge.copyWith(
                                  fontFamily: 'Inter24',
                                  color: Colors.white,
                                  fontWeight: FontWeight.w700,
                                  fontSize: 18,
                                ),
                              ),
                              const SizedBox(width: 8),
                              const Icon(
                                Icons.check_circle_outline,
                                color: Colors.white,
                                size: 20,
                              ),
                            ],
                          ),
                  ),
                ),
              ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSectionLabel(String label) {
    return Text(
      label,
      style: AppTextStyles.bodyMedium.copyWith(
        fontFamily: 'Inter24',
        fontSize: 15,
        fontWeight: FontWeight.w600,
        color: AppColors.textPrimary,
      ),
    );
  }

  InputDecoration _buildInputDecoration({
    required String hint,
    required IconData icon,
    String? suffixText,
  }) {
    return InputDecoration(
      hintText: hint,
      hintStyle: AppTextStyles.bodyMedium.copyWith(
        fontFamily: 'Inter24',
        fontSize: 16,
        color: const Color(0xFFB6BAC4),
      ),
      prefixIcon: Container(
        margin: const EdgeInsets.only(right: 12),
        child: Icon(
          icon,
          color: AppColors.buttonPrimary,
          size: 20,
        ),
      ),
      prefixIconConstraints: const BoxConstraints(
        minWidth: 52,
        minHeight: 20,
      ),
      suffixText: suffixText,
      suffixStyle: AppTextStyles.bodyMedium.copyWith(
        fontFamily: 'Inter24',
        fontSize: 16,
        color: AppColors.textPrimary,
        fontWeight: FontWeight.w600,
      ),
      filled: true,
      fillColor: Colors.white,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: BorderSide(
          color: AppColors.buttonPrimary.withOpacity(0.2),
          width: 1,
        ),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: BorderSide(
          color: AppColors.buttonPrimary.withOpacity(0.2),
          width: 1,
        ),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: const BorderSide(
          color: AppColors.buttonPrimary,
          width: 2,
        ),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: const BorderSide(
          color: Colors.red,
          width: 1.5,
        ),
      ),
      contentPadding: const EdgeInsets.symmetric(
        horizontal: 20,
        vertical: 18,
      ),
    );
  }
}


