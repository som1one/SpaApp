import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../services/image_cache_manager.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../models/staff.dart';
import '../../models/service.dart';
import '../../services/booking_service.dart';
import '../../widgets/skeleton_loader.dart';
import '../../widgets/empty_state.dart';
import '../../routes/route_names.dart';

class MasterSelectionScreen extends StatefulWidget {
  final int serviceId;
  final Service? service;

  const MasterSelectionScreen({
    super.key,
    required this.serviceId,
    this.service,
  });

  @override
  State<MasterSelectionScreen> createState() => _MasterSelectionScreenState();
}

class _MasterSelectionScreenState extends State<MasterSelectionScreen> {
  final _bookingService = BookingService();
  List<StaffMember> _staff = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadStaff();
  }

  Future<void> _loadStaff() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final staff = await _bookingService.getAvailableStaff(widget.serviceId);
      if (!mounted) return;
      
      setState(() {
        _staff = staff;
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.backgroundLight,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, color: AppColors.textPrimary, size: 20),
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Text(
          'Выберите мастера',
          style: AppTextStyles.heading3.copyWith(
            fontFamily: 'Inter24',
            color: AppColors.textPrimary,
            fontWeight: FontWeight.w700,
          ),
        ),
        centerTitle: true,
      ),
      body: _isLoading
          ? _buildLoadingState()
          : _error != null || _staff.isEmpty
              ? EmptyState(
                  type: EmptyStateType.error,
                  error: _error,
                  onButtonPressed: _loadStaff,
                )
              : _buildContent(),
    );
  }

  Widget _buildLoadingState() {
    return ListView.separated(
      padding: const EdgeInsets.all(20),
      itemCount: 3,
      separatorBuilder: (_, __) => const SizedBox(height: 16),
      itemBuilder: (_, __) => const SkeletonLoader(width: double.infinity, height: 100),
    );
  }

  Widget _buildContent() {
    return ListView.separated(
      padding: const EdgeInsets.all(20),
      itemCount: _staff.length,
      separatorBuilder: (_, __) => const SizedBox(height: 16),
      itemBuilder: (context, index) {
        final staff = _staff[index];
        return _buildStaffCard(staff);
      },
    );
  }

  Widget _buildStaffCard(StaffMember staff) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () => _handleStaffSelection(staff),
        borderRadius: BorderRadius.circular(20),
        child: Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: AppColors.borderLight),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.02),
                blurRadius: 12,
                offset: const Offset(0, 3),
              ),
            ],
          ),
          child: Row(
            children: [
              // Аватар
              Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: LinearGradient(
                    colors: [
                      AppColors.buttonPrimary.withOpacity(0.15),
                      AppColors.buttonPrimary.withOpacity(0.05),
                    ],
                  ),
                ),
                child: staff.avatar != null && staff.avatar!.isNotEmpty
                    ? ClipOval(
                        child: CachedNetworkImage(
                          imageUrl: staff.avatar!,
                          fit: BoxFit.cover,
                          cacheManager: SpaImageCacheManager.instance,
                          placeholder: (_, __) => const Icon(
                            Icons.person,
                            size: 32,
                            color: AppColors.buttonPrimary,
                          ),
                          errorWidget: (_, __, ___) => const Icon(
                            Icons.person,
                            size: 32,
                            color: AppColors.buttonPrimary,
                          ),
                        ),
                      )
                    : const Icon(
                        Icons.person,
                        size: 32,
                        color: AppColors.buttonPrimary,
                      ),
              ),
              const SizedBox(width: 16),
              // Информация о мастере
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      staff.name,
                      style: AppTextStyles.bodyLarge.copyWith(
                        fontFamily: 'Inter24',
                        fontWeight: FontWeight.w600,
                        fontSize: 16,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    if (staff.specialization != null) ...[
                      const SizedBox(height: 4),
                      Text(
                        staff.specialization!,
                        style: AppTextStyles.bodySmall.copyWith(
                          fontFamily: 'Inter18',
                          color: AppColors.textSecondary,
                          fontSize: 13,
                        ),
                      ),
                    ],
                    if (staff.rating != null) ...[
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          const Icon(Icons.star, color: Color(0xFFFFD700), size: 16),
                          const SizedBox(width: 4),
                          Text(
                            staff.rating!.toStringAsFixed(1),
                            style: AppTextStyles.bodySmall.copyWith(
                              fontFamily: 'Inter24',
                              fontWeight: FontWeight.w600,
                              color: AppColors.textPrimary,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ],
                ),
              ),
              // Стрелка
              const Icon(
                Icons.chevron_right,
                color: AppColors.textSecondary,
                size: 24,
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _handleStaffSelection(StaffMember staff) {
    Navigator.of(context).pushNamed(
      RouteNames.timeSelection,
      arguments: {
        'serviceId': widget.serviceId,
        'service': widget.service,
        'staffId': staff.id,
        'staffName': staff.name,
      },
    );
  }
}

