import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../models/time_slot.dart';
import '../../models/service.dart';
import '../../services/booking_service.dart';
import '../../widgets/skeleton_loader.dart';
import '../../widgets/empty_state.dart';
import '../../routes/route_names.dart';

class TimeSelectionScreen extends StatefulWidget {
  final int serviceId;
  final Service? service;
  final int staffId;
  final String staffName;

  const TimeSelectionScreen({
    super.key,
    required this.serviceId,
    this.service,
    required this.staffId,
    required this.staffName,
  });

  @override
  State<TimeSelectionScreen> createState() => _TimeSelectionScreenState();
}

class _TimeSelectionScreenState extends State<TimeSelectionScreen> {
  final _bookingService = BookingService();
  List<TimeSlot> _timeSlots = [];
  Set<String> _availableDays = {};
  bool _isLoading = true;
  bool _isLoadingDays = true;
  String? _error;
  DateTime _selectedDate = DateTime.now();
  String? _selectedTimeSlot;

  @override
  void initState() {
    super.initState();
    // Инициализация locale для table_calendar
    _selectedDate = DateTime.now();
    _loadAvailableDays();
    _loadTimeSlots();
  }

  Future<void> _loadAvailableDays() async {
    setState(() {
      _isLoadingDays = true;
    });

    try {
      final days = await _bookingService.getAvailableDays(
        serviceId: widget.serviceId,
        staffId: widget.staffId,
        daysAhead: 60,
      );
      
      if (!mounted) return;
      
      setState(() {
        _availableDays = days.toSet();
        _isLoadingDays = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isLoadingDays = false;
      });
    }
  }

  Future<void> _loadTimeSlots({DateTime? date}) async {
    final targetDate = date ?? _selectedDate;
    
    setState(() {
      _isLoading = true;
      _error = null;
      _selectedTimeSlot = null;
    });

    try {
      final dateStr = DateFormat('yyyy-MM-dd').format(targetDate);
      
      final slots = await _bookingService.getAvailableTimeSlots(
        serviceId: widget.serviceId,
        staffId: widget.staffId,
        dateStr: dateStr,
      );
      
      if (!mounted) return;
      
      final filteredSlots = slots.where((slot) => slot.date == dateStr).toList();
      
      setState(() {
        _timeSlots = filteredSlots;
        _isLoading = false;
        _selectedDate = targetDate;
      });
    } catch (e) {
      
      if (!mounted) return;
      
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.backgroundLight,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, color: AppColors.textPrimary, size: 20),
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Text(
          'Выберите время',
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
          // Инфо блок
          Container(
            padding: const EdgeInsets.all(20),
            color: Colors.white,
            child: Row(
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        AppColors.buttonPrimary.withOpacity(0.15),
                        AppColors.buttonPrimary.withOpacity(0.05),
                      ],
                    ),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.person, color: AppColors.buttonPrimary),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        widget.staffName,
                        style: AppTextStyles.bodyLarge.copyWith(
                          fontFamily: 'Inter24',
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      if (widget.service != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          widget.service!.name,
                          style: AppTextStyles.bodySmall.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ],
            ),
          ),
          // Поле выбора даты
          _buildDatePickerField(),
          // Список слотов времени
          Expanded(
            child: _isLoading
                ? _buildLoadingState()
                : _error != null || _timeSlots.isEmpty
                    ? EmptyState(
                        type: EmptyStateType.noData,
                        message: 'Нет доступных слотов на выбранную дату',
                        onButtonPressed: _loadTimeSlots,
                      )
                    : _buildTimeSlotsList(),
          ),
          // Кнопка продолжить
          if (_selectedTimeSlot != null) _buildContinueButton(),
        ],
      ),
    );
  }

  Widget _buildDatePickerField() {
    final now = DateTime.now();
    final firstDate = DateTime(now.year, now.month, now.day);
    final lastDate = firstDate.add(const Duration(days: 365));
    
    final weekdays = [
      'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'
    ];
    final months = [
      'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
      'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
    ];
    
    final dateStr = '${weekdays[_selectedDate.weekday - 1]}, ${_selectedDate.day} ${months[_selectedDate.month - 1]} ${_selectedDate.year}';
    
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Выберите дату',
            style: AppTextStyles.bodyMedium.copyWith(
              fontFamily: 'Inter24',
              fontSize: 16,
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 12),
          GestureDetector(
            onTap: () async {
              final picked = await showDatePicker(
                context: context,
                initialDate: _selectedDate,
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
              
              if (picked != null && picked != _selectedDate) {
                _loadTimeSlots(date: picked);
              }
            },
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 18),
              decoration: BoxDecoration(
                color: const Color(0xFFFAFAFB),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: AppColors.buttonPrimary.withOpacity(0.2),
                  width: 1.5,
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
                    child: const Icon(
                      Icons.calendar_today_outlined,
                      color: AppColors.buttonPrimary,
                      size: 20,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          dateStr,
                          style: AppTextStyles.bodyLarge.copyWith(
                            fontFamily: 'Inter24',
                            fontWeight: FontWeight.w600,
                            color: AppColors.textPrimary,
                            fontSize: 16,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Нажмите, чтобы выбрать другую дату',
                          style: AppTextStyles.bodySmall.copyWith(
                            fontFamily: 'Inter18',
                            color: AppColors.textSecondary,
                            fontSize: 13,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const Icon(
                    Icons.arrow_forward_ios,
                    color: AppColors.textSecondary,
                    size: 16,
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLoadingState() {
    return GridView.builder(
      padding: const EdgeInsets.all(20),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3,
        mainAxisSpacing: 12,
        crossAxisSpacing: 12,
        childAspectRatio: 2,
      ),
      itemCount: 12,
      itemBuilder: (_, __) => const SkeletonLoader(width: double.infinity, height: 48),
    );
  }

  Widget _buildTimeSlotsList() {
    return GridView.builder(
      padding: const EdgeInsets.all(20),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3,
        mainAxisSpacing: 12,
        crossAxisSpacing: 12,
        childAspectRatio: 2,
      ),
      itemCount: _timeSlots.length,
      itemBuilder: (context, index) {
        final slot = _timeSlots[index];
        return _buildTimeSlotCard(slot);
      },
    );
  }

  Widget _buildTimeSlotCard(TimeSlot slot) {
    final isSelected = _selectedTimeSlot == slot.datetime;
    
    return InkWell(
      onTap: slot.available ? () => setState(() => _selectedTimeSlot = slot.datetime) : null,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        decoration: BoxDecoration(
          color: isSelected ? AppColors.buttonPrimary : Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected ? AppColors.buttonPrimary : AppColors.borderLight,
            width: 1.5,
          ),
        ),
        child: Center(
          child: Text(
            slot.time,
            style: AppTextStyles.bodyMedium.copyWith(
              fontFamily: 'Inter24',
              fontWeight: FontWeight.w600,
              color: isSelected ? Colors.white : (slot.available ? AppColors.textPrimary : AppColors.textMuted),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildContinueButton() {
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
            onPressed: _handleContinue,
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.buttonPrimary,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              elevation: 0,
            ),
            child: Text(
              'Продолжить',
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

  void _handleContinue() {
    if (_selectedTimeSlot == null) return;
    
    Navigator.of(context).pushNamed(
      RouteNames.bookingConfirm,
      arguments: {
        'serviceId': widget.serviceId,
        'service': widget.service,
        'staffId': widget.staffId,
        'staffName': widget.staffName,
        'datetime': _selectedTimeSlot!,
      },
    );
  }
}

