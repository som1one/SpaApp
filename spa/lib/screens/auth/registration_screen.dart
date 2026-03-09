import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import '../../routes/route_names.dart';
import '../../services/api_service.dart';
import '../../services/auth_service.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../utils/validators.dart';
import '../../utils/constants.dart';
// import 'vk_auth_screen.dart';

class RegistrationScreen extends StatefulWidget {
  const RegistrationScreen({super.key});

  @override
  State<RegistrationScreen> createState() => _RegistrationScreenState();
}

class _RegistrationScreenState extends State<RegistrationScreen> {
  final _formKey = GlobalKey<FormState>();
  final _phoneController = TextEditingController();
  final _emailController = TextEditingController();
  bool _isLoading = false;
  bool _isFormattingPhone = false;
  final _authService = AuthService();

  void _handlePhoneFormatting() {
    if (_isFormattingPhone) return;
    final text = _phoneController.text;
    if (text.isEmpty) return;

    final digitsOnly = text.replaceAll(RegExp(r'[^0-9]'), '');
    String formatted = '+$digitsOnly';

    if (formatted == _phoneController.text) {
      return;
    }

    _isFormattingPhone = true;
    _phoneController.value = TextEditingValue(
      text: formatted,
      selection: TextSelection.collapsed(offset: formatted.length),
    );
    _isFormattingPhone = false;
  }

