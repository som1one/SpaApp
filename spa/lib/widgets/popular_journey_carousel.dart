import 'dart:async';

import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:url_launcher/url_launcher.dart';

import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';

class PopularJourneyCarousel extends StatefulWidget {
  final List<PopularJourneyItem>? items;

  const PopularJourneyCarousel({
    super.key,
    this.items,
  });

  @override
  State<PopularJourneyCarousel> createState() => _PopularJourneyCarouselState();
}

class _PopularJourneyCarouselState extends State<PopularJourneyCarousel> {
  final PageController _controller = PageController(viewportFraction: 0.82);
  int _currentPage = 0;
  Timer? _autoSlideTimer;

  late final List<PopularJourneyItem> _journeys = widget.items?.isNotEmpty ==
          true
      ? widget.items!
      : const [
          PopularJourneyItem(
            imageAssetPath: 'assets/images/Home/IMG_2918.png',
            title: 'Клубная карта WELLNESS PRIRODA',
            subtitle:
                'Привилегии и специальные предложения для постоянных гостей.',
            url: 'https://prirodaspa.ru/abonement-offer',
          ),
          PopularJourneyItem(
            imageAssetPath: 'assets/images/Home/IMG2919.png',
            title: 'Спа-терапия, зашитая в отдых',
            subtitle:
                'Комплексные программы для полного восстановления и релакса.',
            url: 'https://prirodaspa.ru/spa-program',
          ),
          PopularJourneyItem(
            imageAssetPath: 'assets/images/Home/IMG2928.png',
            title: 'Конструктор спа-программы',
            subtitle: 'Создайте индивидуальную программу под ваши потребности.',
            url: 'https://prirodaspa.ru/contructor',
          ),
        ];

  @override
  void dispose() {
    _autoSlideTimer?.cancel();
    _controller.dispose();
    super.dispose();
  }

  @override
  void initState() {
    super.initState();
    _startAutoSlide();
  }

  void _startAutoSlide() {
    _autoSlideTimer?.cancel();
    _autoSlideTimer = Timer.periodic(const Duration(seconds: 4), (_) {
      if (!mounted || _journeys.isEmpty) return;
      int nextPage = (_currentPage + 1) % _journeys.length;
      _controller.animateToPage(
        nextPage,
        duration: const Duration(milliseconds: 500),
        // Используем более плавную кривую для 120 Гц
        curve: Curves.easeInOutCubic,
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 28),
          child: Text(
            'Спа-терапия',
            style: AppTextStyles.heading3.copyWith(
              fontFamily: 'Inter24',
              fontSize: 20,
              height: 28 / 20,
              fontWeight: FontWeight.w700,
              color: AppColors.textPrimary,
              letterSpacing: -0.3,
            ),
          ),
        ),
        const SizedBox(height: 16),
        SizedBox(
          height: 240,
          child: PageView.builder(
            controller: _controller,
            itemCount: _journeys.length,
            // Используем более плавную физику для 120 Гц
            physics: const ClampingScrollPhysics(
              parent: BouncingScrollPhysics(),
            ),
            onPageChanged: (index) {
              setState(() => _currentPage = index);
              _startAutoSlide();
            },
            itemBuilder: (context, index) {
              final journey = _journeys[index];
              return RepaintBoundary(
                child: Padding(
                  padding: EdgeInsets.only(
                    left: index == 0 ? 8 : 4,
                    right: index == _journeys.length - 1 ? 8 : 4,
                  ),
                  child: _JourneyCard(data: journey),
                ),
              );
            },
          ),
        ),
        const SizedBox(height: 16),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: List.generate(
            _journeys.length,
            (index) => RepaintBoundary(
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 300),
                curve: Curves.easeOutCubic,
                margin: const EdgeInsets.symmetric(horizontal: 4),
                width: _currentPage == index ? 18 : 8,
                height: 8,
                decoration: BoxDecoration(
                  color: _currentPage == index
                      ? AppColors.buttonPrimary
                      : AppColors.buttonPrimary.withOpacity(0.25),
                  borderRadius: BorderRadius.circular(999),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class _JourneyCardData {
  final String title;
  final String subtitle;
  final String? url;
  final String? imageUrl;
  final String? imageAssetPath;

  const _JourneyCardData({
    required this.title,
    required this.subtitle,
    this.url,
    this.imageUrl,
    this.imageAssetPath,
  });
}

class _JourneyCard extends StatelessWidget {
  final _JourneyCardData data;

  const _JourneyCard({required this.data});

  Future<void> _openUrl(String? url) async {
    if (url == null || url.isEmpty) return;
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  @override
  Widget build(BuildContext context) {
    final isNetworkImage = data.imageUrl != null && data.imageUrl!.isNotEmpty;
    return RepaintBoundary(
      child: GestureDetector(
        onTap: () => _openUrl(data.url),
        child: Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(24),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.08),
                blurRadius: 20,
                offset: const Offset(0, 6),
              ),
            ],
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(24),
            child: Stack(
              fit: StackFit.expand,
              children: [
                if (isNetworkImage)
                  CachedNetworkImage(
                    imageUrl: data.imageUrl!,
                    fit: BoxFit.cover,
                    placeholder: (_, __) => Container(
                      color: AppColors.buttonPrimary.withOpacity(0.08),
                    ),
                    errorWidget: (_, __, ___) => Container(
                      color: AppColors.buttonPrimary.withOpacity(0.08),
                      alignment: Alignment.center,
                      child: Icon(
                        Icons.image_not_supported_outlined,
                        color: Colors.black.withOpacity(0.25),
                      ),
                    ),
                  )
                else
                  Image.asset(
                    data.imageAssetPath ?? 'assets/images/Home/IMG_2918.png',
                    fit: BoxFit.cover,
                    // Кешируем изображение для плавности
                    cacheWidth: (MediaQuery.of(context).size.width *
                            0.82 *
                            MediaQuery.of(context).devicePixelRatio)
                        .round(),
                  ),
                Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: [
                        Colors.black.withOpacity(0),
                        Colors.black.withOpacity(0.65),
                      ],
                    ),
                  ),
                ),
                Positioned(
                  left: 20,
                  right: 20,
                  bottom: 24,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        data.title,
                        style: AppTextStyles.heading3.copyWith(
                          fontFamily: 'Inter24',
                          fontSize: 22,
                          height: 28 / 22,
                          fontWeight: FontWeight.w700,
                          color: Colors.white,
                          letterSpacing: -0.3,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        data.subtitle,
                        style: AppTextStyles.bodyMedium.copyWith(
                          fontFamily: 'Inter18',
                          fontSize: 14,
                          height: 20 / 14,
                          color: Colors.white.withOpacity(0.85),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class PopularJourneyItem extends _JourneyCardData {
  const PopularJourneyItem({
    required super.title,
    required super.subtitle,
    super.url,
    super.imageUrl,
    super.imageAssetPath,
  });
}
