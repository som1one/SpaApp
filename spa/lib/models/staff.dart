/// Модель мастера из YClients
class StaffMember {
  final int id;
  final String name;
  final String? specialization;
  final String? avatar;
  final double? rating;

  StaffMember({
    required this.id,
    required this.name,
    this.specialization,
    this.avatar,
    this.rating,
  });

  factory StaffMember.fromJson(Map<String, dynamic> json) {
    return StaffMember(
      id: json['id'] as int,
      name: json['name'] as String? ?? 'Мастер',
      specialization: json['specialization'] as String?,
      avatar: json['avatar'] as String?,
      rating: json['rating'] != null ? (json['rating'] as num).toDouble() : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'specialization': specialization,
      'avatar': avatar,
      'rating': rating,
    };
  }
}