  @override
  void initState() {
    super.initState();
    _phoneController.addListener(_handlePhoneFormatting);
    
    // Проверяем, авторизован ли пользователь после restoreSession
    // Используем addPostFrameCallback чтобы дать время restoreSession выполниться
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      // Даем время на выполнение restoreSession в фоне
      await Future.delayed(const Duration(milliseconds: 500));
      
      if (!mounted) return;
      
      // Проверяем аутентификацию
      if (_authService.isAuthenticated) {
        Navigator.of(context).pushReplacementNamed(RouteNames.home);
      }
    });
  }

  @override
  void dispose() {
    _phoneController.removeListener(_handlePhoneFormatting);
    _phoneController.dispose();
    _emailController.dispose();
    super.dispose();
  }

  Future<void> _handleContinue() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final apiService = ApiService();
      final email = _emailController.text.trim();
      final rawPhone = _phoneController.text.trim();
      final phone = rawPhone.isNotEmpty && !rawPhone.startsWith('+')
          ? '+$rawPhone'
          : rawPhone;

      try {
        final queryParts = <String>[
          'email=${Uri.encodeComponent(email)}',
          if (phone.isNotEmpty) 'phone=${Uri.encodeComponent(phone)}',
        ];
        final query = queryParts.join('&');
        final checkResponse =
            await apiService.get('/auth/check-email?$query');
        final userExists = checkResponse['exists'] == true;

        if (!mounted) return;
        setState(() {
          _isLoading = false;
        });

        if (userExists) {
          Navigator.of(context).pushNamed(
            RouteNames.password,
            arguments: {'email': email, 'phone': phone},
          );
        } else {
          final password = await _showPasswordDialog(
            title: 'Создайте пароль',
            subtitle:
                'Минимум 8 символов, заглавную букву, цифру и специальный символ.',
            confirm: true,
            primaryActionLabel: 'Продолжить',
          );

          if (password == null) {
            return;
          }

          if (!mounted) return;

          // ЗАКОММЕНТИРОВАНО: запрос кода больше не нужен, сразу переходим к вводу имени
          // final requested = await _requestVerificationCode(apiService, email, phone);
          // if (!requested) {
          //   return;
          // }

          if (!mounted) return;

          Navigator.of(context).pushNamed(
            RouteNames.nameRegistration,
            arguments: {
              'email': email,
              'password': password,
              'phone': phone,
            },
          );
        }
      } catch (e) {
        if (!mounted) return;

        setState(() {
          _isLoading = false;
        });

        var message = e.toString();
        if (message.contains('Failed to fetch')) {
          message =
              'Не удалось подключиться к серверу. Проверьте адрес и доступность API.';
        }

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Ошибка: $message'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      if (!mounted) return;
      
      setState(() {
        _isLoading = false;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Ошибка: ${e.toString()}'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

    // Future<void> _handleVkLogin() async {
  //   if (!mounted) return;
  //   
  //   // VK App ID из констант
  //   final vkAppId = AppConstants.vkAppId;
  //   final redirectUri = AppConstants.vkRedirectUri;
  //   
  //   if (vkAppId.isEmpty) {
  //     if (!mounted) return;
  //     ScaffoldMessenger.of(context).showSnackBar(
  //       const SnackBar(
  //         content: Text('VK App ID не настроен. Обратитесь к администратору.'),
  //         backgroundColor: AppColors.error,
  //       ),
  //     );
  //     return;
  //   }
  //   
  //   // Открываем экран авторизации VK
  //   await Navigator.of(context).push(
  //     MaterialPageRoute(
  //       builder: (context) => VkAuthScreen(
  //         vkAppId: vkAppId,
  //         redirectUri: redirectUri,
  //       ),
  //     ),
  //   );
  // }

  Future<bool> _requestVerificationCode(
    ApiService apiService,
    String email,
    String phone,
  ) async {
    setState(() => _isLoading = true);
    try {
      await apiService.post('/auth/request-code', {
        'email': email,
        'phone': phone,
      });
      if (!mounted) return false;
      setState(() => _isLoading = false);
      return true;
    } catch (e) {
      if (!mounted) return false;
      setState(() => _isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Не удалось отправить код: $e'),
          backgroundColor: Colors.red,
        ),
      );
      return false;
    }
  }

  Future<String?> _showPasswordDialog({
    required String title,
    String? subtitle,
    bool confirm = false,
    required String primaryActionLabel,
  }) async {
    final formKey = GlobalKey<FormState>();
    final passwordController = TextEditingController();
    final confirmController = TextEditingController();
    bool showPassword = false;
    bool showConfirm = false;

    return showDialog<String>(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) {
        return StatefulBuilder(
          builder: (context, setState) {
            return AlertDialog(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(20),
              ),
              title: Text(
                title,
                style: AppTextStyles.heading3.copyWith(
                  fontFamily: 'Inter24',
                  color: AppColors.textPrimary,
                  fontWeight: FontWeight.w700,
                ),
              ),
              content: Form(
                key: formKey,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    if (subtitle != null) ...[
                      Text(
                        subtitle,
                        style: AppTextStyles.bodyMedium.copyWith(
                          fontFamily: 'Inter18',
                          color: AppColors.textSecondary,
                        ),
                      ),
                      const SizedBox(height: 16),
                    ],
                    TextFormField(
                      controller: passwordController,
                      obscureText: !showPassword,
                      decoration: InputDecoration(
                        hintText: 'Пароль',
                        filled: true,
                        fillColor: AppColors.cardBackground,
                        hintStyle: AppTextStyles.bodyLarge.copyWith(
                          fontFamily: 'Inter24',
                          color: AppColors.inputBorder,
                        ),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(14),
                          borderSide: const BorderSide(color: AppColors.inputBorder),
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(14),
                          borderSide: const BorderSide(color: AppColors.inputBorder),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(14),
                          borderSide: const BorderSide(color: AppColors.buttonPrimary),
                        ),
                        contentPadding:
                            const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
                        suffixIcon: IconButton(
                          icon: Icon(
                            showPassword ? Icons.visibility : Icons.visibility_off,
                            color: AppColors.textSecondary,
                          ),
                          onPressed: () => setState(() {
                            showPassword = !showPassword;
                          }),
                        ),
                      ),
                      validator: Validators.validatePassword,
                    ),
                    if (confirm) ...[
                      const SizedBox(height: 12),
                      TextFormField(
                        controller: confirmController,
                        obscureText: !showConfirm,
                        decoration: InputDecoration(
                          hintText: 'Повторите пароль',
                          filled: true,
                          fillColor: AppColors.cardBackground,
                          hintStyle: AppTextStyles.bodyLarge.copyWith(
                            fontFamily: 'Inter24',
                            color: AppColors.inputBorder,
                          ),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(14),
                            borderSide: const BorderSide(color: AppColors.inputBorder),
                          ),
                          enabledBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(14),
                            borderSide: const BorderSide(color: AppColors.inputBorder),
                          ),
                          focusedBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(14),
                            borderSide: const BorderSide(color: AppColors.buttonPrimary),
                          ),
                          contentPadding: const EdgeInsets.symmetric(
                              horizontal: 16, vertical: 16),
                          suffixIcon: IconButton(
                            icon: Icon(
                              showConfirm ? Icons.visibility : Icons.visibility_off,
                              color: AppColors.textSecondary,
                            ),
                            onPressed: () => setState(() {
                              showConfirm = !showConfirm;
                            }),
                          ),
                        ),
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Введите пароль повторно';
                          }
                          if (value != passwordController.text) {
                            return 'Пароли не совпадают';
                          }
                          return null;
                        },
                      ),
                    ],
                  ],
                ),
              ),
              actionsPadding:
                  const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              actions: [
                TextButton(
                  onPressed: () {
                    Navigator.of(dialogContext).pop();
                  },
                  style: TextButton.styleFrom(
                    foregroundColor: AppColors.textSecondary,
                  ),
                  child: Text(
                    'Отмена',
                    style: AppTextStyles.bodyMedium.copyWith(
                      fontFamily: 'Inter18',
                      color: AppColors.textSecondary,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
                ElevatedButton(
                  onPressed: () {
                    if (formKey.currentState?.validate() ?? false) {
                      Navigator.of(dialogContext)
                          .pop(passwordController.text.trim());
                    }
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.buttonPrimary,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: Text(
                    primaryActionLabel,
                    style: AppTextStyles.button.copyWith(
                      fontFamily: 'Inter24',
                      color: Colors.white,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final inputDecoration = InputDecoration(
      filled: true,
      fillColor: const Color(0xFFFAFAFB),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: const BorderSide(color: Color(0xFFDEE1E6)),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: const BorderSide(color: Color(0xFFDEE1E6)),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: const BorderSide(color: Color(0xFFDEE1E6), width: 1.2),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: const BorderSide(color: AppColors.error),
      ),
      contentPadding: const EdgeInsets.symmetric(horizontal: 34, vertical: 20),
      hintStyle: const TextStyle(
        fontFamily: 'Inter24',
        fontSize: 16,
        height: 26 / 16,
        fontWeight: FontWeight.w400,
        color: Color(0xFF9095A1),
      ),
    );

    return GestureDetector(
      onTap: () => FocusScope.of(context).unfocus(),
      child: Scaffold(
        backgroundColor: Colors.white,
        body: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 420),
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const SizedBox(height: 44),
                      Text(
                        'Добро пожаловать!',
                        style: const TextStyle(
                          fontFamily: 'Inter24',
                          fontSize: 34,
                          height: 40 / 34,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF1E2128),
                        ),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 12),
                      Text(
                        'Войдите или создайте аккаунт',
                        style: const TextStyle(
                          fontFamily: 'Inter24',
                          fontSize: 18,
                          height: 28 / 18,
                          fontWeight: FontWeight.w400,
                          color: Color(0xFF9095A1),
                        ),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 40),
                      const _SectionLabel(text: 'Номер телефона'),
                      const SizedBox(height: 12),
                      TextFormField(
                        controller: _phoneController,
                        style: const TextStyle(
                          fontFamily: 'Inter24',
                          fontSize: 16,
                          height: 26 / 16,
                          fontWeight: FontWeight.w400,
                          color: AppColors.textPrimary,
                        ),
                        decoration: inputDecoration.copyWith(
                          hintText: 'Введите номер телефона',
                          prefixIcon: _InputIcon(
                            svgAsset: 'assets/images/Registration/phone.svg',
                            fallback: Icons.phone_outlined,
                            color: const Color(0xFF9095A1),
                          ),
                        ),
                        keyboardType: TextInputType.phone,
                        validator: Validators.validatePhone,
                      ),
                      const SizedBox(height: 22),
                      const _SectionLabel(text: 'Адрес электронной почты'),
                      const SizedBox(height: 12),
                      TextFormField(
                        controller: _emailController,
                        style: const TextStyle(
                          fontFamily: 'Inter24',
                          fontSize: 16,
                          height: 26 / 16,
                          fontWeight: FontWeight.w400,
                          color: AppColors.textPrimary,
                        ),
                        decoration: inputDecoration.copyWith(
                          hintText: 'Введите адрес электронной почты',
                          prefixIcon: _InputIcon(
                            svgAsset: 'assets/images/Registration/mail.svg',
                            fallback: Icons.email_outlined,
                            color: const Color(0xFF9095A1),
                          ),
                        ),
                        keyboardType: TextInputType.emailAddress,
                        validator: Validators.validateEmail,
                        autocorrect: false,
                      ),
                      const SizedBox(height: 32),
                      SizedBox(
                        height: 58,
                        child: ElevatedButton(
                          onPressed: _isLoading ? null : _handleContinue,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppColors.buttonPrimary,
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(18),
                            ),
                            elevation: 0,
                          ),
                          child: _isLoading
                              ? const SizedBox(
                                  width: 20,
                                  height: 20,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                                  ),
                                )
                              : Text(
                                  'Продолжить',
                                  style: AppTextStyles.button.copyWith(
                                    fontFamily: 'Inter24',
                                    fontSize: 20,
                                    color: Colors.white,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                        ),
                      ),
                      // const SizedBox(height: 32),
                      // Row(
                      //   children: [
                      //     Expanded(
                      //       child: Container(
                      //         height: 1,
                      //         color: const Color(0xFFDEE1E6),
                      //       ),
                      //     ),
                      //     const SizedBox(width: 16),
                      //     Text(
                      //       'или',
                      //       style: AppTextStyles.bodyMedium.copyWith(
                      //         fontFamily: 'Inter24',
                      //         color: AppColors.textSecondary,
                      //         fontWeight: FontWeight.w500,
                      //       ),
                      //     ),
                      //     const SizedBox(width: 16),
                      //     Expanded(
                      //       child: Container(
                      //         height: 1,
                      //         color: const Color(0xFFDEE1E6),
                      //       ),
                      //     ),
                      //   ],
                      // ),
                      // const SizedBox(height: 24),
                      // _SocialButton(
                      //   label: 'Войти с помощью VK',
                      //   asset: 'assets/images/Registration/vk.svg',
                      //   fallbackIcon: Icon(
                      //     Icons.group,
                      //     color: AppColors.textPrimary,
                      //     size: 24,
                      //   ),
                      //   onPressed: _handleVkLogin,
                      // ),
                      const SizedBox(height: 20),
                      Text(
                        'Продолжая, вы соглашаетесь с условиями сервиса',
                        style: AppTextStyles.bodySmall.copyWith(
                          fontFamily: 'Inter18',
                          color: AppColors.textSecondary.withOpacity(0.7),
                        ),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 24),
                      TextButton(
                        onPressed: () {
                          Navigator.of(context).pushReplacementNamed(RouteNames.home);
                        },
                        child: Text(
                          'Продолжить как гость',
                          style: AppTextStyles.bodyMedium.copyWith(
                            fontFamily: 'Inter24',
                            color: AppColors.buttonPrimary,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _SectionLabel extends StatelessWidget {
  final String text;
  const _SectionLabel({required this.text});

  @override
  Widget build(BuildContext context) {
    return Text(
      text,
      style: AppTextStyles.bodyMedium.copyWith(
        fontFamily: 'Inter24',
        fontSize: 16,
        height: 26 / 16,
        color: const Color(0xFF1E2128),
        fontWeight: FontWeight.w500,
      ),
    );
  }
}

class _InputIcon extends StatelessWidget {
  final String svgAsset;
  final IconData fallback;
  final Color color;

  const _InputIcon({
    required this.svgAsset,
    required this.fallback,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(left: 18, right: 12),
      child: SvgPicture.asset(
        svgAsset,
        width: 20,
        height: 20,
        colorFilter: ColorFilter.mode(color, BlendMode.srcIn),
        placeholderBuilder: (_) => Icon(
          fallback,
          color: color,
          size: 20,
        ),
      ),
    );
  }
}

class _SocialButton extends StatelessWidget {
  final String label;
  final String asset;
  final VoidCallback onPressed;
  final Widget fallbackIcon;

  const _SocialButton({
    required this.label,
    required this.asset,
    required this.fallbackIcon,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 58,
      child: OutlinedButton(
        onPressed: onPressed,
        style: OutlinedButton.styleFrom(
          backgroundColor: Colors.white,
          foregroundColor: AppColors.textPrimary,
          padding: const EdgeInsets.symmetric(horizontal: 18),
          side: const BorderSide(color: Colors.black),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(18),
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            SvgPicture.asset(
              asset,
              width: 32,
              height: 32,
              placeholderBuilder: (_) => fallbackIcon,
            ),
            const SizedBox(width: 12),
            Text(
              label,
              style: AppTextStyles.button.copyWith(
                fontFamily: 'Inter24',
                color: AppColors.textPrimary,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }
}


