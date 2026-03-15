import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../routes/route_names.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../services/api_service.dart';
import '../../services/auth_service.dart';
import '../../services/user_service.dart';

class VerifyEmailScreen extends StatefulWidget {
  final String email;
  final String password;
  final String phone;
  final String name;
  final String surname;
  
  const VerifyEmailScreen({
    super.key,
    required this.email,
    required this.password,
    required this.phone,
    required this.name,
    required this.surname,
  });

  @override
  State<VerifyEmailScreen> createState() => _VerifyEmailScreenState();
}

class _VerifyEmailScreenState extends State<VerifyEmailScreen> {
  final List<TextEditingController> _controllers = List.generate(
    6,
    (_) => TextEditingController(),
  );
  final List<FocusNode> _focusNodes = List.generate(
    6,
    (_) => FocusNode(),
  );
  bool _isVerifying = false;
  final _apiService = ApiService();
  final _authService = AuthService();
  final _userService = UserService();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _focusNodes[0].requestFocus();
    });
  }

  @override
  void dispose() {
    for (var controller in _controllers) {
      controller.dispose();
    }
    for (var node in _focusNodes) {
      node.dispose();
    }
    super.dispose();
  }

  void _handleCodeChange(int index, String value) {
    if (value.isEmpty && index > 0) {
      _focusNodes[index - 1].requestFocus();
      _controllers[index - 1].selection = TextSelection.fromPosition(
        TextPosition(offset: _controllers[index - 1].text.length),
      );
      return;
    }

    if (value.length > 1) {
      final digits = value.replaceAll(RegExp(r'[^0-9]'), '').split('');
      for (int i = 0; i < digits.length && (index + i) < 6; i++) {
        _controllers[index + i].text = digits[i];
      }
      
      final nextEmptyIndex = index + digits.length;
      if (nextEmptyIndex < 6) {
        _focusNodes[nextEmptyIndex].requestFocus();
      } else {
        _focusNodes[5].unfocus();
      }
    } else if (value.isNotEmpty) {
      if (index < 5) {
        _focusNodes[index + 1].requestFocus();
      } else {
        _focusNodes[index].unfocus();
      }
    }

    if (_isCodeComplete()) {
      Future.delayed(const Duration(milliseconds: 100), () {
        if (mounted) {
          _handleVerifyCode();
        }
      });
    }
  }

  bool _isCodeComplete() {
    return _controllers.every((controller) => controller.text.isNotEmpty);
  }

  String _getCode() {
    return _controllers.map((controller) => controller.text).join();
  }

  Future<void> _handleVerifyCode() async {
    if (_isVerifying) return;

    final code = _getCode();
    if (code.length != 6) return;

    setState(() => _isVerifying = true);

    try {
      await _apiService.post('/auth/register', {
        'name': widget.name,
        'surname': widget.surname,
        'email': widget.email,
        'password': widget.password,
        'phone': widget.phone,
        'code': code,
      });

      final loginSuccess = await _authService.login(widget.email, widget.password);
      if (!mounted) return;

      if (loginSuccess) {
        await _userService.refreshUser();
        if (!mounted) return;
        Navigator.of(context).pushNamedAndRemoveUntil(
          RouteNames.home,
          (route) => false,
        );
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Row(
              children: [
                Icon(Icons.check_circle, color: AppColors.white, size: 20),
                SizedBox(width: 12),
                Text(
                  'Успешный вход',
                  style: TextStyle(
                    fontFamily: 'Inter18',
                    fontWeight: FontWeight.w600,
                    fontSize: 14,
                  ),
                ),
              ],
            ),
            backgroundColor: AppColors.buttonPrimary, // Салатовый цвет как основной
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            margin: const EdgeInsets.all(16),
            duration: const Duration(seconds: 2),
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Не удалось автоматически войти. Попробуйте вручную.'),
            backgroundColor: Colors.orange,
          ),
        );
        Navigator.of(context).pushNamedAndRemoveUntil(
          RouteNames.registration,
          (route) => false,
        );
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Ошибка подтверждения: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      if (mounted) {
        setState(() => _isVerifying = false);
      }
    }
  }

  Future<void> _handleResendCode() async {
    for (var controller in _controllers) {
      controller.clear();
    }
    for (var node in _focusNodes) {
      node.unfocus();
    }
    _focusNodes[0].requestFocus();

    try {
      await _apiService.post('/auth/request-code', {
        'email': widget.email,
        'phone': widget.phone,
      });
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Код отправлен повторно'),
          backgroundColor: Colors.blue,
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Не удалось отправить код: $e'),
          backgroundColor: Colors.red,
        ),
      );
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
          icon: const Icon(
            Icons.arrow_back_ios_new,
            color: AppColors.buttonPrimary,
          ),
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Text(
          'Подтверждение почты',
          style: AppTextStyles.heading3.copyWith(
            fontFamily: 'Inter24',
            fontWeight: FontWeight.w700,
            fontSize: 18,
            color: AppColors.textPrimary,
          ),
        ),
        centerTitle: true,
        bottom: const PreferredSize(
          preferredSize: Size.fromHeight(1),
          child: Divider(
            height: 1,
            thickness: 1,
            color: AppColors.borderLight,
          ),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const SizedBox(height: 32),
              Text(
                'Пожалуйста, введите 6-значный код, который мы отправили на ваш адрес электронной почты.',
                textAlign: TextAlign.center,
                style: AppTextStyles.bodyMedium.copyWith(
                  fontFamily: 'Inter24',
                  fontSize: 16,
                  height: 26 / 16,
                  color: AppColors.textPrimary,
                ),
              ),
              const SizedBox(height: 40),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: List.generate(6, (index) {
                  return SizedBox(
                    width: 52,
                    height: 58,
                    child: TextField(
                      controller: _controllers[index],
                      focusNode: _focusNodes[index],
                      textAlign: TextAlign.center,
                      keyboardType: TextInputType.number,
                      inputFormatters: [
                        FilteringTextInputFormatter.digitsOnly,
                        LengthLimitingTextInputFormatter(1),
                      ],
                      style: const TextStyle(
                        fontFamily: 'Inter24',
                        fontSize: 20,
                        height: 26 / 20,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textPrimary,
                      ),
                      decoration: InputDecoration(
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(14),
                          borderSide: BorderSide(
                            color: AppColors.buttonPrimary.withOpacity(0.28),
                            width: 1,
                          ),
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(14),
                          borderSide: BorderSide(
                            color: AppColors.buttonPrimary.withOpacity(0.28),
                            width: 1,
                          ),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(14),
                          borderSide: const BorderSide(
                            color: AppColors.buttonPrimary,
                            width: 1.6,
                          ),
                        ),
                        filled: true,
                        fillColor: AppColors.backgroundLight,
                        contentPadding: EdgeInsets.zero,
                      ),
                      onChanged: (value) => _handleCodeChange(index, value),
                      onTap: () {
                        _controllers[index].selection = TextSelection.fromPosition(
                          TextPosition(offset: _controllers[index].text.length),
                        );
                      },
                      onSubmitted: (_) {
                        if (index < 5) {
                          _focusNodes[index + 1].requestFocus();
                        }
                      },
                    ),
                  );
                }),
              ),
              const SizedBox(height: 32),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    'Не получили код? ',
                    style: AppTextStyles.bodySmall.copyWith(
                      fontFamily: 'Inter24',
                      fontSize: 14,
                      color: AppColors.textSecondary,
                    ),
                  ),
                  GestureDetector(
                    onTap: _handleResendCode,
                    child: Text(
                      'Отправить еще раз',
                      style: AppTextStyles.bodySmall.copyWith(
                        fontFamily: 'Inter24',
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        color: AppColors.buttonPrimary.withOpacity(0.7),
                      ),
                    ),
                  ),
                ],
              ),
              const Spacer(),
              SizedBox(
                width: double.infinity,
                height: 58,
                child: ElevatedButton(
          onPressed:
              _isCodeComplete() && !_isVerifying ? _handleVerifyCode : null,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.buttonPrimary,
                    foregroundColor: AppColors.white,
                    disabledBackgroundColor: AppColors.buttonPrimary.withOpacity(0.25),
                    disabledForegroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(18),
                    ),
                    elevation: 0,
                  ),
          child: _isVerifying
              ? const SizedBox(
                  width: 22,
                  height: 22,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    valueColor: AlwaysStoppedAnimation<Color>(AppColors.white),
                  ),
                )
              : Text(
                  'Подтвердить код',
                  style: AppTextStyles.button.copyWith(
                    fontFamily: 'Inter24',
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: AppColors.white,
                  ),
                ),
                ),
              ),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }
}

