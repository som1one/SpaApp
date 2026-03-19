import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../services/image_cache_manager.dart';

import '../../routes/route_names.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../models/user.dart';
import '../../models/loyalty.dart';
import '../../models/custom_content.dart';
import '../../services/user_service.dart';
import '../../services/loyalty_service.dart';
import '../../services/custom_content_service.dart';
import '../../services/booking_tracker_service.dart';
import '../../services/local_booking_service.dart';
import '../../services/api_service.dart';
import '../../services/auth_service.dart';
import '../../utils/api_exceptions.dart';
import '../../utils/helpers.dart';
import '../../widgets/popular_journey_carousel.dart';
import '../../widgets/app_bottom_nav.dart';
import '../../widgets/booking_confirmation_dialog.dart';
import '../../widgets/booking_details_sheet.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with WidgetsBindingObserver {
  final _userService = UserService();
  final _loyaltyService = LoyaltyService();
  final _customContentService = CustomContentService();
  final _bookingTracker = BookingTrackerService();
  final _localBookingService = LocalBookingService();
  final _apiService = ApiService();
  final _authService = AuthService();
  User? _user;
  bool _isLoadingUser = true;
  LoyaltyInfo? _loyaltyInfo;
  bool _isLoadingLoyalty = true;
  List<CustomContentBlock> _customBlocks = [];
  bool _isLoadingCustomBlocks = true;
  bool _hasCheckedBooking = false;
  static const String _journeyBlockType = 'spa_travel';

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _loadUser();
    _loadLoyalty();
    _loadCustomBlocks();
    // Проверяем при первой загрузке
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _checkPendingBooking();
      // Убрано автоматическое предложение даты - пользователь сам решит, когда создавать запись
    });
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    super.didChangeAppLifecycleState(state);
    // Когда приложение возвращается в активное состояние
    if (state == AppLifecycleState.resumed) {
      _checkPendingBooking();
      // Убрано автоматическое предложение даты - пользователь сам решит, когда создавать запись
    }
  }

  Future<void> _checkPendingBooking() async {
    if (_hasCheckedBooking) return;

    final pendingBooking = await _bookingTracker.getPendingBooking();
    if (pendingBooking == null || !mounted) return;

    _hasCheckedBooking = true;

    // Небольшая задержка, чтобы UI успел загрузиться
    await Future.delayed(const Duration(milliseconds: 500));

    if (!mounted) return;

    final serviceName = pendingBooking['service_name'] as String;

    BookingConfirmationDialog.show(
      context: context,
      serviceName: serviceName,
      onConfirmed: () => _handleBookingConfirmed(pendingBooking),
      onCancelled: () => _handleBookingCancelled(),
      onSkip: () => _handleBookingSkipped(),
    );
  }

  Future<void> _handleBookingConfirmed(
      Map<String, dynamic> pendingBooking) async {
    try {
      final bookingDetails = await BookingDetailsSheet.show(
        context: context,
        initialServiceName: pendingBooking['service_name'] as String,
      );

      if (!mounted || bookingDetails == null) {
        return;
      }

      // Создаем запись о бронировании локально (без API)
      // Используем выбранную дату и время, если указана, иначе текущая дата + 1 день, 10:00
      final now = DateTime.now();
      final appointmentDate = bookingDetails.appointmentDateTime ??
          DateTime(
            now.year,
            now.month,
            now.day + 1,
            10,
            0,
          );

      final bookingData = {
        'user_id': _user?.id ?? 0,
        'service_name': bookingDetails.serviceName,
        'appointment_datetime': appointmentDate.toIso8601String(),
        'status': 'pending',
        'notes': _composeLocalBookingNotes(bookingDetails),
        'service_duration': null,
        'service_price': (bookingDetails.priceRub * 100).round(),
        'phone': _user?.phone,
      };

      if (bookingDetails.masterName != null &&
          bookingDetails.masterName!.isNotEmpty) {
        bookingData['master_name'] = bookingDetails.masterName;
      }

      // Сохраняем локально
      await _localBookingService.saveLocalBooking(bookingData);

      // Очищаем трекер
      await _bookingTracker.clearPendingBooking();

      // Обновляем данные пользователя
      await _loadUser(forceRefresh: true);

      // Показываем сообщение о том, что запись сохранена
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text(
              'Запись сохранена локально! Вы можете посмотреть её в профиле.'),
          backgroundColor: AppColors.success,
          duration: const Duration(seconds: 3),
          action: SnackBarAction(
            label: 'Открыть профиль',
            textColor: Colors.white,
            onPressed: () {
              Navigator.of(context).pushNamed(RouteNames.profile);
            },
          ),
        ),
      );
    } catch (e) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Ошибка при сохранении записи: ${getErrorMessage(e)}'),
          backgroundColor: AppColors.error,
          duration: const Duration(seconds: 4),
        ),
      );
    }
  }

  String _composeLocalBookingNotes(BookingDetailsResult details) {
    final parts = <String>[
      'Забронировано через YClients',
      'Сумма: ${details.priceRub.toStringAsFixed(0)} ₽',
    ];

    if (details.masterName != null && details.masterName!.isNotEmpty) {
      parts.add('Мастер: ${details.masterName}');
    }

    return parts.join(' • ');
  }

  Future<void> _handleBookingCancelled() async {
    try {
      final pendingBooking = await _bookingTracker.getPendingBooking();
      if (pendingBooking == null) {
        await _bookingTracker.clearPendingBooking();
        return;
      }

      final token = _authService.token;
      if (token != null) {
        _apiService.token = token;
      }

      // Создаем запись об отмене (со статусом cancelled)
      // Используем текущую дату + 1 день как примерную дату записи
      final now = DateTime.now().toUtc();
      final appointmentDate = DateTime.utc(
        now.year,
        now.month,
        now.day + 1,
        10,
        0,
      );

      // Проверяем, что дата в будущем
      if (appointmentDate.isBefore(now)) {
        throw Exception('Неверная дата записи');
      }

      final bookingData = {
        'service_name': pendingBooking['service_name'] as String,
        'appointment_datetime': appointmentDate.toIso8601String(),
        'status': 'cancelled',
        'cancelled_reason': 'Отменено пользователем при возврате из YClients',
        'notes': 'Попытка бронирования через YClients - отменено',
      };

      await _apiService.post('/bookings', bookingData);

      // Очищаем трекер
      await _bookingTracker.clearPendingBooking();

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Информация об отмене сохранена'),
          backgroundColor: AppColors.success,
          duration: Duration(seconds: 2),
        ),
      );

      // Обновляем данные пользователя
      await _loadUser(forceRefresh: true);
    } catch (e) {
      // Очищаем трекер даже при ошибке
      await _bookingTracker.clearPendingBooking();

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
              'Ошибка при сохранении информации об отмене: ${getErrorMessage(e)}'),
          backgroundColor: AppColors.error,
          duration: const Duration(seconds: 3),
        ),
      );
    }
  }

  Future<void> _handleBookingSkipped() async {
    // Просто очищаем трекер, ничего не делаем
    await _bookingTracker.clearPendingBooking();
  }

  Future<void> _loadUser({bool forceRefresh = false}) async {
    try {
      final user =
          await _userService.getCurrentUser(forceRefresh: forceRefresh);
      if (!mounted) return;
      setState(() {
        _user = user;
        _isLoadingUser = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _isLoadingUser = false;
      });
    }
  }

  Future<void> _loadLoyalty() async {
    try {
      final info = await _loyaltyService.getLoyaltyInfo();
      if (!mounted) return;
      setState(() {
        _loyaltyInfo = info;
        _isLoadingLoyalty = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _isLoadingLoyalty = false;
      });
    }
  }

  Future<void> _loadCustomBlocks() async {
    if (mounted) {
      setState(() {
        _isLoadingCustomBlocks = _customBlocks.isEmpty;
      });
    }

    final cached = await _customContentService.getCachedBlocks();
    if (cached.isNotEmpty && mounted) {
      setState(() {
        _customBlocks = cached;
        _isLoadingCustomBlocks = false;
      });
    }

    try {
      final blocks = await _customContentService.getCustomContentBlocks();
      if (!mounted) return;
      setState(() {
        _customBlocks = blocks;
        _isLoadingCustomBlocks = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isLoadingCustomBlocks = _customBlocks.isEmpty;
      });
    }
  }

  Future<void> _refresh() async {
    await Future.wait([
      _loadUser(forceRefresh: true),
      _loadLoyalty(),
      _loadCustomBlocks(),
    ]);
  }

  Future<void> _openExternalUrl(String url) async {
    final uri = Uri.parse(url);
    final launched = await launchUrl(uri, mode: LaunchMode.externalApplication);
    if (!launched && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Не удалось открыть ссылку'),
          backgroundColor: AppColors.error,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final journeyItems = _customBlocks
        .where((b) => b.blockType == _journeyBlockType)
        .map(
          (b) => PopularJourneyItem(
            title: b.title,
            subtitle: (b.subtitle ?? '').trim(),
            url: b.actionUrl,
            imageUrl: b.imageUrl == null
                ? null
                : (Helpers.resolveImageUrl(b.imageUrl!) ?? b.imageUrl),
          ),
        )
        .where((item) => item.title.trim().isNotEmpty)
        .toList();

    final contentBlocks =
        _customBlocks.where((b) => b.blockType != _journeyBlockType).toList();

    return Scaffold(
      backgroundColor: AppColors.white,
      body: SafeArea(
        bottom: false,
        child: RefreshIndicator(
          onRefresh: _refresh,
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.only(bottom: 100),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildTopSection(),
                _buildLoyaltyCard(),
                const SizedBox(height: 32),
                PopularJourneyCarousel(items: journeyItems),
                const SizedBox(height: 32),
                if (contentBlocks.isNotEmpty) ...[
                  _buildCustomContentBlocks(contentBlocks),
                  const SizedBox(height: 32),
                ],
                _buildActionButtons(),
                const SizedBox(height: 32),
              ],
            ),
          ),
        ),
      ),
      bottomNavigationBar: SafeArea(
        top: false,
        child: AppBottomNav(
          current: BottomNavItem.home,
        ),
      ),
    );
  }

  Widget _buildTopSection() {
    final displayName = _user?.fullName ?? '';
    final hasName = displayName.trim().isNotEmpty;
    return Container(
      decoration: BoxDecoration(
        color: AppColors.white,
        boxShadow: [
          BoxShadow(
            color: AppColors.shadowLight,
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: double.infinity,
            height: 88,
            child: Stack(
              children: [
                Positioned(
                  left: 0,
                  right: 0,
                  top: 0,
                  bottom: 0,
                  child: Center(
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        SvgPicture.asset(
                          'assets/images/Home/sheet.svg',
                          width: 24,
                          height: 24,
                          colorFilter: const ColorFilter.mode(
                            AppColors.textPrimary,
                            BlendMode.srcIn,
                          ),
                        ),
                        const SizedBox(width: 10),
                        Text(
                          'PRIRODA SPA',
                          style: AppTextStyles.heading3.copyWith(
                            fontFamily: 'Inter24',
                            fontWeight: FontWeight.w700,
                            fontSize: 19,
                            letterSpacing: 0.5,
                            color: AppColors.textPrimary,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
          // Аккуратный разделитель под PRIRODA SPA
          Container(
            margin: const EdgeInsets.symmetric(horizontal: 28),
            height: 1,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  Colors.transparent,
                  AppColors.buttonPrimary.withOpacity(0.2),
                  AppColors.buttonPrimary.withOpacity(0.3),
                  AppColors.buttonPrimary.withOpacity(0.2),
                  Colors.transparent,
                ],
                stops: const [0.0, 0.2, 0.5, 0.8, 1.0],
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(28, 20, 28, 24),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        'Добрый день,',
                        style: AppTextStyles.heading3.copyWith(
                          fontFamily: 'Inter24',
                          fontSize: 26,
                          height: 34 / 26,
                          fontWeight: FontWeight.w700,
                          color: AppColors.textPrimary,
                          letterSpacing: -0.3,
                        ),
                      ),
                      const SizedBox(height: 4),
                      AnimatedSwitcher(
                        duration: const Duration(milliseconds: 250),
                        child: Text(
                          hasName
                              ? '$displayName!'
                              : (_isLoadingUser ? '...' : 'Гость!'),
                          key: ValueKey<String>(
                            hasName
                                ? displayName
                                : (_isLoadingUser ? 'loading' : 'guest'),
                          ),
                          style: AppTextStyles.heading3.copyWith(
                            fontFamily: 'Inter24',
                            fontSize: 26,
                            height: 34 / 26,
                            fontWeight: FontWeight.w700,
                            color: AppColors.buttonPrimary,
                            letterSpacing: -0.3,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 20),
                GestureDetector(
                  onTap: () async {
                    await Navigator.of(context).pushNamed(RouteNames.profile);
                    await _loadUser(forceRefresh: true);
                  },
                  child: _buildAvatar(),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAvatar() {
    final avatarUrl = _user?.avatarUrl;
    return Container(
      width: 56,
      height: 56,
      decoration: BoxDecoration(
        color: AppColors.primaryWithOpacity10,
        borderRadius: BorderRadius.circular(28),
        border: Border.all(
          color: AppColors.buttonPrimary.withOpacity(0.12),
          width: 1.5,
        ),
        boxShadow: [
          BoxShadow(
            color: AppColors.buttonPrimary.withOpacity(0.08),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(28),
        child: avatarUrl != null && avatarUrl.isNotEmpty
            ? CachedNetworkImage(
                imageUrl: Helpers.resolveImageUrl(avatarUrl) ?? avatarUrl,
                width: 56,
                height: 56,
                fit: BoxFit.cover,
                cacheManager: SpaImageCacheManager.instance,
                placeholder: (_, __) => _buildAvatarPlaceholder(),
                errorWidget: (_, __, ___) => _buildAvatarPlaceholder(),
              )
            : _buildAvatarPlaceholder(),
      ),
    );
  }

  Widget _buildAvatarPlaceholder() {
    return Padding(
      padding: const EdgeInsets.all(10),
      child: SvgPicture.asset(
        'assets/images/Home/avatar_placeholder.svg',
        colorFilter: ColorFilter.mode(
          AppColors.buttonPrimary,
          BlendMode.srcIn,
        ),
      ),
    );
  }

  // Определить номер уровня на основе бонусов
  int _getLevelNumber(int bonuses) {
    if (bonuses < 30000) return 1;
    if (bonuses < 100000) return 2;
    if (bonuses < 200000) return 3;
    return 4;
  }

  // Получить цвета градиента для уровня на основе цветов приложения
  List<Color> _getLevelGradientColors(int levelNum) {
    switch (levelNum) {
      case 1:
        return [AppColors.primary, AppColors.primaryLight];
      case 2:
        return [AppColors.primaryLight, AppColors.primary];
      case 3:
        return [AppColors.primary, AppColors.primaryDark];
      case 4:
        return [AppColors.primaryDark, AppColors.primaryDarker];
      default:
        return [AppColors.primary, AppColors.primaryLight];
    }
  }

  Color _parseLoyaltyColor(String hex) {
    try {
      return Color(
          int.parse(hex.replaceFirst('#', ''), radix: 16) + 0xFF000000);
    } catch (e) {
      return AppColors.buttonPrimary;
    }
  }

  Widget _buildLoyaltyCard() {
    final currentBonuses = _loyaltyInfo?.currentBonuses ?? 0;
    final levelName = _loyaltyInfo?.currentLevel?.name ?? '0';
    final levelNum = int.tryParse(levelName) ?? 0;
    final displayLevelName = 'Уровень $levelName';

    // Используем цвета из AppColors для градиента
    final gradientColors = _getLevelGradientColors(levelNum);
    final iconColor = AppColors.buttonPrimary;

    return Padding(
      padding: const EdgeInsets.fromLTRB(28, 24, 28, 0),
      child: GestureDetector(
        onTap: () {
          Navigator.of(context).pushNamed(RouteNames.loyalty);
        },
        child: Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: gradientColors,
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(24),
            border: Border.all(
              color: AppColors.buttonPrimary.withOpacity(0.3),
              width: 1,
            ),
            boxShadow: [
              BoxShadow(
                color: AppColors.buttonPrimary.withOpacity(0.12),
                blurRadius: 24,
                offset: const Offset(0, 6),
              ),
            ],
          ),
          child: Row(
            children: [
              Container(
                width: 64,
                height: 64,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: AppColors.white.withOpacity(0.2),
                  border: Border.all(
                    color: Colors.white.withOpacity(0.3),
                    width: 2,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.white.withOpacity(0.15),
                      blurRadius: 12,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Center(
                  child: Icon(
                    Icons.workspace_premium,
                    color: Colors.white,
                    size: 32,
                  ),
                ),
              ),
              const SizedBox(width: 20),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      'Программа лояльности',
                      style: AppTextStyles.heading3.copyWith(
                        fontFamily: 'Inter24',
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                        color: AppColors.white.withOpacity(0.85),
                        letterSpacing: 0.3,
                      ),
                    ),
                    const SizedBox(height: 8),
                    if (_isLoadingLoyalty)
                      Text(
                        'Загружаем ваш уровень...',
                        style: AppTextStyles.bodyMedium.copyWith(
                          fontFamily: 'Inter18',
                          fontSize: 14,
                          color: AppColors.white.withOpacity(0.7),
                        ),
                      )
                    else
                      RichText(
                        text: TextSpan(
                          style: AppTextStyles.bodyMedium.copyWith(
                            fontFamily: 'Inter24',
                            fontSize: 18,
                            color: AppColors.white,
                          ),
                          children: [
                            TextSpan(
                              text: displayLevelName,
                              style: const TextStyle(
                                fontWeight: FontWeight.w700,
                                letterSpacing: -0.3,
                              ),
                            ),
                            TextSpan(
                              text: '\n$currentBonuses бонусов',
                              style: TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.w500,
                                color: AppColors.white.withOpacity(0.85),
                              ),
                            ),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
              const SizedBox(width: 12),
              Icon(
                Icons.arrow_forward_ios,
                color: AppColors.white.withOpacity(0.7),
                size: 16,
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _mapLevelToLabel(int level) {
    switch (level) {
      case 1:
        return 'Уровень 1 · Начало пути';
      case 2:
        return 'Уровень 2 · Хороший прогресс';
      case 3:
        return 'Уровень 3 · Почти на максимуме';
      case 4:
        return 'Уровень 4 · Максимальный уровень';
      default:
        return 'Уровень $level';
    }
  }

  Widget _buildActionButtons() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 28),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Специальные предложения',
            style: AppTextStyles.heading3.copyWith(
              fontFamily: 'Inter24',
              fontSize: 20,
              fontWeight: FontWeight.w700,
              color: AppColors.textPrimary,
              letterSpacing: -0.3,
            ),
          ),
          const SizedBox(height: 20),
          _buildActionCard(
            title: 'Подарочные сертификаты',
            subtitle: 'Идеальный подарок для близких',
            icon: Icons.card_giftcard_rounded,
            gradient: const LinearGradient(
              colors: [AppColors.primary, AppColors.primaryDark],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            onPressed: () =>
                _openExternalUrl('https://prirodaspa.ru/gift-sertificate'),
          ),
          const SizedBox(height: 16),
          _buildActionCard(
            title: 'Спа-меню',
            subtitle: 'Выгодные условия на курсы процедур',
            icon: Icons.local_florist_rounded,
            gradient: const LinearGradient(
              colors: [AppColors.primaryLight, AppColors.primary],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            onPressed: () => _openExternalUrl('https://prirodaspa.ru/spa-menu'),
          ),
          const SizedBox(height: 16),
          _buildActionCard(
            title: 'Каталог товаров',
            subtitle: 'Профессиональная косметика для дома',
            icon: Icons.shopping_bag_rounded,
            gradient: const LinearGradient(
              colors: [AppColors.primary, AppColors.primaryDark],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            onPressed: () => _openExternalUrl(
                'https://priroda-therapy.ru/priroda-spa-catalog'),
          ),
        ],
      ),
    );
  }

  Widget _buildActionCard({
    required String title,
    required String subtitle,
    required IconData icon,
    required Gradient gradient,
    required VoidCallback? onPressed,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.white,
        borderRadius: BorderRadius.circular(22),
        border: Border.all(
          color: AppColors.buttonPrimary.withOpacity(0.15),
          width: 1.5,
        ),
        boxShadow: [
          BoxShadow(
            color: AppColors.buttonPrimary.withOpacity(0.08),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
          BoxShadow(
            color: AppColors.shadowLight,
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onPressed,
          borderRadius: BorderRadius.circular(22),
          child: Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(22),
            ),
            child: Row(
              children: [
                Container(
                  width: 56,
                  height: 56,
                  decoration: BoxDecoration(
                    gradient: gradient,
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: gradient.colors.first.withOpacity(0.3),
                        blurRadius: 8,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Icon(
                    icon,
                    color: AppColors.white,
                    size: 28,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        title,
                        style: AppTextStyles.heading3.copyWith(
                          fontFamily: 'Inter24',
                          fontSize: 17,
                          fontWeight: FontWeight.w700,
                          color: AppColors.textPrimary,
                          letterSpacing: -0.3,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        subtitle,
                        style: AppTextStyles.bodyMedium.copyWith(
                          fontFamily: 'Inter18',
                          fontSize: 13,
                          color: AppColors.textSecondary,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ),
                Container(
                  width: 36,
                  height: 36,
                  decoration: BoxDecoration(
                    color: AppColors.buttonPrimary.withOpacity(0.1),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    Icons.arrow_forward_ios_rounded,
                    color: AppColors.buttonPrimary,
                    size: 16,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildCustomContentBlocks(List<CustomContentBlock> blocks) {
    if (_isLoadingCustomBlocks) {
      return const Padding(
        padding: EdgeInsets.symmetric(horizontal: 28),
        child: Center(child: CircularProgressIndicator()),
      );
    }

    if (blocks.isEmpty) {
      return const SizedBox.shrink();
    }

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 28),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: blocks.map((block) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: _buildCustomContentBlock(block),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildCustomContentBlock(CustomContentBlock block) {
    Color? backgroundColor;
    Color? textColor;
    Gradient? gradient;

    // Определяем фон
    if (block.gradientStart != null && block.gradientEnd != null) {
      gradient = LinearGradient(
        colors: [
          _parseColor(block.gradientStart!) ?? AppColors.buttonPrimary,
          _parseColor(block.gradientEnd!) ?? AppColors.buttonPrimary,
        ],
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      );
    } else if (block.backgroundColor != null) {
      backgroundColor = _parseColor(block.backgroundColor!);
    } else {
      backgroundColor = AppColors.white;
    }

    textColor = block.textColor != null
        ? _parseColor(block.textColor!)
        : AppColors.textPrimary;

    return GestureDetector(
      onTap: block.actionUrl != null && block.actionUrl!.isNotEmpty
          ? () => _openExternalUrl(block.actionUrl!)
          : null,
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: backgroundColor,
          gradient: gradient,
          borderRadius: BorderRadius.circular(22),
          border: gradient == null
              ? Border.all(
                  color: AppColors.buttonPrimary.withOpacity(0.15),
                  width: 1.5,
                )
              : null,
          boxShadow: [
            BoxShadow(
              color: (gradient != null
                      ? gradient.colors.first
                      : AppColors.buttonPrimary)
                  .withOpacity(0.08),
              blurRadius: 12,
              offset: const Offset(0, 4),
            ),
            BoxShadow(
              color: AppColors.shadowLight,
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          children: [
            if (block.imageUrl != null && block.imageUrl!.isNotEmpty) ...[
              ClipRRect(
                borderRadius: BorderRadius.circular(16),
                child: CachedNetworkImage(
                  imageUrl: Helpers.resolveImageUrl(block.imageUrl!) ??
                      block.imageUrl!,
                  width: 80,
                  height: 80,
                  fit: BoxFit.cover,
                  cacheManager: SpaImageCacheManager.instance,
                  placeholder: (_, __) => Container(
                    width: 80,
                    height: 80,
                    color: AppColors.borderLight,
                    child: const Center(child: CircularProgressIndicator()),
                  ),
                  errorWidget: (_, __, ___) => Container(
                    width: 80,
                    height: 80,
                    color: AppColors.borderLight,
                    child: Icon(Icons.image_not_supported,
                        color: AppColors.textMuted),
                  ),
                ),
              ),
              const SizedBox(width: 16),
            ],
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    block.title,
                    style: AppTextStyles.heading3.copyWith(
                      fontFamily: 'Inter24',
                      fontSize: 18,
                      fontWeight: FontWeight.w700,
                      color: gradient != null ? AppColors.white : textColor,
                      letterSpacing: -0.3,
                    ),
                  ),
                  if (block.subtitle != null && block.subtitle!.isNotEmpty) ...[
                    const SizedBox(height: 6),
                    Text(
                      block.subtitle!,
                      style: AppTextStyles.bodyMedium.copyWith(
                        fontFamily: 'Inter18',
                        fontSize: 14,
                        color: gradient != null
                            ? AppColors.white.withOpacity(0.9)
                            : textColor?.withOpacity(0.8),
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                  if (block.description != null &&
                      block.description!.isNotEmpty) ...[
                    const SizedBox(height: 8),
                    Text(
                      block.description!,
                      style: AppTextStyles.bodySmall.copyWith(
                        fontFamily: 'Inter18',
                        fontSize: 13,
                        color: gradient != null
                            ? AppColors.white.withOpacity(0.85)
                            : textColor?.withOpacity(0.7),
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ],
              ),
            ),
            if (block.actionUrl != null && block.actionUrl!.isNotEmpty) ...[
              const SizedBox(width: 12),
              Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  color: gradient != null
                      ? Colors.white.withOpacity(0.2)
                      : AppColors.buttonPrimary.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.arrow_forward_ios_rounded,
                  color: gradient != null
                      ? AppColors.white
                      : AppColors.buttonPrimary,
                  size: 16,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Color? _parseColor(String hex) {
    try {
      return Color(
          int.parse(hex.replaceFirst('#', ''), radix: 16) + 0xFF000000);
    } catch (e) {
      return null;
    }
  }
}
