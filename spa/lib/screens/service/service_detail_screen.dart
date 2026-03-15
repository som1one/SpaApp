import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../services/image_cache_manager.dart';

import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../services/api_service.dart';
import '../../services/auth_service.dart';
import '../../models/service.dart';
import '../../routes/route_names.dart';
import '../../utils/helpers.dart';

class ServiceDetailScreen extends StatefulWidget {
  final int serviceId;

  const ServiceDetailScreen({
    super.key,
    required this.serviceId,
  });

  @override
  State<ServiceDetailScreen> createState() => _ServiceDetailScreenState();
}

class _ServiceDetailScreenState extends State<ServiceDetailScreen> {
  final _apiService = ApiService();
  final _authService = AuthService();
  Service? _service;
  bool _isLoading = true;
  String? _error;
  bool _isFavorite = false;

  @override
  void initState() {
    super.initState();
    _loadService();
  }

  Future<void> _loadService() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final token = _authService.token;
      if (token != null) {
        _apiService.token = token;
      }

      final response = await _apiService.get('/services/${widget.serviceId}');
      Service service;
      if (response is Map) {
        service = Service.fromJson(Map<String, dynamic>.from(response as Map));
      } else {
        throw Exception('Неверный формат ответа от сервера');
      }

      if (!mounted) return;

      setState(() {
        _service = service;
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;

      setState(() {
        _error = e.toString();
        _isLoading = false;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Ошибка загрузки услуги: ${e.toString()}'),
          backgroundColor: AppColors.error,
        ),
      );
    }
  }

  Future<void> _handleQuickBooking() async {
    if (_service == null) return;
    
    // Если услуга привязана к YClients, используем YClients виджет
    if (_service!.yclientsServiceId != null) {
      Navigator.of(context).pushNamed(
        RouteNames.yclientsBooking,
        arguments: {
          'serviceId': _service!.id,
          'service': _service!.toJson(),
        },
      );
    } else {
      // Иначе используем обычный booking flow
      Navigator.of(context).pushNamed(
        RouteNames.masterSelection,
        arguments: {
          'serviceId': _service!.id,
          'service': _service,
        },
      );
    }
  }

