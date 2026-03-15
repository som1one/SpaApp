import 'package:flutter/material.dart';
import '../../theme/app_text_styles.dart';
import '../../utils/validators.dart';
import '../../theme/app_colors.dart';
import '../../services/auth_service.dart';
import '../../routes/route_names.dart';

class PasswordScreen extends StatefulWidget {
  final String email;
  final String? phone;

  const PasswordScreen({
    super.key,
    required this.email,
    this.phone,
  });

  @override
  State<PasswordScreen> createState() => _PasswordScreenState();
}

class _PasswordScreenState extends State<PasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _passwordController = TextEditingController();
  bool _isObscured = true;
  bool _isLoading = false;
  final _authService = AuthService();

  @override
  void dispose() {
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _handleSubmit() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() => _isLoading = true);

    final success = await _authService.login(
      widget.email,
      _passwordController.text.trim(),
    );

    if (!mounted) return;

    setState(() => _isLoading = false);

    if (success) {
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
          content: Text('Неверный пароль'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => FocusScope.of(context).unfocus(),
      child: Scaffold(
        backgroundColor: AppColors.white,
        appBar: AppBar(
          backgroundColor: AppColors.white,
          elevation: 0,
          leading: IconButton(
            icon: const Icon(Icons.arrow_back_ios_new, color: AppColors.buttonPrimary),
            onPressed: () => Navigator.of(context).pop(),
          ),
          title: Text(
            'Вход',
            style: AppTextStyles.heading3.copyWith(
              fontFamily: 'Inter24',
              fontWeight: FontWeight.w700,
              color: AppColors.buttonPrimary,
            ),
          ),
          centerTitle: true,
        ),
        body: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 420),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const _SectionTitle(),
                    const SizedBox(height: 12),
                    _PasswordField(
                      controller: _passwordController,
                      isObscured: _isObscured,
                      onToggleVisibility: () => setState(() {
                        _isObscured = !_isObscured;
                      }),
                    ),
                    const SizedBox(height: 24),
                    SizedBox(
                      height: 58,
                      child: ElevatedButton(
                        onPressed: _isLoading ? null : _handleSubmit,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.buttonPrimary,
                          foregroundColor: AppColors.white,
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
                                  valueColor: AlwaysStoppedAnimation<Color>(AppColors.white),
                                ),
                              )
                            : Text(
                                'Подтвердить',
                                style: AppTextStyles.button.copyWith(
                                  fontFamily: 'Inter24',
                                  fontSize: 20,
                                  fontWeight: FontWeight.w600,
                                  color: AppColors.white,
                                ),
                              ),
                      ),
                    ),
                    const SizedBox(height: 28),
                    const _PasswordRequirements(),
                    const SizedBox(height: 24),
                    Text(
                      'Используйте уникальный пароль, чтобы обеспечить безопасность вашей учетной записи.',
                      style: AppTextStyles.bodyMedium.copyWith(
                        fontFamily: 'Inter18',
                        color: AppColors.textSecondary,
                        height: 26 / 16,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _SectionTitle extends StatelessWidget {
  const _SectionTitle();

  @override
  Widget build(BuildContext context) {
    return Text(
      'Пароль',
      style: AppTextStyles.bodyMedium.copyWith(
        fontFamily: 'Inter24',
        fontSize: 16,
        height: 26 / 16,
        fontWeight: FontWeight.w500,
        color: AppColors.buttonPrimary,
      ),
    );
  }
}

class _PasswordField extends StatelessWidget {
  final TextEditingController controller;
  final bool isObscured;
  final VoidCallback onToggleVisibility;

  const _PasswordField({
    required this.controller,
    required this.isObscured,
    required this.onToggleVisibility,
  });

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      obscureText: isObscured,
      style: TextStyle(
        fontFamily: 'Inter24',
        fontSize: 16,
        height: 26 / 16,
        fontWeight: FontWeight.w400,
        color: AppColors.textPrimary,
      ),
      decoration: InputDecoration(
        hintText: 'Введите ваш пароль',
        hintStyle: const TextStyle(
          fontFamily: 'Inter24',
          fontSize: 16,
          height: 26 / 16,
          fontWeight: FontWeight.w400,
          color: Color(0xFF9095A1),
        ),
        filled: true,
        fillColor: const Color(0xFFFAFAFB),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: AppColors.buttonPrimary.withOpacity(0.35)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: AppColors.buttonPrimary.withOpacity(0.35)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: AppColors.buttonPrimary, width: 1.4),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
        suffixIcon: IconButton(
          icon: Icon(
            isObscured ? Icons.visibility : Icons.visibility_off,
            color: AppColors.buttonPrimary,
          ),
          onPressed: onToggleVisibility,
        ),
      ),
      validator: (value) {
        if (value == null || value.isEmpty) {
          return 'Введите пароль';
        }
        if (value.length < 8) {
          return 'Пароль должен содержать минимум 8 символов';
        }
        if (!RegExp(r'[A-ZА-Я]').hasMatch(value)) {
          return 'Добавьте хотя бы одну заглавную букву';
        }
        if (!RegExp(r'\d').hasMatch(value)) {
          return 'Добавьте хотя бы одну цифру';
        }
        if (!RegExp(r'[^A-Za-z0-9]').hasMatch(value)) {
          return 'Добавьте хотя бы один специальный символ';
        }
        return null;
      },
    );
  }
}

class _PasswordRequirements extends StatelessWidget {
  const _PasswordRequirements();

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Подсказки для пароля:',
          style: AppTextStyles.bodyMedium.copyWith(
            fontFamily: 'Inter24',
            fontSize: 16,
            height: 26 / 16,
            fontWeight: FontWeight.w500,
            color: AppColors.buttonPrimary,
          ),
        ),
        const SizedBox(height: 12),
        const _RequirementItem(text: 'Минимум 8 символов'),
        const _RequirementItem(text: 'Хотя бы одну заглавную букву'),
        const _RequirementItem(text: 'Хотя бы одну цифру'),
        const _RequirementItem(text: 'Хотя бы один специальный символ'),
      ],
    );
  }
}

class _RequirementItem extends StatelessWidget {
  final String text;

  const _RequirementItem({required this.text});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Padding(
            padding: EdgeInsets.only(top: 9),
            child: Icon(
              Icons.circle,
              size: 6,
              color: AppColors.buttonPrimary,
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              text,
              style: const TextStyle(
                fontFamily: 'Inter24',
                fontSize: 16,
                height: 26 / 16,
                fontWeight: FontWeight.w400,
                color: Color(0xFF3A3E47),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

