import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../theme/app_colors.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../services/image_cache_manager.dart';
import '../../theme/app_text_styles.dart';
import '../../services/api_service.dart';
import '../../services/auth_service.dart';
import '../../services/user_service.dart';
import '../../services/loyalty_service.dart';
import '../../services/local_booking_service.dart';
import '../../models/user.dart';
import '../../models/booking.dart';
import '../../models/loyalty.dart';
import '../../routes/route_names.dart';
import '../../utils/helpers.dart';
import '../../widgets/app_bottom_nav.dart';
import '../../widgets/connectivity_wrapper.dart';
import '../../widgets/skeleton_loader.dart';
import '../../widgets/empty_state.dart';
import '../../utils/api_exceptions.dart';
import '../../widgets/animations.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  static const String _adminSupportPhone = '+79006870737';
  static const String _techSupportTelegramUrl = 'https://t.me/priroda_spa';

  final _apiService = ApiService();
  final _authService = AuthService();
  final _userService = UserService();
  final _loyaltyService = LoyaltyService();
  final _localBookingService = LocalBookingService();
  User? _user;
  List<Booking> _bookings = [];
  LoyaltyInfo? _loyaltyInfo;
  bool _isLoading = true;
  bool _isLoadingBookings = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  bool _hasCheckedInitialRefresh = false;
  DateTime? _lastBookingUpdate;

  Future<void> _openDialer(String phone) async {
    final uri = Uri.parse('tel:$phone');
    try {
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      } else if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
              content: Text('Не удалось открыть приложение телефона')),
        );
      }
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Ошибка при попытке звонка')),
        );
      }
    }
  }

  Future<void> _openTechSupportTelegram() async {
    final uri = Uri.parse(_techSupportTelegramUrl);
    try {
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      } else if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Не удалось открыть Telegram')),
        );
      }
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Не удалось открыть Telegram')),
        );
      }
    }
  }

  Future<void> _showEditProfileSheet() async {
    final user = _user;
    if (user == null || !mounted) return;

    final nameController = TextEditingController(text: user.name);
    final surnameController = TextEditingController(text: user.surname ?? '');

    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) => SafeArea(
        top: false,
        child: Padding(
          padding: EdgeInsets.fromLTRB(
            20,
            16,
            20,
            16 + MediaQuery.of(context).viewInsets.bottom,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Данные профиля',
                style: AppTextStyles.heading3.copyWith(
                  color: AppColors.textPrimary,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: nameController,
                textInputAction: TextInputAction.next,
                decoration: const InputDecoration(
                  labelText: 'Имя',
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: surnameController,
                textInputAction: TextInputAction.done,
                decoration: const InputDecoration(
                  labelText: 'Фамилия',
                ),
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () async {
                    final name = nameController.text.trim();
                    final surname = surnameController.text.trim();

                    if (name.length < 2) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Имя должно быть не короче 2 символов'),
                        ),
                      );
                      return;
                    }

                    try {
                      final updated = await _userService.updateProfile(
                        name: name,
                        surname: surname,
                      );
                      if (!mounted) return;
                      if (updated != null) {
                        setState(() => _user = updated);
                      }
                      Navigator.of(context).pop();
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Профиль обновлён')),
                      );
                    } catch (e) {
                      if (!mounted) return;
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(getErrorMessage(e)),
                          backgroundColor: AppColors.error,
                        ),
                      );
                    }
                  },
                  child: const Text('Сохранить'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (!_hasCheckedInitialRefresh) {
      _hasCheckedInitialRefresh = true;
      final result = ModalRoute.of(context)?.settings.arguments;
      if (result is Map && result['refreshBookings'] == true) {
        _loadBookings();
      }
    } else {
      // Обновляем записи при возврате на экран (но не слишком часто)
      final now = DateTime.now();
      if (_lastBookingUpdate == null ||
          now.difference(_lastBookingUpdate!).inSeconds > 2) {
        _lastBookingUpdate = now;
        _loadBookings();
      }
    }
  }

  Future<void> _loadProfile() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    // Проверяем авторизацию
    if (!_authService.isAuthenticated) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _error = 'not_authenticated';
      });
      return;
    }

    try {
      final token = _authService.token;
      if (token != null) {
        _apiService.token = token;
      }

      final response = await _apiService.get('/auth/me');
      final user = User.fromJson(response);

      if (!mounted) return;

      setState(() {
        _user = user;
        _isLoading = false;
      });
      _userService.updateCachedUser(user);

      await Future.wait([
        _loadBookings(),
        _loadLoyalty(),
      ]);
    } catch (e) {
      if (!mounted) return;

      setState(() {
        _error = e.toString();
        _isLoading = false;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(getErrorMessage(e)),
          backgroundColor: AppColors.error,
          duration: const Duration(seconds: 4),
        ),
      );
    }
  }

  Future<void> _loadBookings() async {
    setState(() {
      _isLoadingBookings = true;
    });

    try {
      // Загружаем записи из API (если доступно)
      List<Booking> apiBookings = [];
      try {
        final token = _authService.token;
        if (token != null) {
          _apiService.token = token;
        }

        final response = await _apiService.get('/bookings');
        final List<dynamic> bookingsData = response is List
            ? response
            : (response['bookings'] as List<dynamic>? ?? []);

        apiBookings = bookingsData
            .where((json) => json is Map<String, dynamic>)
            .map((json) => Booking.fromJson(json as Map<String, dynamic>))
            .toList();
      } catch (e) {
        // Игнорируем ошибки API
      }

      // Загружаем локальные записи
      final localBookingsData = await _localBookingService.getLocalBookings();
      final localBookings =
          localBookingsData.map((json) => Booking.fromJson(json)).toList();

      // Объединяем записи
      final allBookings = [...apiBookings, ...localBookings];

      // Фильтруем отмененные записи
      final cancelledIds = await _localBookingService.getCancelledBookingIds();
      final filteredBookings = allBookings
          .where((booking) => !cancelledIds.contains(booking.id))
          .toList();

      if (!mounted) return;

      setState(() {
        _bookings = filteredBookings;
        _isLoadingBookings = false;
      });
    } catch (e) {
      if (!mounted) return;

      setState(() {
        _isLoadingBookings = false;
      });
    }
  }

  Future<void> _loadLoyalty() async {
    try {
      final info = await _loyaltyService.getLoyaltyInfo();
      if (!mounted) return;
      setState(() {
        _loyaltyInfo = info;
      });
    } catch (e) {
      // Игнорируем ошибки загрузки лояльности
    }
  }

  @override
  Widget build(BuildContext context) {
    return ConnectivityWrapper(
      onRetry: _loadProfile,
      child: Scaffold(
        backgroundColor: Colors.white,
        appBar: AppBar(
          backgroundColor: Colors.white,
          elevation: 0,
          automaticallyImplyLeading: false,
          centerTitle: true,
          title: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                'Профиль',
                style: AppTextStyles.heading3.copyWith(
                  fontWeight: FontWeight.w700,
                  color: AppColors.textPrimary,
                  fontSize: 22,
                ),
              ),
            ],
          ),
          toolbarHeight: 88,
        ),
        body: SafeArea(
          bottom: false,
          child: AnimatedStateSwitcher(
            child: _isLoading
                ? _buildSkeletonLoader()
                : _error != null
                    ? FadeInWidget(
                        child: _buildErrorState(),
                      )
                    : RefreshIndicator(
                        onRefresh: _loadProfile,
                        child: SingleChildScrollView(
                          physics: const AlwaysScrollableScrollPhysics(),
                          padding: const EdgeInsets.symmetric(horizontal: 20),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const SizedBox(height: 16),
                              _ProfileHeaderCard(
                                user: _user,
                                onEdit: _showEditProfileSheet,
                              ),
                              const SizedBox(height: 16),
                              _ContactInfoCard(),
                              const SizedBox(height: 16),
                              if (_loyaltyInfo != null)
                                _LoyaltyCard(loyaltyInfo: _loyaltyInfo!),
                              if (_loyaltyInfo != null)
                                const SizedBox(height: 24),
                              _UpcomingBookingsSection(
                                isLoading: _isLoadingBookings,
                                bookings: _bookings,
                                onBookingCancelled: () {
                                  _loadBookings();
                                },
                              ),
                              const SizedBox(height: 24),
                              _QuickLinks(
                                onSettings: () => Navigator.of(context)
                                    .pushNamed(RouteNames.settings),
                                onSupport: _openTechSupportTelegram,
                                onCallAdmin: () =>
                                    _openDialer(_adminSupportPhone),
                              ),
                              const SizedBox(height: 100),
                            ],
                          ),
                        ),
                      ),
          ),
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
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 16),
          const SkeletonProfileHeader(),
          const SizedBox(height: 16),
          // Skeleton для карточки лояльности
          const SkeletonCard(
            height: 120,
            borderRadius: BorderRadius.all(Radius.circular(24)),
          ),
          const SizedBox(height: 24),
          // Skeleton для заголовка "Предстоящие записи"
          const SkeletonText(width: 180, height: 24),
          const SizedBox(height: 12),
          // Skeleton для карточек записей
          const SkeletonBookingCard(),
          const SizedBox(height: 12),
          const SkeletonBookingCard(),
          const SizedBox(height: 24),
          // Skeleton для "Быстрые ссылки"
          const SkeletonText(width: 150, height: 20),
          const SizedBox(height: 12),
          const SkeletonCard(
            height: 64,
            borderRadius: BorderRadius.all(Radius.circular(18)),
          ),
          const SizedBox(height: 12),
          const SkeletonCard(
            height: 64,
            borderRadius: BorderRadius.all(Radius.circular(18)),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorState() {
    // Если пользователь не авторизован, показываем специальное сообщение
    if (_error == 'not_authenticated' || !_authService.isAuthenticated) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.person_outline,
                  size: 64, color: AppColors.textSecondary),
              const SizedBox(height: 16),
              Text(
                'Вам нужно войти',
                style: AppTextStyles.heading3
                    .copyWith(color: AppColors.textPrimary),
              ),
              const SizedBox(height: 8),
              Text(
                'Для доступа к профилю необходимо войти или зарегистрироваться',
                style: AppTextStyles.bodyMedium
                    .copyWith(color: AppColors.textSecondary),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () {
                  Navigator.of(context)
                      .pushReplacementNamed(RouteNames.registration);
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.buttonPrimary,
                  foregroundColor: Colors.white,
                  padding:
                      const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: Text(
                  'Войти или зарегистрироваться',
                  style: AppTextStyles.button.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
        ),
      );
    }

    // Обычная ошибка
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 64, color: AppColors.error),
            const SizedBox(height: 16),
            Text(
              'Ошибка загрузки профиля',
              style:
                  AppTextStyles.heading3.copyWith(color: AppColors.textPrimary),
            ),
            const SizedBox(height: 8),
            Text(
              _error ?? 'Попробуйте повторить позже',
              style: AppTextStyles.bodyMedium
                  .copyWith(color: AppColors.textSecondary),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: _loadProfile,
              child: const Text('Повторить'),
            ),
          ],
        ),
      ),
    );
  }
}

