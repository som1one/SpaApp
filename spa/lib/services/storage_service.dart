import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

import '../utils/constants.dart';

class StorageService {
  static final StorageService _instance = StorageService._internal();
  factory StorageService() => _instance;
  StorageService._internal();

  SharedPreferences? _prefs;

  Future<void> init() async {
    _prefs ??= await SharedPreferences.getInstance();
  }

  Future<SharedPreferences> _ensurePrefs() async {
    _prefs ??= await SharedPreferences.getInstance();
    return _prefs!;
  }

  Future<void> saveString(String key, String value) async {
    final prefs = await _ensurePrefs();
    await prefs.setString(key, value);
  }

  Future<String?> getString(String key) async {
    final prefs = await _ensurePrefs();
    return prefs.getString(key);
  }

  Future<void> saveBool(String key, bool value) async {
    final prefs = await _ensurePrefs();
    await prefs.setBool(key, value);
  }

  Future<bool?> getBool(String key) async {
    final prefs = await _ensurePrefs();
    return prefs.getBool(key);
  }

  Future<void> saveObject(String key, Map<String, dynamic> value) async {
    final prefs = await _ensurePrefs();
    await prefs.setString(key, jsonEncode(value));
  }

  Future<Map<String, dynamic>?> getObject(String key) async {
    final prefs = await _ensurePrefs();
    final jsonString = prefs.getString(key);
    if (jsonString == null) return null;
    return jsonDecode(jsonString) as Map<String, dynamic>;
  }

  Future<void> remove(String key) async {
    final prefs = await _ensurePrefs();
    await prefs.remove(key);
  }

  Future<void> clear() async {
    final prefs = await _ensurePrefs();
    await prefs.clear();
  }

  Future<void> saveToken(String token) async {
    await saveString(AppConstants.tokenKey, token);
  }

  Future<String?> getToken() async {
    return getString(AppConstants.tokenKey);
  }

  Future<void> removeToken() async {
    await remove(AppConstants.tokenKey);
  }
}

