class AppConstants {
  // API URLs
  static const String baseUrl = String.fromEnvironment(
    'SERVER_BASE_URL',
    // По умолчанию подключаемся к продовому серверу
    // При необходимости можно переопределить через --dart-define=SERVER_BASE_URL=...
    defaultValue: 'http://194.87.187.146:9003',
  );
  static const String apiVersion = String.fromEnvironment(
    'API_VERSION',
    defaultValue: '/api/v1',
  );
  
  // Timeouts
  static const int _connectionTimeoutSeconds = int.fromEnvironment(
    'CONNECTION_TIMEOUT_SECONDS',
    defaultValue: 30,
  );
  static const int _receiveTimeoutSeconds = int.fromEnvironment(
    'RECEIVE_TIMEOUT_SECONDS',
    defaultValue: 30,
  );
  static const Duration connectionTimeout = Duration(seconds: _connectionTimeoutSeconds);
  static const Duration receiveTimeout = Duration(seconds: _receiveTimeoutSeconds);
  
  // Storage keys
  static const String tokenKey = 'auth_token';
  static const String userKey = 'user_data';
  
  // Pagination
  static const int itemsPerPage = int.fromEnvironment(
    'ITEMS_PER_PAGE',
    defaultValue: 20,
  );
  
  // Default values
  static const String _defaultPaddingStr = String.fromEnvironment(
    'DEFAULT_PADDING',
    defaultValue: '16.0',
  );
  static const String _defaultBorderRadiusStr = String.fromEnvironment(
    'DEFAULT_BORDER_RADIUS',
    defaultValue: '8.0',
  );
  static double get defaultPadding => double.tryParse(_defaultPaddingStr) ?? 16.0;
  static double get defaultBorderRadius =>
      double.tryParse(_defaultBorderRadiusStr) ?? 8.0;
  
  // VK ID OAuth
  static const String vkAppId = String.fromEnvironment(
    'VK_APP_ID',
    defaultValue: '', // TODO: Установить VK App ID
  );
  static const String vkRedirectUri = 'https://oauth.vk.com/blank.html';
}

