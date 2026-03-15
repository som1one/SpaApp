import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../services/api_service.dart';
import '../../services/auth_service.dart';
import '../../services/local_booking_service.dart';
import '../../models/booking.dart';
import '../../routes/route_names.dart';
import '../../widgets/app_bottom_nav.dart';
import '../../widgets/connectivity_wrapper.dart';
import '../../widgets/skeleton_loader.dart';
import '../../widgets/empty_state.dart';
import '../../widgets/animations.dart';
import '../../utils/api_exceptions.dart';

class BookingsScreen extends StatefulWidget {
  const BookingsScreen({super.key});

  @override
  State<BookingsScreen> createState() => _BookingsScreenState();
}

class _BookingsScreenState extends State<BookingsScreen> {
  final _apiService = ApiService();
  final _authService = AuthService();
  final _localBookingService = LocalBookingService();
  
  List<Booking> _bookings = [];
  bool _isLoading = true;
  String? _error;
  String? _selectedStatus;

  @override
  void initState() {
    super.initState();
    _loadBookings();
  }

  bool _hasCheckedInitialRefresh = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // Проверяем результат навигации и обновляем бронирования при необходимости
    if (!_hasCheckedInitialRefresh) {
      _hasCheckedInitialRefresh = true;
      final result = ModalRoute.of(context)?.settings.arguments;
      if (result is Map && result['refreshBookings'] == true) {
        _loadBookings(forceRefresh: true);
      }
    }
  }

  Future<void> _loadBookings({bool forceRefresh = false}) async {
    if (!forceRefresh) {
      setState(() {
        _isLoading = true;
        _error = null;
      });
    }

    try {
      // Загружаем записи из API (если доступно)
      List<Booking> apiBookings = [];
      try {
        final token = _authService.token;
        if (token != null) {
          _apiService.token = token;
        }

        final params = <String, String>{};
        if (_selectedStatus != null && _selectedStatus!.isNotEmpty) {
          params['status'] = _selectedStatus!;
        }

        final queryString = params.isEmpty 
            ? '' 
            : '?${params.entries.map((e) => '${Uri.encodeComponent(e.key)}=${Uri.encodeComponent(e.value)}').join('&')}';
        
        final response = await _apiService.get('/bookings$queryString');
        
        if (response is List) {
          apiBookings = (response as List)
              .where((item) => item is Map<String, dynamic>)
              .map((item) => Booking.fromJson(item as Map<String, dynamic>))
              .toList();
        }
      } catch (e) {
        // Игнорируем ошибки API
      }

      // Загружаем локальные записи
      final localBookingsData = await _localBookingService.getLocalBookings();
      final localBookings = localBookingsData
          .map((json) => Booking.fromJson(json))
          .toList();

      // Объединяем записи
      final allBookings = [...apiBookings, ...localBookings];

      // Фильтруем отмененные записи
      final cancelledIds = await _localBookingService.getCancelledBookingIds();
      final filteredBookings = allBookings
          .where((booking) => !cancelledIds.contains(booking.id))
          .toList();

      // Применяем фильтр по статусу, если выбран
      final bookings = _selectedStatus != null && _selectedStatus!.isNotEmpty
          ? filteredBookings.where((b) => b.status == _selectedStatus).toList()
          : filteredBookings;

      if (!mounted) return;
      setState(() {
        _bookings = bookings;
        _isLoading = false;
        _error = null;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _cancelBooking(Booking booking) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        title: Text(
          'Отменить бронирование?',
          style: AppTextStyles.heading3.copyWith(
            color: AppColors.textPrimary,
            fontWeight: FontWeight.bold,
          ),
        ),
        content: Text(
          'Вы уверены, что хотите отменить эту запись?',
          style: AppTextStyles.bodyMedium.copyWith(
            color: AppColors.textSecondary,
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: Text(
              'Нет',
              style: AppTextStyles.bodyLarge.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: Text(
              'Да, отменить',
              style: AppTextStyles.bodyLarge.copyWith(
                color: AppColors.error,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );

    if (confirmed != true) return;

    try {
      // Отменяем локально (без API)
      await _localBookingService.cancelBooking(booking.id);
      
      // Если это локальная запись (отрицательный ID), удаляем её
      if (booking.id < 0) {
        await _localBookingService.deleteLocalBooking(booking.id);
      }

      if (!mounted) return;
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Бронирование отменено'),
          backgroundColor: AppColors.success,
        ),
      );

      _loadBookings(forceRefresh: true);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Ошибка при отмене: ${getErrorMessage(e)}'),
          backgroundColor: AppColors.error,
        ),
      );
    }
  }

  String _getStatusText(String status) {
    switch (status) {
      case 'confirmed':
        return 'Подтверждено';
      case 'completed':
        return 'Завершено';
      case 'cancelled':
        return 'Отменено';
      default:
        return status;
    }
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'confirmed':
        return AppColors.success;
      case 'completed':
        return AppColors.textSecondary;
      case 'cancelled':
        return AppColors.error;
      default:
        return AppColors.textSecondary;
    }
  }

  @override
  Widget build(BuildContext context) {
    return ConnectivityWrapper(
      onRetry: _loadBookings,
      child: Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: Text(
          'Мои записи',
          style: AppTextStyles.heading3.copyWith(
            color: AppColors.textPrimary,
            fontWeight: FontWeight.bold,
          ),
        ),
        centerTitle: true,
      ),
      body: Column(
        children: [
          // Фильтры по статусу
          _buildStatusFilters(),
          
          // Список бронирований
          Expanded(
            child: AnimatedStateSwitcher(
              child: _isLoading
                  ? _buildSkeletonLoader()
                  : _error != null
                      ? FadeInWidget(
                          child: _buildErrorState(),
                        )
                      : _bookings.isEmpty
                          ? FadeInWidget(
                              child: _buildEmptyState(),
                            )
                          : _buildBookingsList(),
            ),
          ),
        ],
      ),
      bottomNavigationBar: SafeArea(
        top: false,
        child: AppBottomNav(
          current: BottomNavItem.profile,
        ),
      ),
      ),
    );
  }

  Widget _buildSkeletonLoader() {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: 3,
      itemBuilder: (context, index) {
        return const SkeletonBookingCard();
      },
    );
  }

  Widget _buildStatusFilters() {
    final statuses = [
      {'value': null, 'label': 'Все'},
      {'value': 'confirmed', 'label': 'Подтверждены'},
      {'value': 'completed', 'label': 'Завершены'},
      {'value': 'cancelled', 'label': 'Отменены'},
    ];

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: statuses.map((status) {
            final isSelected = _selectedStatus == status['value'];
            return Padding(
              padding: const EdgeInsets.only(right: 8),
              child: FilterChip(
                selected: isSelected,
                label: Text(status['label'] as String),
                onSelected: (selected) {
                  setState(() {
                    _selectedStatus = selected ? status['value'] as String? : null;
                  });
                  _loadBookings();
                },
                selectedColor: AppColors.buttonPrimary.withOpacity(0.2),
                checkmarkColor: AppColors.buttonPrimary,
                labelStyle: AppTextStyles.bodySmall.copyWith(
                  color: isSelected
                      ? AppColors.buttonPrimary
                      : AppColors.textSecondary,
                  fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                ),
              ),
            );
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildErrorState() {
    return EmptyState(
      type: EmptyStateType.error,
      title: 'Ошибка загрузки',
      error: _error,
      onButtonPressed: () => _loadBookings(),
    );
  }

  Widget _buildEmptyState() {
    return EmptyState(
      type: EmptyStateType.noBookings,
      message: _selectedStatus != null
          ? 'Нет записей с выбранным статусом'
          : 'У вас пока нет записей на услуги',
      onButtonPressed: () {
        Navigator.of(context).pushNamed(RouteNames.menuSpa);
      },
    );
  }

  Widget _buildBookingsList() {
    return RefreshIndicator(
      onRefresh: () => _loadBookings(forceRefresh: true),
      child: ListView.builder(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 100),
        itemCount: _bookings.length,
        itemBuilder: (context, index) {
          final booking = _bookings[index];
          return SlideUpWidget(
            duration: Duration(milliseconds: 300 + (index * 50)),
            offset: 20.0,
            child: _buildBookingCard(booking),
          );
        },
      ),
    );
  }

  Widget _buildBookingCard(Booking booking) {
    final dateFormat = DateFormat('dd MMMM yyyy', 'ru');
    final timeFormat = DateFormat('HH:mm', 'ru');
    
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.cardBackground,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: AppColors.textMuted.withOpacity(0.1),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Заголовок с услугой и статусом
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  booking.serviceName,
                  style: AppTextStyles.heading4.copyWith(
                    color: AppColors.textPrimary,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: _getStatusColor(booking.status).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  _getStatusText(booking.status),
                  style: AppTextStyles.bodySmall.copyWith(
                    color: _getStatusColor(booking.status),
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          if (booking.masterName != null && booking.masterName!.isNotEmpty) ...[
            const SizedBox(height: 6),
            Row(
              children: [
                Icon(
                  Icons.person_outline,
                  size: 16,
                  color: AppColors.textSecondary,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Мастер: ${booking.masterName}',
                    style: AppTextStyles.bodySmall.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                ),
              ],
            ),
          ],
          const SizedBox(height: 12),
          
          // Дата и время
          Row(
            children: [
              Icon(
                Icons.calendar_today,
                size: 16,
                color: AppColors.textSecondary,
              ),
              const SizedBox(width: 8),
              Text(
                dateFormat.format(booking.appointmentDateTime.toLocal()),
                style: AppTextStyles.bodyMedium.copyWith(
                  color: AppColors.textPrimary,
                ),
              ),
              const SizedBox(width: 16),
              Icon(
                Icons.access_time,
                size: 16,
                color: AppColors.textSecondary,
              ),
              const SizedBox(width: 8),
              Text(
                timeFormat.format(booking.appointmentDateTime.toLocal()),
                style: AppTextStyles.bodyMedium.copyWith(
                  color: AppColors.textPrimary,
                ),
              ),
            ],
          ),
          
          // Длительность и цена
          if (booking.serviceDuration != null || booking.servicePrice != null) ...[
            const SizedBox(height: 8),
            Row(
              children: [
                if (booking.serviceDuration != null) ...[
                  Icon(
                    Icons.timer_outlined,
                    size: 16,
                    color: AppColors.textSecondary,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    '${booking.serviceDuration} мин',
                    style: AppTextStyles.bodySmall.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                ],
                if (booking.serviceDuration != null && booking.servicePrice != null)
                  const SizedBox(width: 16),
                if (booking.servicePrice != null) ...[
                  Icon(
                    Icons.attach_money,
                    size: 16,
                    color: AppColors.textSecondary,
                  ),
                  if (booking.priceInRubles != null) ...[
                    const SizedBox(width: 8),
                    Text(
                      '${booking.priceInRubles!.toStringAsFixed(0)} ₽',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ],
              ],
            ),
          ],
          
          // Индикатор записи из YClients
          if (booking.isFromYClients) ...[
            const SizedBox(height: 8),
            Row(
              children: [
                Icon(
                  Icons.check_circle_outline,
                  size: 14,
                  color: AppColors.success,
                ),
                const SizedBox(width: 4),
                Text(
                  'Запись через YClients',
                  style: AppTextStyles.bodySmall.copyWith(
                    color: AppColors.success,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ],
          
          // Комментарий (скрываем техническую информацию YClients)
          if (booking.notes != null && booking.notes!.isNotEmpty && !booking.isFromYClients) ...[
            const SizedBox(height: 8),
            Text(
              booking.notes!,
              style: AppTextStyles.bodySmall.copyWith(
                color: AppColors.textSecondary,
              ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ],
          
          // Кнопка отмены
          if (booking.canCancel) ...[
            const SizedBox(height: 12),
            Align(
              alignment: Alignment.centerRight,
              child: TextButton(
                onPressed: () => _cancelBooking(booking),
                child: Text(
                  'Отменить',
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.error,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}