class _ContactInfoCard extends StatelessWidget {
  const _ContactInfoCard();

  Future<void> _launchUrl(String url) async {
    final uri = Uri.parse(url);
    try {
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      }
    } catch (e) {
      // Ошибка открытия URL
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFE5E5E5), width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.location_on_outlined,
                color: AppColors.buttonPrimary,
                size: 20,
              ),
              const SizedBox(width: 8),
              Text(
                'Адрес',
                style: AppTextStyles.heading4.copyWith(
                  fontWeight: FontWeight.w700,
                  color: AppColors.textPrimary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            'ул. Ключевская, д. 7, г. Петропавловск-Камчатский',
            style: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: 20),
          Text(
            'Мы в соцсетях',
            style: AppTextStyles.heading4.copyWith(
              fontWeight: FontWeight.w700,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              _SocialButton(
                icon: Icons.send_rounded,
                label: 'Telegram',
                color: AppColors.textSecondary,
                onTap: () => _launchUrl('https://t.me/priroda_kamchatka'),
              ),
              const SizedBox(width: 12),
              _SocialButton(
                icon: Icons.chat_bubble_rounded,
                label: 'WhatsApp',
                color: AppColors.textSecondary,
                onTap: () => _launchUrl('https://wa.me/79006870737'),
              ),
              const SizedBox(width: 12),
              _SocialButton(
                icon: Icons.group_rounded,
                label: 'ВКонтакте',
                color: AppColors.textSecondary,
                onTap: () => _launchUrl('https://vk.com/priroda_spa'),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _SocialButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _SocialButton({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(20),
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(
                color: AppColors.borderLight,
                width: 1,
              ),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.02),
                  blurRadius: 12,
                  offset: const Offset(0, 3),
                ),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        color.withOpacity(0.15),
                        color.withOpacity(0.05),
                      ],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: Icon(
                    icon,
                    color: color,
                    size: 24,
                  ),
                ),
                const SizedBox(height: 10),
                Text(
                  label,
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.textPrimary,
                    fontWeight: FontWeight.w600,
                    fontSize: 13,
                  ),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _ProfileHeaderCard extends StatelessWidget {
  final User? user;
  final VoidCallback onEdit;

  const _ProfileHeaderCard({
    required this.user,
    required this.onEdit,
  });

  @override
  Widget build(BuildContext context) {
    final avatarUrl = user?.avatarUrl;
    final resolved = avatarUrl != null && avatarUrl.isNotEmpty
        ? Helpers.resolveImageUrl(avatarUrl) ?? avatarUrl
        : null;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFE5E5E5), width: 1),
      ),
      child: Row(
        children: [
          Stack(
            clipBehavior: Clip.none,
            children: [
              Container(
                width: 72,
                height: 72,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border:
                      Border.all(color: const Color(0xFFFFC1CC), width: 2.5),
                ),
                child: ClipOval(
                  child: resolved != null && resolved.isNotEmpty
                      ? CachedNetworkImage(
                          imageUrl: resolved,
                          width: 72,
                          height: 72,
                          fit: BoxFit.cover,
                          cacheManager: SpaImageCacheManager.instance,
                          placeholder: (_, __) => Container(
                            color: AppColors.cardBackground,
                            child: Icon(
                              Icons.person,
                              color: AppColors.textSecondary,
                              size: 36,
                            ),
                          ),
                          errorWidget: (_, __, ___) => Container(
                            color: AppColors.cardBackground,
                            child: Icon(
                              Icons.person,
                              color: AppColors.textSecondary,
                              size: 36,
                            ),
                          ),
                        )
                      : Container(
                          color: AppColors.cardBackground,
                          child: Icon(
                            Icons.person,
                            color: AppColors.textSecondary,
                            size: 36,
                          ),
                        ),
                ),
              ),
              Positioned(
                right: -2,
                bottom: -2,
                child: Container(
                  width: 16,
                  height: 16,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: AppColors.success,
                    border: Border.all(color: Colors.white, width: 2),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        user?.fullName ?? 'Гость',
                        style: AppTextStyles.heading4.copyWith(
                          fontWeight: FontWeight.w700,
                          color: AppColors.textPrimary,
                        ),
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.edit_outlined),
                      color: AppColors.textSecondary,
                      onPressed: user == null ? null : onEdit,
                      tooltip: 'Редактировать',
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  user?.email ?? '',
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
                if (user?.uniqueCode != null) ...[
                  const SizedBox(height: 8),
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: AppColors.primaryWithOpacity10,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: AppColors.primary.withOpacity(0.3),
                        width: 1,
                      ),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          Icons.qr_code_2,
                          size: 16,
                          color: AppColors.primary,
                        ),
                        const SizedBox(width: 6),
                        Text(
                          'Код: ${user!.uniqueCode}',
                          style: AppTextStyles.bodySmall.copyWith(
                            color: AppColors.primary,
                            fontWeight: FontWeight.w600,
                            letterSpacing: 0.5,
                          ),
                        ),
                        const SizedBox(width: 4),
                        GestureDetector(
                          onTap: () {
                            final code = user?.uniqueCode;
                            if (code == null || code.isEmpty) {
                              return;
                            }
                            Clipboard.setData(ClipboardData(text: code));
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Код скопирован'),
                                duration: Duration(seconds: 1),
                              ),
                            );
                          },
                          child: Icon(
                            Icons.copy,
                            size: 14,
                            color: AppColors.primary.withOpacity(0.7),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _LoyaltyCard extends StatelessWidget {
  final LoyaltyInfo loyaltyInfo;

  const _LoyaltyCard({required this.loyaltyInfo});

  // Определить номер уровня на основе потраченных рублей (minBonuses - это рубли)
  int _getLevelNumber(int rubles) {
    if (rubles < 30000) return 1;
    if (rubles < 100000) return 2;
    if (rubles < 200000) return 3;
    return 4;
  }

  // Форматирование рублей
  String _formatRub(int amount) {
    final formatter = NumberFormat.decimalPattern('ru');
    return '${formatter.format(amount)} ₽';
  }

  // Получить градиент для уровня на основе цветов приложения
  LinearGradient _getLevelGradient(int levelNum) {
    switch (levelNum) {
      case 1:
        return LinearGradient(
          colors: [AppColors.primary, AppColors.primaryLight],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        );
      case 2:
        return LinearGradient(
          colors: [AppColors.primaryLight, AppColors.primary],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        );
      case 3:
        return LinearGradient(
          colors: [AppColors.primary, AppColors.primaryDark],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        );
      case 4:
        return LinearGradient(
          colors: [AppColors.primaryDark, AppColors.primaryDarker],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        );
      default:
        return LinearGradient(
          colors: [AppColors.primary, AppColors.primaryLight],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        );
    }
  }

  Color _parseColor(String hex) {
    try {
      return Color(
          int.parse(hex.replaceFirst('#', ''), radix: 16) + 0xFF000000);
    } catch (e) {
      return AppColors.buttonPrimary;
    }
  }

  @override
  Widget build(BuildContext context) {
    final currentLevel = loyaltyInfo.currentLevel;
    final nextLevel = loyaltyInfo.nextLevel;
    final currentBonuses = loyaltyInfo.currentBonuses;

    if (currentLevel == null) {
      return const SizedBox.shrink();
    }

    // Используем данные из бэкенда (уже рассчитаны по потраченным рублям)
    final bonusesToNext =
        loyaltyInfo.bonusesToNext; // Это рубли до следующего уровня
    final progress = loyaltyInfo.progress;
    final levelName = currentLevel.name;

    // Определяем номер уровня из имени (0, 1, 2, 3, 4) или по minBonuses
    final levelNum =
        int.tryParse(levelName) ?? _getLevelNumber(currentLevel.minBonuses);

    String statusText = 'Уровень $levelName';
    String subtitleText = '';

    if (nextLevel != null && bonusesToNext > 0) {
      subtitleText =
          'Потратить ещё ${_formatRub(bonusesToNext)} до Уровня ${nextLevel.name}';
    } else if (nextLevel == null) {
      subtitleText = 'Вы на максимальном уровне';
    } else {
      subtitleText = 'Максимальный уровень достигнут';
    }

    if (currentLevel == null) {
      return const SizedBox.shrink();
    }

    // Используем цвета из AppColors для градиента
    final gradient = _getLevelGradient(levelNum);

    return GestureDetector(
      onTap: () => Navigator.of(context).pushNamed(RouteNames.loyalty),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          gradient: gradient,
          borderRadius: BorderRadius.circular(24),
          boxShadow: [
            BoxShadow(
              color: AppColors.buttonPrimary.withOpacity(0.35),
              blurRadius: 40,
              offset: const Offset(0, 20),
            ),
          ],
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Ваш уровень лояльности:',
                    style: AppTextStyles.bodyMedium.copyWith(
                      color: Colors.white.withOpacity(0.8),
                      fontWeight: FontWeight.w400,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    statusText,
                    style: AppTextStyles.heading3.copyWith(
                      color: Colors.white,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'Бонусы: $currentBonuses',
                    style: AppTextStyles.bodyMedium.copyWith(
                      color: Colors.white.withOpacity(0.9),
                      fontWeight: FontWeight.w400,
                    ),
                  ),
                  const SizedBox(height: 12),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(999),
                    child: LinearProgressIndicator(
                      value: progress,
                      minHeight: 8,
                      backgroundColor: Colors.white.withOpacity(0.25),
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    subtitleText,
                    style: AppTextStyles.bodySmall.copyWith(
                      color: Colors.white.withOpacity(0.9),
                      fontWeight: FontWeight.w400,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 8),
            const Icon(
              Icons.chevron_right,
              color: Color(0xFFBDBDBD),
              size: 24,
            ),
          ],
        ),
      ),
    );
  }
}

class _UpcomingBookingsSection extends StatefulWidget {
  final bool isLoading;
  final List<Booking> bookings;
  final VoidCallback? onBookingCancelled;

  const _UpcomingBookingsSection({
    required this.isLoading,
    required this.bookings,
    this.onBookingCancelled,
  });

  @override
  State<_UpcomingBookingsSection> createState() =>
      _UpcomingBookingsSectionState();
}

class _UpcomingBookingsSectionState extends State<_UpcomingBookingsSection> {
  final _apiService = ApiService();
  final _authService = AuthService();
  final _localBookingService = LocalBookingService();

  String _formatDateTime(DateTime dateTime) {
    final months = [
      'января',
      'февраля',
      'марта',
      'апреля',
      'мая',
      'июня',
      'июля',
      'августа',
      'сентября',
      'октября',
      'ноября',
      'декабря',
    ];
    return '${dateTime.day} ${months[dateTime.month - 1]} в ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
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

      // Вызываем callback для обновления списка
      widget.onBookingCancelled?.call();
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

  @override
  Widget build(BuildContext context) {
    final futureBookings = widget.bookings
        .where((b) =>
            b.appointmentDateTime.isAfter(DateTime.now()) &&
            b.status != 'cancelled' &&
            b.status != 'completed')
        .toList()
      ..sort((a, b) => a.appointmentDateTime.compareTo(b.appointmentDateTime));

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            GestureDetector(
              onTap: () {
                if (!widget.isLoading) {
                  Navigator.of(context).pushNamed(RouteNames.bookings);
                }
              },
              child: Text(
                'Предстоящие записи',
                style: AppTextStyles.heading2.copyWith(
                  fontWeight: FontWeight.w700,
                  color: AppColors.textPrimary,
                  fontSize: 24,
                ),
              ),
            ),
            if (!widget.isLoading && futureBookings.isNotEmpty)
              TextButton(
                onPressed: () {
                  Navigator.of(context).pushNamed(RouteNames.bookings);
                },
                style: TextButton.styleFrom(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  minimumSize: Size.zero,
                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      'Все',
                      style: AppTextStyles.bodyMedium.copyWith(
                        color: AppColors.buttonPrimary,
                        fontWeight: FontWeight.w600,
                        fontSize: 14,
                      ),
                    ),
                    const SizedBox(width: 4),
                    Icon(
                      Icons.arrow_forward_ios,
                      size: 12,
                      color: AppColors.buttonPrimary,
                    ),
                  ],
                ),
              ),
          ],
        ),
        const SizedBox(height: 12),
        if (widget.isLoading)
          const Center(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: CircularProgressIndicator(),
            ),
          )
        else if (futureBookings.isEmpty)
          const CompactEmptyState(
            message: 'Нет ближайших записей',
          )
        else
          AnimatedListWidget(
            children: futureBookings.take(2).map((booking) {
              return Material(
                color: Colors.transparent,
                child: InkWell(
                  borderRadius: BorderRadius.circular(18),
                  onTap: () {
                    Navigator.of(context).pushNamed(RouteNames.bookings);
                  },
                  child: Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.symmetric(
                        horizontal: 16, vertical: 14),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF7F7F2),
                      borderRadius: BorderRadius.circular(18),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.03),
                          blurRadius: 8,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                    child: Row(
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                booking.serviceName,
                                style: AppTextStyles.bodyLarge.copyWith(
                                  fontWeight: FontWeight.w600,
                                  color: AppColors.textPrimary,
                                  fontSize: 16,
                                ),
                              ),
                              if (booking.masterName != null &&
                                  booking.masterName!.isNotEmpty) ...[
                                const SizedBox(height: 4),
                                Row(
                                  children: [
                                    Icon(
                                      Icons.person_outline,
                                      size: 14,
                                      color: AppColors.textSecondary,
                                    ),
                                    const SizedBox(width: 6),
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
                              const SizedBox(height: 6),
                              Text(
                                _formatDateTime(booking.appointmentDateTime),
                                style: AppTextStyles.bodyMedium.copyWith(
                                  color: AppColors.textSecondary,
                                  fontSize: 14,
                                ),
                              ),
                            ],
                          ),
                        ),
                        if (booking.canCancel) ...[
                          TextButton(
                            onPressed: () => _cancelBooking(booking),
                            style: TextButton.styleFrom(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 12, vertical: 8),
                              minimumSize: Size.zero,
                              tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                            ),
                            child: Text(
                              'Отменить',
                              style: AppTextStyles.bodySmall.copyWith(
                                color: AppColors.error,
                                fontWeight: FontWeight.w600,
                                fontSize: 12,
                              ),
                            ),
                          ),
                          const SizedBox(width: 4),
                        ],
                        const Icon(
                          Icons.chevron_right,
                          color: AppColors.textPrimary,
                          size: 24,
                        ),
                      ],
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
      ],
    );
  }
}

