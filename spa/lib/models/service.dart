class Service {
  final int id;
  final String name;
  final String? subtitle;
  final String? description;
  final double? price;
  final int? duration; // мин
  final String? category;
  final int? categoryId;
  final String? imageUrl;
  final String? detailImageUrl;
  final List<Map<String, dynamic>>? additionalServices;
  final List<String>? highlights;
  final String? contactLink;
  final String? contactLabel;
  final String? bookButtonLabel;
  final int orderIndex;
  final bool isActive;
  final int? yclientsServiceId;
  final int? yclientsStaffId;

  Service({
    required this.id,
    required this.name,
    this.subtitle,
    this.description,
    this.price,
    this.duration,
    this.category,
    this.categoryId,
    this.imageUrl,
    this.detailImageUrl,
    this.additionalServices,
    this.highlights,
    this.contactLink,
    this.contactLabel,
    this.bookButtonLabel,
    this.orderIndex = 0,
    this.isActive = true,
    this.yclientsServiceId,
    this.yclientsStaffId,
  });

  factory Service.fromJson(Map<String, dynamic> json) {
    List<Map<String, dynamic>>? parseAdditional(dynamic data) {
      if (data == null) return null;
      return (data as List)
          .map(
            (item) => item is Map
                ? Map<String, dynamic>.from(item as Map)
                : {
                    'name': item.toString(),
                  },
          )
          .toList();
    }

    List<String>? parseHighlights(dynamic data) {
      if (data == null) return null;
      return (data as List).map((item) => item.toString()).toList();
    }

    return Service(
      id: json['id'] is int ? json['id'] : int.parse(json['id'].toString()),
      name: json['name'] as String? ?? '',
      subtitle: json['subtitle'] as String?,
      description: json['description'] as String?,
      price: json['price'] != null ? (json['price'] as num).toDouble() : null,
      duration: json['duration'] as int?,
      category: json['category'] as String?,
      categoryId: json['category_id'] as int?,
      imageUrl: json['image_url'] as String?,
      detailImageUrl: json['detail_image_url'] as String?,
      additionalServices: parseAdditional(json['additional_services']),
      highlights: parseHighlights(json['highlights']),
      contactLink: json['contact_link'] as String?,
      contactLabel: json['contact_label'] as String?,
      bookButtonLabel: json['book_button_label'] as String?,
      orderIndex: json['order_index'] as int? ?? 0,
      isActive: json['is_active'] as bool? ?? true,
      yclientsServiceId: json['yclients_service_id'] as int?,
      yclientsStaffId: json['yclients_staff_id'] as int?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'subtitle': subtitle,
      'description': description,
      'price': price,
      'duration': duration,
      'category': category,
      'category_id': categoryId,
      'image_url': imageUrl,
      'detail_image_url': detailImageUrl,
      'additional_services': additionalServices,
      'highlights': highlights,
      'contact_link': contactLink,
      'contact_label': contactLabel,
      'book_button_label': bookButtonLabel,
      'order_index': orderIndex,
      'is_active': isActive,
      'yclients_service_id': yclientsServiceId,
      'yclients_staff_id': yclientsStaffId,
    };
  }

  Service copyWith({
    int? id,
    String? name,
    String? subtitle,
    String? description,
    double? price,
    int? duration,
    String? category,
    int? categoryId,
    String? imageUrl,
    String? detailImageUrl,
    List<Map<String, dynamic>>? additionalServices,
    List<String>? highlights,
    String? contactLink,
    String? contactLabel,
    String? bookButtonLabel,
    int? orderIndex,
    bool? isActive,
    int? yclientsServiceId,
    int? yclientsStaffId,
  }) {
    return Service(
      id: id ?? this.id,
      name: name ?? this.name,
      subtitle: subtitle ?? this.subtitle,
      description: description ?? this.description,
      price: price ?? this.price,
      duration: duration ?? this.duration,
      category: category ?? this.category,
      categoryId: categoryId ?? this.categoryId,
      imageUrl: imageUrl ?? this.imageUrl,
      detailImageUrl: detailImageUrl ?? this.detailImageUrl,
      additionalServices: additionalServices ?? this.additionalServices,
      highlights: highlights ?? this.highlights,
      contactLink: contactLink ?? this.contactLink,
      contactLabel: contactLabel ?? this.contactLabel,
      bookButtonLabel: bookButtonLabel ?? this.bookButtonLabel,
      orderIndex: orderIndex ?? this.orderIndex,
      isActive: isActive ?? this.isActive,
      yclientsServiceId: yclientsServiceId ?? this.yclientsServiceId,
      yclientsStaffId: yclientsStaffId ?? this.yclientsStaffId,
    );
  }
}

