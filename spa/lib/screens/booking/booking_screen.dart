import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../services/api_service.dart';
import '../../services/auth_service.dart';
import '../../services/user_service.dart';
import '../../models/service.dart';
import '../../models/user.dart';
import '../../routes/route_names.dart';

class BookingScreen extends StatefulWidget {
  final int serviceId;
  final Service? service;

  const BookingScreen({
    super.key,
    required this.serviceId,
    this.service,
  });

  @override
  State<BookingScreen> createState() => _BookingScreenState();
}

class _BookingScreenState extends State<BookingScreen> {
  final _apiService = ApiService();
  final _authService = AuthService();
  
  Service? _service;
  User? _user;
  bool _isLoading = true;
  String? _error;
  
  DateTime _focusedDate = DateTime.now();
  DateTime? _selectedDate;
  String? _selectedTime;
  
  // Доступные временные слоты
  final List<String> _timeSlots = [
    '09:00', '10:00', '11:00', '12:00', '13:00', '14:00',
    '15:00', '16:00', '17:00', '18:00', '19:00', '20:00',
  ];

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final token = _authService.token;
      if (token != null) {
        _apiService.token = token;
      }

      // Загружаем услугу, если не передана
      if (widget.service == null) {
        final serviceResponse = await _apiService.get('/services/${widget.serviceId}');
        if (serviceResponse is Map) {
          _service = Service.fromJson(Map<String, dynamic>.from(serviceResponse as Map));
        }
      } else {
        _service = widget.service;
      }

      // Загружаем данные пользователя
      _user = await UserService().getCurrentUser();

