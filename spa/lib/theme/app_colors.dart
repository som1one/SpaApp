import 'package:flutter/material.dart';

class AppColors {
  // Основные цвета бренда
  // Основной зеленый: #5A7C4A (RGB: 90, 124, 74)
  static const Color primary = Color(0xFF5A7C4A);
  
  // Вариации основного зеленого
  static const Color primaryLight = Color(0xFF7A9C6A); // Более светлый оттенок
  static const Color primaryLighter = Color(0xFF9ABC8A); // Еще светлее
  static const Color primaryDark = Color(0xFF4A6C3A); // Темнее
  static const Color primaryDarker = Color(0xFF3A5C2A); // Еще темнее
  
  // Нейтральные цвета бренда
  static const Color white = Color(0xFFFFFFFF); // #FFFFFF
  static const Color offWhite = Color(0xFFF7F6F2); // #F7F6F2 (RGB: 247, 246, 242)
  static const Color darkGrey = Color(0xFF383838); // #383838 (RGB: 56, 56, 56)
  
  // Цвета для кнопок
  static const Color buttonPrimary = primary; // #5A7C4A
  static const Color buttonPrimaryHover = primaryDark; // Темнее при наведении
  static const Color buttonPrimaryPressed = primaryDarker; // Еще темнее при нажатии
  static const Color buttonSecondary = offWhite; // #F7F6F2
  static const Color buttonSecondaryText = primary; // Текст на вторичных кнопках
  static const Color buttonDisabled = Color(0xFFBDBDBD);
  
  // Фон
  static const Color backgroundLight = offWhite; // #F7F6F2
  static const Color backgroundDark = darkGrey; // #383838
  static const Color cardBackground = white; // #FFFFFF
  static const Color cardBackgroundSecondary = Color(0xFFF0EFEB); // Слегка темнее off-white
  
  // Текст
  static const Color textPrimary = darkGrey; // #383838
  static const Color textSecondary = Color(0xFF757575); // Средне-серый
  static const Color textLight = white; // #FFFFFF
  static const Color textMuted = Color(0xFF9E9E9E);
  static const Color inputBorder = Color(0xFFC5C7CE);
  
  // UI элементы
  static const Color error = Color(0xFFE53935);
  static const Color success = primary; // Используем основной зеленый для успеха
  static const Color warning = Color(0xFFFF9800);
  static const Color info = Color(0xFF2196F3);
  
  // Программа лояльности
  static const Color loyaltyIconBg = Color(0xFFE8F5E9); // Светло-зеленый фон (используем с прозрачностью primary)
  static const Color loyaltyIcon = primary; // #5A7C4A
  
  // Дополнительные цвета для градиентов и эффектов
  static const Color primaryWithOpacity10 = Color(0x1A5A7C4A); // 10% прозрачности
  static const Color primaryWithOpacity15 = Color(0x265A7C4A); // 15% прозрачности
  static const Color primaryWithOpacity25 = Color(0x405A7C4A); // 25% прозрачности
  static const Color primaryWithOpacity50 = Color(0x805A7C4A); // 50% прозрачности
  
  // Тени и границы
  static const Color shadowLight = Color(0x1A000000); // Легкая тень
  static const Color shadowMedium = Color(0x33000000); // Средняя тень
  static const Color borderLight = Color(0xFFE0E0E0); // Светлая граница
}