  void _handleShare() {
    if (_service == null) return;
    
    // TODO: Реализация шаринга
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Поделиться услугой'),
      ),
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
            Icons.arrow_back,
            color: AppColors.textPrimary,
          ),
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Text(
          _service?.name ?? 'Детали услуги',
          style: AppTextStyles.heading4.copyWith(
            color: AppColors.textPrimary,
            fontWeight: FontWeight.w700,
          ),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: Icon(
              _isFavorite ? Icons.favorite : Icons.favorite_border,
              color: _isFavorite ? Colors.red : AppColors.textPrimary,
            ),
            onPressed: () {
              setState(() {
                _isFavorite = !_isFavorite;
              });
            },
          ),
          IconButton(
            icon: const Icon(
              Icons.share,
              color: AppColors.textPrimary,
            ),
            onPressed: _handleShare,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(),
            )
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
                        'Ошибка загрузки услуги',
                        style: AppTextStyles.heading3.copyWith(
                          color: AppColors.textPrimary,
                        ),
                      ),
                      const SizedBox(height: 8),
                      if (_error != null)
                        Text(
                          _error!,
                          style: AppTextStyles.bodyMedium.copyWith(
                            color: AppColors.textSecondary,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      const SizedBox(height: 24),
                      ElevatedButton(
                        onPressed: _loadService,
                        child: const Text('Повторить'),
                      ),
                    ],
                  ),
                )
              : _buildContent(),
    );
  }

  Widget _buildContent() {
    if (_service == null) return const SizedBox.shrink();

    return Stack(
      children: [
        SingleChildScrollView(
          padding: const EdgeInsets.only(bottom: 100),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildHeroImage(),
              _buildDescriptionSection(),
            ],
          ),
        ),
        // Кнопка быстрого бронирования (fixed внизу)
        Positioned(
          bottom: 0,
          left: 0,
          right: 0,
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 10,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
              child: SafeArea(
                child: SizedBox(
                  width: double.infinity,
                  height: 56,
                  child: ElevatedButton(
                    onPressed: _handleQuickBooking,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.buttonPrimary,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                      elevation: 2,
                      shadowColor: AppColors.buttonPrimary.withOpacity(0.2),
                    ),
                    child: Text(
                      _service?.bookButtonLabel ?? 'Записаться',
                      style: AppTextStyles.bodyLarge.copyWith(
                        fontFamily: 'Inter24',
                        color: Colors.white,
                        fontWeight: FontWeight.w600,
                        fontSize: 16,
                        letterSpacing: 0.1,
                      ),
                    ),
                  ),
                ),
              ),
          ),
        ),
      ],
    );
  }

  Widget _buildHeroImage() {
    return Stack(
      children: [
        // Изображение
        SizedBox(
          width: double.infinity,
          height: 320,
          child: Builder(builder: (context) {
            final rawUrl = _service!.detailImageUrl?.isNotEmpty == true
                ? _service!.detailImageUrl!
                : _service!.imageUrl;
            final imageUrl = Helpers.resolveImageUrl(rawUrl) ?? rawUrl;
            if (imageUrl != null && imageUrl.isNotEmpty) {
              return CachedNetworkImage(
                imageUrl: imageUrl,
                fit: BoxFit.cover,
                cacheManager: SpaImageCacheManager.instance,
                placeholder: (_, __) => const Center(
                  child: SizedBox(
                    width: 24,
                    height: 24,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                ),
                errorWidget: (_, __, ___) => Container(
                  color: AppColors.cardBackground,
                  child: Center(
                    child: Icon(Icons.image, size: 64, color: AppColors.textMuted),
                  ),
                ),
              );
            }
            return Container(
              color: AppColors.cardBackground,
              child: Center(
                child: Icon(Icons.image, size: 64, color: AppColors.textMuted),
              ),
            );
          }),
        ),
        Positioned(
          bottom: 0,
          left: 0,
          right: 0,
          child: Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  Colors.transparent,
                  Colors.black.withOpacity(0.85),
                ],
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _service!.name,
                  style: AppTextStyles.heading2.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                if (_service!.subtitle != null && _service!.subtitle!.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(top: 6),
                    child: Text(
                      _service!.subtitle!,
                      style: AppTextStyles.bodyLarge.copyWith(
                        color: Colors.white.withOpacity(0.9),
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildDescriptionSection() {
    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (_service?.highlights?.isNotEmpty ?? false) ...[
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: (_service!.highlights ?? [])
                  .map(
                    (item) => Container(
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(999),
                        color: AppColors.cardBackground,
                      ),
                      child: Text(
                        item,
                        style: AppTextStyles.bodySmall.copyWith(
                          color: AppColors.textSecondary,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  )
                  .toList(),
            ),
            const SizedBox(height: 20),
          ],
          Text(
            'Описание',
            style: AppTextStyles.heading3.copyWith(
              color: AppColors.textPrimary,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            _service!.description ?? 'Описание отсутствует',
            style: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.textPrimary,
              height: 1.5,
            ),
          ),
          const SizedBox(height: 24),
          _buildPriceCard(),
          const SizedBox(height: 24),
          _buildAdditionalServices(),
          const SizedBox(height: 120),
        ],
      ),
    );
  }

  Widget _buildPriceCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.cardBackground,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Цена',
                style: AppTextStyles.bodyLarge.copyWith(
                  color: AppColors.textPrimary,
                  fontWeight: FontWeight.bold,
                ),
              ),
              if (_service!.duration != null) ...[
                const SizedBox(height: 4),
                Text(
                  '${_service!.duration} минут',
                  style: AppTextStyles.bodySmall.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ],
          ),
          if (_service!.price != null)
            Text(
              '${_service!.price!.toStringAsFixed(0)} ₽',
              style: AppTextStyles.heading2.copyWith(
                color: AppColors.buttonPrimary,
                fontWeight: FontWeight.bold,
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildAdditionalServices() {
    final additionalServices = _service?.additionalServices ?? [];
    if (additionalServices.isEmpty) return const SizedBox.shrink();

    IconData getIcon(String name) {
      final lowerName = name.toLowerCase();
      if (lowerName.contains('кам')) return Icons.wb_twilight;
      if (lowerName.contains('рефлекс') || lowerName.contains('стоп')) return Icons.directions_walk;
      if (lowerName.contains('голов') || lowerName.contains('head')) return Icons.self_improvement;
      return Icons.spa;
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Дополнительные услуги',
          style: AppTextStyles.heading3.copyWith(
            color: AppColors.textPrimary,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: additionalServices.map((item) {
            final name = item['name'] as String? ?? item.toString();
            return Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: BoxDecoration(
                color: AppColors.cardBackground,
                borderRadius: BorderRadius.circular(24),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(getIcon(name), size: 18, color: AppColors.textSecondary),
                  const SizedBox(width: 8),
                  Text(
                    name,
                    style: AppTextStyles.bodySmall.copyWith(color: AppColors.textPrimary),
                  ),
                ],
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  @override
  void dispose() {
    super.dispose();
  }
}

