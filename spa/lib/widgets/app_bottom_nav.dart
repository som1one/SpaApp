import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

import '../routes/route_names.dart';
import '../theme/app_colors.dart';

enum BottomNavItem { home, menu, loyalty, profile }

class AppBottomNav extends StatelessWidget {
  final BottomNavItem current;

  const AppBottomNav({
    super.key,
    required this.current,
  });

  @override
  Widget build(BuildContext context) {
    final items = [
      _BottomNavConfig(
        item: BottomNavItem.home,
        label: 'Главная',
        assetPath: 'assets/images/Navigation/home_page.svg',
        routeName: RouteNames.home,
      ),
      _BottomNavConfig(
        item: BottomNavItem.menu,
        label: 'Меню',
        assetPath: 'assets/images/Navigation/menu_page.svg',
        routeName: RouteNames.menuSpa,
      ),
      // Новый пункт навигации для программы лояльности между меню и профилем
      _BottomNavConfig(
        item: BottomNavItem.loyalty,
        label: 'Лояльность',
        assetPath: 'assets/images/Navigation/booking_page.svg',
        routeName: RouteNames.loyalty,
      ),
      _BottomNavConfig(
        item: BottomNavItem.profile,
        label: 'Профиль',
        assetPath: 'assets/images/Navigation/profile_page.svg',
        routeName: RouteNames.profile,
      ),
    ];

    return SafeArea(
      top: false,
      child: Container(
        height: 68,
        decoration: BoxDecoration(
          color: AppColors.backgroundLight, // Цвет бренда #F7F6F2
          border: Border(
            top: BorderSide(
              color: AppColors.borderLight,
              width: 1,
            ),
          ),
          boxShadow: [
            BoxShadow(
              color: AppColors.shadowLight,
              blurRadius: 8,
              offset: const Offset(0, -2),
            ),
          ],
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: items.map((config) {
            final isSelected = config.item == current;
            return Expanded(
              child: Material(
                color: Colors.transparent,
                child: InkWell(
                  onTap: () => _handleTap(context, config),
                  borderRadius: BorderRadius.circular(16),
                  child: RepaintBoundary(
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 200),
                      curve: Curves.easeOutCubic,
                      margin: const EdgeInsets.symmetric(vertical: 4, horizontal: 2),
                      padding: const EdgeInsets.symmetric(vertical: 4, horizontal: 6),
                      decoration: BoxDecoration(
                        color: isSelected
                            ? AppColors.buttonPrimary.withOpacity(0.15)
                            : Colors.transparent,
                        borderRadius: BorderRadius.circular(16),
                      ),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        Container(
                          padding: const EdgeInsets.all(5),
                          decoration: BoxDecoration(
                            color: isSelected
                                ? AppColors.buttonPrimary.withOpacity(0.1)
                                : Colors.transparent,
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: SvgPicture.asset(
                            config.assetPath,
                            width: 20,
                            height: 20,
                            colorFilter: ColorFilter.mode(
                              isSelected
                                  ? AppColors.buttonPrimary
                                  : const Color(0xFF9E9E9E),
                              BlendMode.srcIn,
                            ),
                            placeholderBuilder: (BuildContext context) => SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: isSelected
                                    ? AppColors.buttonPrimary
                                    : const Color(0xFF9E9E9E),
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          config.label,
                          style: TextStyle(
                            fontFamily: 'Inter18',
                            fontSize: 10,
                            height: 1.1,
                            fontWeight:
                                isSelected ? FontWeight.w600 : FontWeight.w400,
                            color: isSelected
                                ? AppColors.buttonPrimary
                                : AppColors.textMuted,
                            letterSpacing: -0.2,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                    ),
                  ),
                ),
              ),
            );
          }).toList(),
        ),
      ),
    );
  }

  void _handleTap(BuildContext context, _BottomNavConfig config) {
    if (config.item == current) return;

    switch (config.item) {
      case BottomNavItem.home:
        Navigator.of(context).pushNamedAndRemoveUntil(
          RouteNames.home,
          (route) => route.isFirst,
        );
        break;
      case BottomNavItem.menu:
        Navigator.of(context).pushNamedAndRemoveUntil(
          RouteNames.menuSpa,
          (route) => route.isFirst,
        );
        break;
      case BottomNavItem.loyalty:
        Navigator.of(context).pushNamedAndRemoveUntil(
          RouteNames.loyalty,
          (route) => route.isFirst,
        );
        break;
      case BottomNavItem.profile:
        Navigator.of(context).pushNamedAndRemoveUntil(
          RouteNames.profile,
          (route) => route.isFirst,
        );
        break;
    }
  }
}

class _BottomNavConfig {
  final BottomNavItem item;
  final String label;
  final String assetPath;
  final String routeName;

  _BottomNavConfig({
    required this.item,
    required this.label,
    required this.assetPath,
    required this.routeName,
  });
}