class _QuickLinks extends StatelessWidget {
  final VoidCallback onSettings;
  final VoidCallback onSupport;
  final VoidCallback onCallAdmin;

  const _QuickLinks({
    required this.onSettings,
    required this.onSupport,
    required this.onCallAdmin,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Быстрые ссылки',
          style: AppTextStyles.heading2.copyWith(
            fontWeight: FontWeight.w700,
            color: AppColors.textPrimary,
            fontSize: 24,
          ),
        ),
        const SizedBox(height: 12),
        _QuickLinkTile(
          icon: Icons.settings_outlined,
          title: 'Настройки',
          onTap: onSettings,
        ),
        const SizedBox(height: 12),
        _QuickLinkTile(
          icon: Icons.history,
          title: 'Прошедшие записи',
          onTap: () => Navigator.of(context).pushNamed(RouteNames.pastBookings),
        ),
        const SizedBox(height: 12),
        _QuickLinkTile(
          icon: Icons.help_outline,
          title: 'Тех поддержка',
          subtitle: '@priroda_spa в Telegram',
          onTap: onSupport,
        ),
        const SizedBox(height: 12),
        _QuickLinkTile(
          icon: Icons.call_outlined,
          title: 'Позвонить в администрацию',
          subtitle: '+7 900 687-07-37',
          onTap: onCallAdmin,
        ),
      ],
    );
  }
}

