import 'package:flutter/material.dart';
import 'storage_service.dart';

class LanguageService {
  static const String _languageKey = 'app_language';
  static const Locale defaultLocale = Locale('ru');

  static final LanguageService _instance = LanguageService._internal();
  factory LanguageService() => _instance;
  LanguageService._internal();

  final StorageService _storage = StorageService();

  Future<Locale> getLocale() async {
    final languageCode = await _storage.getString(_languageKey);
    if (languageCode == null) {
      return defaultLocale;
    }
    return Locale(languageCode);
  }

  Future<void> setLocale(Locale locale) async {
    await _storage.saveString(_languageKey, locale.languageCode);
  }

  Future<void> setLanguage(String languageCode) async {
    await setLocale(Locale(languageCode));
  }
}

