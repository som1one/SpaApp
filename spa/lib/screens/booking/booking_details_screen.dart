import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../services/api_service.dart';
import '../../services/auth_service.dart';
import '../../services/user_service.dart';
import '../../models/service.dart';
import '../../models/user.dart';
import '../../routes/route_names.dart';

class BookingDetailsScreen extends StatefulWidget {
  final int serviceId;
  final Service? service;
  final DateTime appointmentDateTime;

  const BookingDetailsScreen({
    super.key,
    required this.serviceId,
    this.service,
    required this.appointmentDateTime,
  });

  @override
  State<BookingDetailsScreen> createState() => _BookingDetailsScreenState();
}

class _BookingDetailsScreenState extends State<BookingDetailsScreen> {
  final _formKey = GlobalKey<FormState>();
  final _notesController = TextEditingController();
  final _phoneController = TextEditingController();
  
  final _apiService = ApiService();
  final _authService = AuthService();
  
  Service? _service;
  User? _user;
  bool _isLoading = true;
  String? _error;
  
  Set<String> _selectedAdditionalServices = {};

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  @override
  void dispose() {
    _notesController.dispose();
    _phoneController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final token = _authService.token;
      if (token != null) {
        _apiService.token = token;
      }

      // Загружаем услугу, если не передана
      if (widget.service == null) {
        final serviceResponse = await _apiService.get('/services/${widget.serviceId}');
        if (serviceResponse is Map) {
          _service = Service.fromJson(Map<String, dynamic>.from(serviceResponse as Map));
        }
      } else {
        _service = widget.service;
      }

      // Загружаем данные пользователя
      _user = await UserService().getCurrentUser();
      if (_user?.phone != null) {
        _phoneController.text = _user!.phone!;
      }

      if (!mounted) return;
      setState(() {
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  void _toggleAdditionalService(String serviceName) {
    setState(() {
      if (_selectedAdditionalServices.contains(serviceName)) {
        _selectedAdditionalServices.remove(serviceName);
      } else {
        _selectedAdditionalServices.add(serviceName);
      }
    });
  }

  double _calculateTotalPrice() {
    double total = _service?.price ?? 0.0;
    // TODO: Добавить цены для дополнительных услуг, если они есть в БД
    return total;
  }

  Future<void> _handleContinue() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    // Переход на YClients для бронирования (оплата происходит в YClients)
    if (_service == null) return;
    
    Navigator.of(context).pushNamed(
      RouteNames.yclientsBooking,
      arguments: {
        'serviceId': _service!.id,
        'service': _service,
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(
            Icons.arrow_back_ios_new,
            color: AppColors.textPrimary,
            size: 20,
          ),
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Text(
          'Забронировать услугу',
          style: AppTextStyles.heading3.copyWith(
            color: AppColors.textPrimary,
            fontWeight: FontWeight.bold,
          ),
        ),
        centerTitle: true,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null || _service == null
              ? Center(
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
                        'Ошибка загрузки',
                        style: AppTextStyles.heading3.copyWith(
                          color: AppColors.textPrimary,
                        ),
                      ),
                      const SizedBox(height: 24),
                      ElevatedButton(
                        onPressed: _loadData,
                        child: const Text('Повторить'),
                      ),
                    ],
                  ),
                )
              : _buildContent(),
    );
  }

  Widget _buildContent() {
    return Form(
      key: _formKey,
      child: Column(
        children: [
          // Прогресс-бар
          _buildProgressBar(),
          
          // Контент
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Информация о записи
                  _buildBookingInfo(),
                  const SizedBox(height: 24),

                  // Дополнительные услуги
                  if (_service?.additionalServices?.isNotEmpty ?? false) ...[
                    _buildAdditionalServices(),
                    const SizedBox(height: 24),
                  ],

                  // Контактные данные
                  _buildContactSection(),
                  const SizedBox(height: 24),

                  // Комментарий
                  _buildNotesSection(),
                  const SizedBox(height: 24),

                  // Итоговая стоимость
                  _buildTotalPrice(),
                  const SizedBox(height: 100),
                ],
              ),
            ),
          ),