class _QuickLinkTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final String? subtitle;
  final VoidCallback onTap;

  const _QuickLinkTile({
    required this.icon,
    required this.title,
    this.subtitle,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: const Color(0xFFF7F7F2),
      borderRadius: BorderRadius.circular(18),
      child: InkWell(
        borderRadius: BorderRadius.circular(18),
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          decoration: BoxDecoration(
            color: const Color(0xFFF7F7F2),
            borderRadius: BorderRadius.circular(18),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.03),
                blurRadius: 8,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Row(
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: AppColors.buttonPrimary.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(
                  icon,
                  color: AppColors.buttonPrimary,
                  size: 22,
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
                      style: AppTextStyles.bodyLarge.copyWith(
                        color: AppColors.textPrimary,
                        fontWeight: FontWeight.w500,
                        fontSize: 16,
                      ),
                    ),
                    if (subtitle != null) ...[
                      const SizedBox(height: 2),
                      Text(
                        subtitle!,
                        style: AppTextStyles.bodySmall.copyWith(
                          color: AppColors.textSecondary,
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              const SizedBox(width: 8),
              const Icon(
                Icons.chevron_right,
                color: AppColors.textPrimary,
                size: 24,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

String _formatDateTime(DateTime dateTime) {
  final months = [
    'января',
    'февраля',
    'марта',
    'апреля',
    'мая',
    'июня',
    'июля',
    'августа',
    'сентября',
    'октября',
    'ноября',
    'декабря',
  ];
  return '${dateTime.day} ${months[dateTime.month - 1]} в '
      '${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
}
