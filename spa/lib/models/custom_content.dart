class CustomContentBlock {
  final int id;
  final String title;
  final String? subtitle;
  final String? description;
  final String? imageUrl;
  final String? actionUrl;
  final String? actionText;
  final String blockType;
  final int orderIndex;
  final bool isActive;
  final String? backgroundColor;
  final String? textColor;
  final String? gradientStart;
  final String? gradientEnd;

  CustomContentBlock({
    required this.id,
    required this.title,
    this.subtitle,
    this.description,
    this.imageUrl,
    this.actionUrl,
    this.actionText,
    required this.blockType,
    required this.orderIndex,
    required this.isActive,
    this.backgroundColor,
    this.textColor,
    this.gradientStart,
    this.gradientEnd,
  });

  factory CustomContentBlock.fromJson(Map<String, dynamic> json) {
    return CustomContentBlock(
      id: json['id'] as int,
      title: json['title'] as String,
      subtitle: json['subtitle'] as String?,
      description: json['description'] as String?,
      imageUrl: json['image_url'] as String?,
      actionUrl: json['action_url'] as String?,
      actionText: json['action_text'] as String?,
      blockType: json['block_type'] as String,
      orderIndex: json['order_index'] as int,
      isActive: json['is_active'] as bool,
      backgroundColor: json['background_color'] as String?,
      textColor: json['text_color'] as String?,
      gradientStart: json['gradient_start'] as String?,
      gradientEnd: json['gradient_end'] as String?,
    );
  }
}

