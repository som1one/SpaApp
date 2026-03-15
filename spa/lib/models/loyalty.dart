class LoyaltyLevel {
  final int id;
  final String name;
  final int minBonuses; // Минимальная сумма потраченных рублей для уровня (в рублях)
  final int cashbackPercent;
  final String colorStart;
  final String colorEnd;
  final String icon;
  final int orderIndex;
  final bool isActive;

  LoyaltyLevel({
    required this.id,
    required this.name,
    required this.minBonuses,
    required this.cashbackPercent,
    required this.colorStart,
    required this.colorEnd,
    required this.icon,
    required this.orderIndex,
    required this.isActive,
  });

  factory LoyaltyLevel.fromJson(Map<String, dynamic> json) {
    return LoyaltyLevel(
      id: json['id'] as int,
      name: json['name'] as String,
      minBonuses: json['min_bonuses'] as int,
      cashbackPercent: json['cashback_percent'] as int? ?? 0,
      colorStart: json['color_start'] as String,
      colorEnd: json['color_end'] as String,
      icon: json['icon'] as String? ?? 'eco',
      orderIndex: json['order_index'] as int? ?? 0,
      isActive: json['is_active'] as bool? ?? true,
    );
  }
}

class LoyaltyBonus {
  final int id;
  final String title;
  final String description;
  final String icon;
  final int? minLevelId;
  final int orderIndex;

  LoyaltyBonus({
    required this.id,
    required this.title,
    required this.description,
    required this.icon,
    this.minLevelId,
    required this.orderIndex,
  });

  factory LoyaltyBonus.fromJson(Map<String, dynamic> json) {
    return LoyaltyBonus(
      id: json['id'] as int,
      title: json['title'] as String,
      description: json['description'] as String,
      icon: json['icon'] as String? ?? 'card_giftcard',
      minLevelId: json['min_level_id'] as int?,
      orderIndex: json['order_index'] as int? ?? 0,
    );
  }
}

class LoyaltyInfo {
  final int currentBonuses; // Текущее количество бонусов
  final int spentBonuses; // Потраченные бонусы
  final LoyaltyLevel? currentLevel;
  final LoyaltyLevel? nextLevel;
  final int bonusesToNext; // Рублей до следующего уровня (название поля для совместимости, но содержит рубли)
  final double progress;
  final List<LoyaltyBonus> availableBonuses;
  final List<LoyaltyLevel> levels;

  LoyaltyInfo({
    required this.currentBonuses,
    required this.spentBonuses,
    this.currentLevel,
    this.nextLevel,
    required this.bonusesToNext,
    required this.progress,
    required this.availableBonuses,
    required this.levels,
  });

  factory LoyaltyInfo.fromJson(Map<String, dynamic> json) {
    return LoyaltyInfo(
      currentBonuses: json['current_bonuses'] as int,
      spentBonuses: json['spent_bonuses'] as int? ?? 0,
      currentLevel: json['current_level'] != null
          ? LoyaltyLevel.fromJson(json['current_level'] as Map<String, dynamic>)
          : null,
      nextLevel: json['next_level'] != null
          ? LoyaltyLevel.fromJson(json['next_level'] as Map<String, dynamic>)
          : null,
      bonusesToNext: json['bonuses_to_next'] as int,
      progress: (json['progress'] as num).toDouble(),
      availableBonuses: (json['available_bonuses'] as List<dynamic>?)
              ?.map((item) => LoyaltyBonus.fromJson(item as Map<String, dynamic>))
              .toList() ??
          [],
      levels: (json['levels'] as List<dynamic>?)
              ?.map((item) => LoyaltyLevel.fromJson(item as Map<String, dynamic>))
              .toList() ??
          [],
    );
  }
}

