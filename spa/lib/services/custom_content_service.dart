import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

import '../models/custom_content.dart';
import '../services/api_service.dart';

class CustomContentService {
  final _apiService = ApiService();
  static const String _cacheKey = 'custom_content_cache';

  Future<List<CustomContentBlock>> getCachedBlocks() async {
    final prefs = await SharedPreferences.getInstance();
    final cached = prefs.getString(_cacheKey);
    if (cached == null || cached.isEmpty) {
      return [];
    }
    try {
      final List<dynamic> decoded = jsonDecode(cached) as List<dynamic>;
      return decoded
          .whereType<Map<String, dynamic>>()
          .map(CustomContentBlock.fromJson)
          .toList();
    } catch (_) {
      return [];
    }
  }

  Future<void> _saveCache(List<CustomContentBlock> blocks) async {
    final prefs = await SharedPreferences.getInstance();
    final encoded = jsonEncode(blocks.map(_blockToJson).toList());
    await prefs.setString(_cacheKey, encoded);
  }

  Map<String, dynamic> _blockToJson(CustomContentBlock block) {
    return {
      'id': block.id,
      'title': block.title,
      'subtitle': block.subtitle,
      'description': block.description,
      'image_url': block.imageUrl,
      'action_url': block.actionUrl,
      'action_text': block.actionText,
      'block_type': block.blockType,
      'order_index': block.orderIndex,
      'is_active': block.isActive,
      'background_color': block.backgroundColor,
      'text_color': block.textColor,
      'gradient_start': block.gradientStart,
      'gradient_end': block.gradientEnd,
    };
  }

  Future<List<CustomContentBlock>> getCustomContentBlocks() async {
    final cached = await getCachedBlocks();
    try {
      final response = await _apiService.get('/custom-content');
      if (response is List) {
        final blocks = response
            .whereType<Map<String, dynamic>>()
            .map(CustomContentBlock.fromJson)
            .toList();
        if (blocks.isNotEmpty) {
          await _saveCache(blocks);
          return blocks;
        }
      }
      return cached;
    } catch (_) {
      return cached;
    }
  }
}