      if (!mounted) return;
      setState(() {
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  bool _isDateAvailable(DateTime date) {
    final now = DateTime.now();
    // Нельзя выбрать прошедшие даты
    if (date.year < now.year || 
        (date.year == now.year && date.month < now.month) ||
        (date.year == now.year && date.month == now.month && date.day < now.day)) {
      return false;
    }
    // Можно выбрать даты на 90 дней вперед
    final maxDate = now.add(const Duration(days: 90));
    if (date.isAfter(maxDate)) {
      return false;
    }
    return true;
  }

  List<String> _getAvailableTimeSlots(DateTime? date) {
    if (date == null) return _timeSlots;
    
    final now = DateTime.now();
    final isToday = date.year == now.year && 
                    date.month == now.month && 
                    date.day == now.day;
    
    if (!isToday) return _timeSlots;
    
    // Для сегодняшней даты фильтруем прошедшие времена
    final currentHour = now.hour;
    final currentMinute = now.minute;
    
    return _timeSlots.where((slot) {
      final parts = slot.split(':');
      final hour = int.parse(parts[0]);
      final minute = int.parse(parts[1]);
      
      if (hour < currentHour) return false;
      if (hour == currentHour && minute <= currentMinute) return false;
      
      // Минимальное время - текущее + 1 час
      final minTime = now.add(const Duration(hours: 1));
      final slotTime = DateTime(now.year, now.month, now.day, hour, minute);
      
      return slotTime.isAfter(minTime);
    }).toList();
  }

  void _handleDateSelect(DateTime date) {
    if (!_isDateAvailable(date)) return;
    
    setState(() {
      _selectedDate = date;
      // Сбрасываем время при смене даты
      _selectedTime = null;
    });
  }

  void _handleTimeSelect(String time) {
    setState(() {
      _selectedTime = time;
    });
  }

  void _handlePreviousMonth() {
    setState(() {
      _focusedDate = DateTime(_focusedDate.year, _focusedDate.month - 1);
    });
  }

  void _handleNextMonth() {
    setState(() {
      _focusedDate = DateTime(_focusedDate.year, _focusedDate.month + 1);
    });
  }

  Future<void> _handleConfirm() async {
    if (_selectedDate == null || _selectedTime == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Выберите дату и время'),
          backgroundColor: AppColors.error,
        ),
      );
      return;
    }

    // Парсим время
    final timeParts = _selectedTime!.split(':');
    final hour = int.parse(timeParts[0]);
    final minute = int.parse(timeParts[1]);
    
    final appointmentDateTime = DateTime(
      _selectedDate!.year,
      _selectedDate!.month,
      _selectedDate!.day,
      hour,
      minute,
    );

    // Переход на следующий шаг (детали)
    Navigator.of(context).pushNamed(
      RouteNames.bookingDetails,
      arguments: {
        'serviceId': _service!.id,
        'service': _service,
        'appointmentDateTime': appointmentDateTime,
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(
            Icons.arrow_back_ios_new,
            color: AppColors.textPrimary,
            size: 20,
          ),
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Text(
          'Забронировать услугу',
          style: AppTextStyles.heading3.copyWith(
            color: AppColors.textPrimary,
            fontWeight: FontWeight.bold,
          ),
        ),
        centerTitle: true,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null || _service == null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.error_outline,
                        size: 64,
                        color: AppColors.error,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'Ошибка загрузки',
                        style: AppTextStyles.heading3.copyWith(
                          color: AppColors.textPrimary,
                        ),
                      ),
                      const SizedBox(height: 24),
                      ElevatedButton(
                        onPressed: _loadData,
                        child: const Text('Повторить'),
                      ),
                    ],
                  ),
                )
              : _buildContent(),
    );
  }

  Widget _buildContent() {
    return Column(
      children: [
        // Прогресс-бар
        _buildProgressBar(),
        
        // Контент
        Expanded(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Календарь
                _buildDateSection(),
                const SizedBox(height: 32),
                
                // Выбор времени
                _buildTimeSection(),
                const SizedBox(height: 100),
              ],
            ),
          ),
        ),

        // Кнопка подтверждения
        _buildConfirmButton(),
      ],
    );
  }

  Widget _buildProgressBar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      child: Row(
        children: [
          _buildProgressStep(
            number: 1,
            label: 'Дата и время',
            isActive: true,
            isCompleted: false,
          ),
          Expanded(
            child: Container(
              height: 2,
              color: AppColors.cardBackground,
              margin: const EdgeInsets.symmetric(horizontal: 8),
            ),
          ),
          _buildProgressStep(
            number: 2,
            label: 'Детали',
            isActive: false,
            isCompleted: false,
          ),
          Expanded(
            child: Container(
              height: 2,
              color: AppColors.cardBackground,
              margin: const EdgeInsets.symmetric(horizontal: 8),
            ),
          ),
          _buildProgressStep(
            number: 3,
            label: 'Забронировать',
            isActive: false,
            isCompleted: false,
          ),
          Expanded(
            child: Container(
              height: 2,
              color: AppColors.cardBackground,
              margin: const EdgeInsets.symmetric(horizontal: 8),
            ),
          ),
          _buildProgressStep(
            number: 4,
            label: 'Подтв',
            isActive: false,
            isCompleted: false,
          ),
        ],
      ),
    );
  }

  Widget _buildProgressStep({
    required int number,
    required String label,
    required bool isActive,
    required bool isCompleted,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: isActive ? AppColors.buttonPrimary : Colors.transparent,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (isActive)
            Icon(
              Icons.eco,
              size: 16,
              color: Colors.white,
            )
          else
            Container(
              width: 20,
              height: 20,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: AppColors.cardBackground,
              ),
              child: Center(
                child: Text(
                  '$number',
                  style: AppTextStyles.bodySmall.copyWith(
                    color: AppColors.textSecondary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ),
          const SizedBox(width: 6),
          Text(
            label,
            style: AppTextStyles.bodySmall.copyWith(
              color: isActive ? Colors.white : AppColors.textSecondary,
              fontWeight: isActive ? FontWeight.w600 : FontWeight.normal,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDateSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Выберите дату',
          style: AppTextStyles.heading3.copyWith(
            color: AppColors.textPrimary,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppColors.cardBackground,
            borderRadius: BorderRadius.circular(16),
          ),
          child: Column(
            children: [
              // Заголовок календаря
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  IconButton(
                    icon: const Icon(Icons.chevron_left, size: 20),
                    onPressed: _handlePreviousMonth,
                    color: AppColors.textPrimary,
                  ),
                  Text(
                    DateFormat('MMMM yyyy г.', 'ru').format(_focusedDate),
                    style: AppTextStyles.bodyLarge.copyWith(
                      color: AppColors.textPrimary,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.chevron_right, size: 20),
                    onPressed: _handleNextMonth,
                    color: AppColors.textPrimary,
                  ),
                ],
              ),
              const SizedBox(height: 16),
              // Дни недели
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
                    .map((day) => Expanded(
                          child: Center(
                            child: Text(
                              day,
                              style: AppTextStyles.bodySmall.copyWith(
                                color: AppColors.textSecondary,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ))
                    .toList(),
              ),
              const SizedBox(height: 12),
              // Календарная сетка
              _buildCalendarGrid(),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildCalendarGrid() {
    final firstDayOfMonth = DateTime(_focusedDate.year, _focusedDate.month, 1);
    final lastDayOfMonth = DateTime(_focusedDate.year, _focusedDate.month + 1, 0);
    final firstWeekday = firstDayOfMonth.weekday; // 1 = Monday, 7 = Sunday
    final daysInMonth = lastDayOfMonth.day;
    
    // Начинаем с понедельника (1)
    final startOffset = firstWeekday == 7 ? 0 : firstWeekday - 1;
    
    final rows = <Widget>[];
    var currentDay = 1;
    
    while (currentDay <= daysInMonth || rows.length < 6) {
      final cells = <Widget>[];
      
      for (int i = 0; i < 7; i++) {
        if (rows.isEmpty && i < startOffset) {
          // Пустые ячейки в начале первого ряда
          cells.add(const Expanded(child: SizedBox()));
        } else if (currentDay <= daysInMonth) {
          final date = DateTime(_focusedDate.year, _focusedDate.month, currentDay);
          final isSelected = _selectedDate != null &&
              _selectedDate!.year == date.year &&
              _selectedDate!.month == date.month &&
              _selectedDate!.day == date.day;
          final isAvailable = _isDateAvailable(date);
          
          cells.add(
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(4),
                child: InkWell(
                  onTap: isAvailable ? () => _handleDateSelect(date) : null,
                  borderRadius: BorderRadius.circular(8),
                  child: Container(
                    height: 40,
                    decoration: BoxDecoration(
                      color: isSelected
                          ? AppColors.buttonPrimary
                          : Colors.transparent,
                      shape: BoxShape.circle,
                    ),
                    child: Center(
                      child: Text(
                        '$currentDay',
                        style: AppTextStyles.bodyMedium.copyWith(
                          color: isSelected
                              ? Colors.white
                              : (isAvailable
                                  ? AppColors.textPrimary
                                  : AppColors.textSecondary.withOpacity(0.3)),
                          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ),
          );
          currentDay++;
        } else {
          // Пустые ячейки в конце последнего ряда
          cells.add(const Expanded(child: SizedBox()));
        }
      }
      
      rows.add(Row(children: cells));
      
      if (currentDay > daysInMonth) break;
    }
    
    return Column(children: rows);
  }

  Widget _buildTimeSection() {
    final availableSlots = _getAvailableTimeSlots(_selectedDate);
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Выберите время',
          style: AppTextStyles.heading3.copyWith(
            color: AppColors.textPrimary,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        SizedBox(
          height: 50,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            itemCount: availableSlots.length,
            itemBuilder: (context, index) {
              final time = availableSlots[index];
              final isSelected = _selectedTime == time;
              
              return Padding(
                padding: EdgeInsets.only(
                  right: index < availableSlots.length - 1 ? 12 : 0,
                ),
                child: InkWell(
                  onTap: () => _handleTimeSelect(time),
                  borderRadius: BorderRadius.circular(16),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                    decoration: BoxDecoration(
                      color: isSelected
                          ? AppColors.buttonPrimary
                          : AppColors.cardBackground,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Center(
                      child: Text(
                        time,
                        style: AppTextStyles.bodyMedium.copyWith(
                          color: isSelected
                              ? Colors.white
                              : AppColors.textPrimary,
                          fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                        ),
                      ),
                    ),
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildConfirmButton() {
    final isEnabled = _selectedDate != null && _selectedTime != null;
    
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
        child: SizedBox(
          width: double.infinity,
          height: 52,
          child: ElevatedButton(
            onPressed: isEnabled ? _handleConfirm : null,
            style: ElevatedButton.styleFrom(
              backgroundColor: isEnabled
                  ? AppColors.buttonPrimary
                  : AppColors.buttonPrimary.withOpacity(0.5),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              elevation: 0,
            ),
            child: Text(
              'Подтвердить бронирование',
              style: AppTextStyles.bodyLarge.copyWith(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