          // Кнопка продолжения
          _buildContinueButton(),
        ],
      ),
    );
  }

  Widget _buildProgressBar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      child: Row(
        children: [
          _buildProgressStep(
            number: 1,
            label: 'Дата и время',
            isActive: false,
            isCompleted: true,
          ),
          Expanded(
            child: Container(
              height: 2,
              color: AppColors.buttonPrimary,
              margin: const EdgeInsets.symmetric(horizontal: 8),
            ),
          ),
          _buildProgressStep(
            number: 2,
            label: 'Детали',
            isActive: true,
            isCompleted: false,
          ),
          Expanded(
            child: Container(
              height: 2,
              color: AppColors.cardBackground,
              margin: const EdgeInsets.symmetric(horizontal: 8),
            ),
          ),
          _buildProgressStep(
            number: 3,
            label: 'Забронировать',
            isActive: false,
            isCompleted: false,
          ),
          Expanded(
            child: Container(
              height: 2,
              color: AppColors.cardBackground,
              margin: const EdgeInsets.symmetric(horizontal: 8),
            ),
          ),
          _buildProgressStep(
            number: 4,
            label: 'Подтв',
            isActive: false,
            isCompleted: false,
          ),
        ],
      ),
    );
  }

  Widget _buildProgressStep({
    required int number,
    required String label,
    required bool isActive,
    required bool isCompleted,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: isActive ? AppColors.buttonPrimary : Colors.transparent,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (isActive)
            const Icon(
              Icons.eco,
              size: 16,
              color: Colors.white,
            )
          else if (isCompleted)
            Container(
              width: 20,
              height: 20,
              decoration: const BoxDecoration(
                shape: BoxShape.circle,
                color: AppColors.buttonPrimary,
              ),
              child: const Icon(
                Icons.check,
                size: 12,
                color: Colors.white,
              ),
            )
          else
            Container(
              width: 20,
              height: 20,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: AppColors.cardBackground,
              ),
              child: Center(
                child: Text(
                  '$number',
                  style: AppTextStyles.bodySmall.copyWith(
                    color: AppColors.textSecondary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ),
          const SizedBox(width: 6),
          Text(
            label,
            style: AppTextStyles.bodySmall.copyWith(
              color: isActive ? Colors.white : AppColors.textSecondary,
              fontWeight: isActive ? FontWeight.w600 : FontWeight.normal,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBookingInfo() {
    final dateFormat = DateFormat('dd MMMM yyyy', 'ru');
    final timeFormat = DateFormat('HH:mm', 'ru');
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.cardBackground,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: AppColors.buttonPrimary.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(
              Icons.calendar_today,
              color: AppColors.buttonPrimary,
              size: 24,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  dateFormat.format(widget.appointmentDateTime),
                  style: AppTextStyles.bodyLarge.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  timeFormat.format(widget.appointmentDateTime),
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAdditionalServices() {
    final services = _service?.additionalServices ?? [];
    if (services.isEmpty) return const SizedBox.shrink();

    IconData getIcon(String name) {
      final lowerName = name.toLowerCase();
      if (lowerName.contains('кам')) return Icons.wb_twilight;
      if (lowerName.contains('рефлекс') || lowerName.contains('стоп')) return Icons.directions_walk;
      if (lowerName.contains('голов') || lowerName.contains('head')) return Icons.self_improvement;
      return Icons.spa;
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Дополнительные услуги',
          style: AppTextStyles.heading3.copyWith(
            color: AppColors.textPrimary,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: services.map((item) {
            final name = item['name'] as String? ?? item.toString();
            final isSelected = _selectedAdditionalServices.contains(name);
            return InkWell(
              onTap: () => _toggleAdditionalService(name),
              borderRadius: BorderRadius.circular(24),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                decoration: BoxDecoration(
                  color: isSelected
                      ? AppColors.buttonPrimary.withOpacity(0.1)
                      : AppColors.cardBackground,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(
                    color: isSelected
                        ? AppColors.buttonPrimary
                        : Colors.transparent,
                    width: 2,
                  ),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      getIcon(name),
                      size: 18,
                      color: isSelected
                          ? AppColors.buttonPrimary
                          : AppColors.textSecondary,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      name,
                      style: AppTextStyles.bodySmall.copyWith(
                        color: isSelected
                            ? AppColors.buttonPrimary
                            : AppColors.textPrimary,
                        fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                      ),
                    ),
                  ],
                ),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildContactSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Контактные данные',
          style: AppTextStyles.heading3.copyWith(
            color: AppColors.textPrimary,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        TextFormField(
          controller: _phoneController,
          decoration: InputDecoration(
            labelText: 'Телефон',
            hintText: '+7 (999) 123-45-67',
            prefixIcon: const Icon(Icons.phone),
            filled: true,
            fillColor: AppColors.cardBackground,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(16),
              borderSide: BorderSide.none,
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(16),
              borderSide: BorderSide.none,
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(16),
              borderSide: const BorderSide(
                color: AppColors.buttonPrimary,
                width: 2,
              ),
            ),
          ),
          keyboardType: TextInputType.phone,
          inputFormatters: [
            FilteringTextInputFormatter.digitsOnly,
          ],
          validator: (value) {
            if (value == null || value.trim().isEmpty) {
              return 'Введите номер телефона';
            }
            if (value.length < 10) {
              return 'Номер телефона слишком короткий';
            }
            return null;
          },
        ),
      ],
    );
  }

  Widget _buildNotesSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Комментарий (необязательно)',
          style: AppTextStyles.heading3.copyWith(
            color: AppColors.textPrimary,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        TextFormField(
          controller: _notesController,
          decoration: InputDecoration(
            hintText: 'Дополнительные пожелания...',
            prefixIcon: const Icon(Icons.note),
            filled: true,
            fillColor: AppColors.cardBackground,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(16),
              borderSide: BorderSide.none,
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(16),
              borderSide: BorderSide.none,
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(16),
              borderSide: const BorderSide(
                color: AppColors.buttonPrimary,
                width: 2,
              ),
            ),
          ),
          maxLines: 3,
          textInputAction: TextInputAction.done,
        ),
      ],
    );
  }

  Widget _buildTotalPrice() {
    final total = _calculateTotalPrice();
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.buttonPrimary.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            'Итого',
            style: AppTextStyles.heading3.copyWith(
              color: AppColors.textPrimary,
              fontWeight: FontWeight.bold,
            ),
          ),
          Text(
            '${total.toStringAsFixed(0)} ₽',
            style: AppTextStyles.heading2.copyWith(
              color: AppColors.buttonPrimary,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildContinueButton() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        child: SizedBox(
          width: double.infinity,
          height: 52,
          child: ElevatedButton(
            onPressed: _handleContinue,
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.buttonPrimary,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              elevation: 0,
            ),
            child: Text(
              'Забронировать',
              style: AppTextStyles.bodyLarge.copyWith(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

