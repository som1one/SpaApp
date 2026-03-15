import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../../models/booking.dart';
import '../../routes/route_names.dart';
import '../../services/api_service.dart';
import '../../services/auth_service.dart';
import '../../services/local_booking_service.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../utils/api_exceptions.dart';
import '../../widgets/animations.dart';
import '../../widgets/app_bottom_nav.dart';
import '../../widgets/connectivity_wrapper.dart';
import '../../widgets/empty_state.dart';
import '../../widgets/skeleton_loader.dart';

class PastBookingsScreen extends StatefulWidget {
  const PastBookingsScreen({super.key});

  @override
  State<PastBookingsScreen> createState() => _PastBookingsScreenState();
}

class _PastBookingsScreenState extends State<PastBookingsScreen> {
  final _apiService = ApiService();
  final _authService = AuthService();
  final _localBookingService = LocalBookingService();

  List<Booking> _bookings = [];
  bool _isLoading = true;
  String? _error;
  static const String _loyaltyCodeMarker = 'Код клиента';

  @override
  void initState() {
    super.initState();
    _loadBookings();
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

        final response = await _apiService.get('/bookings');

        if (response is List) {
          apiBookings = (response as List)
              .where((item) => item is Map<String, dynamic>)
              .map(
                (item) => Booking.fromJson(
                  item as Map<String, dynamic>,
                ),
              )
              .toList();
        } else if (response is Map<String, dynamic>) {
          final List<dynamic> data =
              response['bookings'] as List<dynamic>? ?? [];
          apiBookings = data
              .where((item) => item is Map<String, dynamic>)
              .map(
                (item) => Booking.fromJson(
                  item as Map<String, dynamic>,
                ),
              )
              .toList();
        }
      } catch (e) {
        // Игнорируем ошибки API, покажем локальные записи
      }

      // Загружаем локальные записи
      final localBookingsData = await _localBookingService.getLocalBookings();
      final localBookings = localBookingsData
          .map((json) => Booking.fromJson(json))
          .toList();

      // Объединяем записи
      final allBookings = [...apiBookings, ...localBookings];

      // Фильтруем отменённые локально
      final cancelledIds = await _localBookingService.getCancelledBookingIds();
      final filtered = allBookings
          .where((booking) => !cancelledIds.contains(booking.id))
          .toList();

      final now = DateTime.now();

      // Берём только прошедшие записи
      final pastBookings = filtered
          .where(
            (booking) =>
                (booking.appointmentDateTime.isBefore(now) ||
                    booking.status == 'completed' ||
                    booking.status == 'cancelled') &&
                _hasLoyaltyCode(booking),
          )
          .toList()
        ..sort(
          (a, b) => b.appointmentDateTime.compareTo(a.appointmentDateTime),
        );

      if (!mounted) return;

      setState(() {
        _bookings = pastBookings;
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

  bool _hasLoyaltyCode(Booking booking) {
    final notes = booking.notes ?? '';
    return notes.contains(_loyaltyCodeMarker);
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
            'Прошедшие записи',
            style: AppTextStyles.heading3.copyWith(
              color: AppColors.textPrimary,
              fontWeight: FontWeight.bold,
            ),
          ),
          centerTitle: true,
        ),
        body: Column(
          children: [
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
        bottomNavigationBar: const SafeArea(
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
      message: 'У вас пока нет прошедших записей',
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
                padding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
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
              const Icon(
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
          Row(
            children: [
              const Icon(
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
              const Icon(
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
          if (booking.serviceDuration != null ||
              booking.servicePrice != null) ...[
            const SizedBox(height: 8),
            Row(
              children: [
                if (booking.serviceDuration != null) ...[
                  const Icon(
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
                if (booking.serviceDuration != null &&
                    booking.servicePrice != null)
                  const SizedBox(width: 16),
                if (booking.servicePrice != null) ...[
                  const Icon(
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
          if (booking.isFromYClients) ...[
            const SizedBox(height: 8),
            Row(
              children: [
                const Icon(
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
          if (booking.notes != null &&
              booking.notes!.isNotEmpty &&
              !booking.isFromYClients) ...[
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
        ],
      ),
    );
  }
}


