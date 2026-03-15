import 'service.dart';

class MenuCategory {
  final int id;
  final String name;
  final String? description;
  final String? imageUrl;
  final int? parentId;
  final int orderIndex;
  final bool isActive;
  final List<MenuCategory> children;
  final List<Service> services;

  MenuCategory({
    required this.id,
    required this.name,
    this.description,
    this.imageUrl,
    this.parentId,
    this.orderIndex = 0,
    this.isActive = true,
    this.children = const [],
    this.services = const [],
  });

  factory MenuCategory.fromJson(Map<String, dynamic> json) {
    final List<dynamic> childData = json['children'] as List<dynamic>? ?? [];
    final List<dynamic> serviceData = json['services'] as List<dynamic>? ?? [];
    return MenuCategory(
      id: json['id'] as int,
      name: json['name'] as String? ?? '',
      description: json['description'] as String?,
      imageUrl: json['image_url'] as String?,
      parentId: json['parent_id'] as int?,
      orderIndex: json['order_index'] as int? ?? 0,
      isActive: json['is_active'] as bool? ?? true,
      children: childData.map((child) => MenuCategory.fromJson(Map<String, dynamic>.from(child as Map))).toList(),
      services: serviceData.map((svc) => Service.fromJson(Map<String, dynamic>.from(svc as Map))).toList(),
    );
  }

  MenuCategory copyWith({
    int? id,
    String? name,
    String? description,
    String? imageUrl,
    int? parentId,
    int? orderIndex,
    bool? isActive,
    List<MenuCategory>? children,
    List<Service>? services,
  }) {
    return MenuCategory(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      imageUrl: imageUrl ?? this.imageUrl,
      parentId: parentId ?? this.parentId,
      orderIndex: orderIndex ?? this.orderIndex,
      isActive: isActive ?? this.isActive,
      children: children ?? this.children,
      services: services ?? this.services,
    );
  }
}


