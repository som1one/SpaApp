import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'package:http/http.dart' as http;
import '../../services/auth_service.dart';
import '../../routes/route_names.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';

class VkAuthScreen extends StatefulWidget {
  final String vkAppId;
  final String redirectUri;

  const VkAuthScreen({
    super.key,
    required this.vkAppId,
    required this.redirectUri,
  });

  @override
  State<VkAuthScreen> createState() => _VkAuthScreenState();
}

class _VkAuthScreenState extends State<VkAuthScreen> {
  late WebViewController _controller;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _initWebView();
  }

  void _initWebView() {
    final vkAuthUrl = Uri.parse(
      'https://oauth.vk.com/authorize?'
      'client_id=${widget.vkAppId}&'
      'redirect_uri=${Uri.encodeComponent(widget.redirectUri)}&'
      'display=mobile&'
      'scope=email&'
      'response_type=token&'
      'v=5.131'
    ).toString();

    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setNavigationDelegate(
        NavigationDelegate(
          onPageStarted: (String url) {
            setState(() {
              _isLoading = true;
            });
            
            // Обрабатываем redirect URL с токеном
            if (url.startsWith(widget.redirectUri)) {
              _handleRedirect(url);
            }
          },
          onPageFinished: (String url) {
            setState(() {
              _isLoading = false;
            });
          },
          onWebResourceError: (WebResourceError error) {
            setState(() {
              _error = error.description;
              _isLoading = false;
            });
          },
        ),
      )
      ..loadRequest(Uri.parse(vkAuthUrl));
  }

  void _handleRedirect(String url) {
    try {
      // VK возвращает токен в fragment (#access_token=...)
      // URL выглядит как: https://oauth.vk.com/blank.html#access_token=...&user_id=...&email=...
      if (url.contains('#')) {
        final fragment = url.split('#')[1];
        final params = Uri.splitQueryString(fragment);
        
        if (params.containsKey('access_token')) {
          final accessToken = params['access_token']!;
          final userIdStr = params['user_id'] ?? '';
          final userId = int.tryParse(userIdStr);
          final email = params['email'];
          
          if (userId != null && accessToken.isNotEmpty) {
            _completeAuth(accessToken, userId, email);
            return;
          } else {
            setState(() {
              _error = 'Не удалось получить данные пользователя из VK';
              _isLoading = false;
            });
            return;
          }
        }
        
        if (params.containsKey('error')) {
          final errorDescription = params['error_description'] ?? 
                                   params['error_reason'] ?? 
                                   'Неизвестная ошибка';
          setState(() {
            _error = errorDescription;
            _isLoading = false;
          });
          return;
        }
      }
      
      // Также проверяем query параметры (на случай если VK вернет их там)
      final uri = Uri.parse(url);
      if (uri.queryParameters.containsKey('access_token')) {
        final accessToken = uri.queryParameters['access_token']!;
        final userIdStr = uri.queryParameters['user_id'] ?? '';
        final userId = int.tryParse(userIdStr);
        final email = uri.queryParameters['email'];
        
        if (userId != null && accessToken.isNotEmpty) {
          _completeAuth(accessToken, userId, email);
          return;
        }
      }
    } catch (e) {
      setState(() {
        _error = 'Ошибка обработки ответа: $e';
        _isLoading = false;
      });
    }
  }

  Future<void> _completeAuth(String accessToken, int userId, String? email) async {
    try {
      setState(() {
        _isLoading = true;
      });

      // Получаем дополнительную информацию о пользователе через VK API
      String? firstName;
      String? lastName;
      String? photoUrl;

      try {
        final vkApiUrl = Uri.parse(
          'https://api.vk.com/method/users.get?'
          'access_token=$accessToken&'
          'user_ids=$userId&'
          'fields=photo_200&'
          'v=5.131'
        );
        
        final response = await http.get(vkApiUrl);
        if (response.statusCode == 200) {
          final data = json.decode(response.body);
          if (data['response'] != null && data['response'].isNotEmpty) {
            final userData = data['response'][0];
            firstName = userData['first_name'];
            lastName = userData['last_name'];
            photoUrl = userData['photo_200'];
          }
        }
      } catch (e) {
        // Ошибка получения данных пользователя VK
        // Продолжаем без дополнительных данных
      }

      final authService = AuthService();
      final success = await authService.handleVkAuthData(
        accessToken: accessToken,
        userId: userId,
        email: email,
        firstName: firstName,
        lastName: lastName,
        photoUrl: photoUrl,
      );

      if (!mounted) return;

      if (success) {
        Navigator.of(context).pushNamedAndRemoveUntil(
          RouteNames.home,
          (route) => false,
        );
      } else {
        setState(() {
          _error = 'Не удалось войти через VK ID';
          _isLoading = false;
        });
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = 'Ошибка авторизации: $e';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.white,
      appBar: AppBar(
        backgroundColor: AppColors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, color: AppColors.textPrimary, size: 20),
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Text(
          'Вход через VK ID',
          style: AppTextStyles.heading3.copyWith(
            fontFamily: 'Inter24',
            color: AppColors.textPrimary,
            fontWeight: FontWeight.w700,
          ),
        ),
        centerTitle: true,
      ),
      body: Stack(
        children: [
          if (_error != null)
            Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.error_outline,
                      size: 64,
                      color: AppColors.error,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      _error!,
                      style: AppTextStyles.bodyMedium.copyWith(
                        fontFamily: 'Inter18',
                        color: AppColors.textPrimary,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 24),
                    ElevatedButton(
                      onPressed: () => Navigator.of(context).pop(),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.buttonPrimary,
                        foregroundColor: AppColors.white,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: Text(
                        'Закрыть',
                        style: AppTextStyles.button.copyWith(
                          fontFamily: 'Inter24',
                          color: AppColors.white,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            )
          else
            WebViewWidget(controller: _controller),
          if (_isLoading && _error == null)
            Container(
              color: AppColors.white,
              child: const Center(
                child: CircularProgressIndicator(
                  valueColor: AlwaysStoppedAnimation<Color>(AppColors.buttonPrimary),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

