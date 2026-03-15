import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';

class AppLoadingScreen extends StatefulWidget {
  final String? subtitle;

  const AppLoadingScreen({super.key, this.subtitle});

  @override
  State<AppLoadingScreen> createState() => _AppLoadingScreenState();
}

class _AppLoadingScreenState extends State<AppLoadingScreen>
    with SingleTickerProviderStateMixin {
  static const _dotDelays = [0.0, 0.18, 0.36];

  late final AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1800),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  double _pulseScale() {
    final progress = _controller.value;
    return 0.92 + 0.12 * math.sin(progress * 2 * math.pi);
  }

  double _dotTranslation(double delay) {
    final progress = (_controller.value + delay) % 1;
    return math.sin(progress * 2 * math.pi).clamp(0, 1);
  }

  @override
  Widget build(BuildContext context) {
    final caption = widget.subtitle ?? 'Подготавливаем вашу SPA-трансформацию';

    return AbsorbPointer(
      absorbing: true,
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Colors.white,
              AppColors.offWhite.withOpacity(0.3),
            ],
          ),
        ),
        child: Center(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                        // Логотип с листьями
                        AnimatedBuilder(
                  animation: _controller,
                  builder: (_, __) {
                    return Transform.scale(
                      scale: _pulseScale(),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          // SVG листья (стилизованно)
                          Container(
                            height: 80,
                            width: 120,
                            decoration: BoxDecoration(
                              color: AppColors.primary,
                              borderRadius: const BorderRadius.only(
                                topLeft: Radius.elliptical(60, 40),
                                topRight: Radius.elliptical(60, 40),
                                bottomLeft: Radius.elliptical(60, 40),
                                bottomRight: Radius.elliptical(60, 40),
                              ),
                              boxShadow: [
                                BoxShadow(
                                  color: AppColors.primary.withOpacity(0.25),
                                  blurRadius: 24,
                                  offset: const Offset(0, 12),
                                ),
                              ],
                            ),
                            child: Center(
                              child: Icon(
                                Icons.spa_outlined,
                                size: 50,
                                color: AppColors.white.withOpacity(0.9),
                              ),
                            ),
                          ),
                          const SizedBox(height: 24),
                          // Текст PRIRODA SPA
                          Text(
                            'PRIRODA  SPA',
                            style: AppTextStyles.heading2.copyWith(
                              color: AppColors.textPrimary,
                              fontSize: 26,
                              letterSpacing: 2,
                              fontWeight: FontWeight.w300,
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
                const SizedBox(height: 42),
                SizedBox(
                  height: 10,
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: List.generate(_dotDelays.length, (index) {
                      final translation = _dotTranslation(_dotDelays[index]);
                      return Transform.translate(
                        offset: Offset(0, -translation * 12),
                        child: Container(
                          width: 12,
                          height: 12,
                          margin: const EdgeInsets.symmetric(horizontal: 6),
                          decoration: BoxDecoration(
                            color: AppColors.primaryDarker,
                            borderRadius: BorderRadius.circular(6),
                          ),
                        ),
                      );
                    }),
                  ),
                ),
                const SizedBox(height: 22),
                ClipRRect(
                  borderRadius: BorderRadius.circular(3),
                  child: LinearProgressIndicator(
                    minHeight: 5,
                    valueColor: const AlwaysStoppedAnimation(AppColors.primary),
                    backgroundColor: AppColors.primaryWithOpacity15,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  caption,
                  style: AppTextStyles.bodySmall.copyWith(
                    color: AppColors.textSecondary,
                    letterSpacing: 0.4,
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

