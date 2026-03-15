class User {
  final int id;
  final String name;
  final String? surname;
  final String email;
  final String? phone;
  final String? avatarUrl;
  final bool isVerified;
  final int? loyaltyLevel;
  final int? loyaltyBonuses;
  final int? spentBonuses;
  final bool autoApplyLoyaltyPoints;
  final String? uniqueCode;

  User({
    required this.id,
    required this.name,
    this.surname,
    required this.email,
    this.phone,
    this.avatarUrl,
    this.isVerified = false,
    this.loyaltyLevel,
    this.loyaltyBonuses,
    this.spentBonuses,
    this.autoApplyLoyaltyPoints = false,
    this.uniqueCode,
  });

  String get fullName {
    if (surname != null && surname!.isNotEmpty) {
      return '$name $surname';
    }
    return name;
  }

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] is int ? json['id'] : int.parse(json['id'].toString()),
      name: json['name'] as String? ?? '',
      surname: json['surname'] as String?,
      email: json['email'] as String,
      phone: json['phone'] as String?,
      avatarUrl: json['avatar_url'] as String?,
      isVerified: json['is_verified'] as bool? ?? false,
      loyaltyLevel: json['loyalty_level'] is int
          ? json['loyalty_level'] as int?
          : json['loyalty_level'] != null
              ? int.tryParse(json['loyalty_level'].toString())
              : null,
      loyaltyBonuses: json['loyalty_bonuses'] is int
          ? json['loyalty_bonuses'] as int?
          : json['loyalty_bonuses'] != null
              ? int.tryParse(json['loyalty_bonuses'].toString())
              : null,
      spentBonuses: json['spent_bonuses'] is int
          ? json['spent_bonuses'] as int?
          : json['spent_bonuses'] != null
              ? int.tryParse(json['spent_bonuses'].toString())
              : null,
      autoApplyLoyaltyPoints: json['auto_apply_loyalty_points'] as bool? ?? false,
      uniqueCode: json['unique_code'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'surname': surname,
      'email': email,
      'phone': phone,
      'avatar_url': avatarUrl,
      'is_verified': isVerified,
      'loyalty_level': loyaltyLevel,
      'loyalty_bonuses': loyaltyBonuses,
      'spent_bonuses': spentBonuses,
      'auto_apply_loyalty_points': autoApplyLoyaltyPoints,
      'unique_code': uniqueCode,
    };
  }

  User copyWith({
    int? id,
    String? name,
    String? surname,
    String? email,
    String? phone,
    String? avatarUrl,
    bool? isVerified,
    int? loyaltyLevel,
    int? loyaltyBonuses,
    int? spentBonuses,
    bool? autoApplyLoyaltyPoints,
    String? uniqueCode,
  }) {
    return User(
      id: id ?? this.id,
      name: name ?? this.name,
      surname: surname ?? this.surname,
      email: email ?? this.email,
      phone: phone ?? this.phone,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      isVerified: isVerified ?? this.isVerified,
      loyaltyLevel: loyaltyLevel ?? this.loyaltyLevel,
      loyaltyBonuses: loyaltyBonuses ?? this.loyaltyBonuses,
      spentBonuses: spentBonuses ?? this.spentBonuses,
      autoApplyLoyaltyPoints: autoApplyLoyaltyPoints ?? this.autoApplyLoyaltyPoints,
      uniqueCode: uniqueCode ?? this.uniqueCode,
    );
  }
}

