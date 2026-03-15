class Booking {
  final int id;
  final int userId;
  final String serviceName;
  final int? serviceDuration; // в минутах
  final int? servicePrice; // в копейках
  final String? masterName;
  final DateTime appointmentDateTime;
  final String status; // pending, confirmed, completed, cancelled
  final String? notes;
  final String? phone;
  final DateTime? cancelledAt;
  final String? cancelledReason;
  final DateTime createdAt;
  final DateTime updatedAt;

  Booking({
    required this.id,
    required this.userId,
    required this.serviceName,
    this.serviceDuration,
    this.servicePrice,
    this.masterName,
    required this.appointmentDateTime,
    required this.status,
    this.notes,
    this.phone,
    this.cancelledAt,
    this.cancelledReason,
    required this.createdAt,
    required this.updatedAt,
  });

  // Геттер для цены в рублях
  double? get priceInRubles {
    return servicePrice != null ? servicePrice! / 100.0 : null;
  }

  // Геттер для проверки, можно ли отменить
  bool get canCancel {
    return status != 'cancelled' && status != 'completed';
  }

  // Геттер для проверки, создана ли запись через YClients
  bool get isFromYClients {
    return notes != null && notes!.contains('YClients');
  }

  factory Booking.fromJson(Map<String, dynamic> json) {
    return Booking(
      id: json['id'] is int ? json['id'] : int.parse(json['id'].toString()),
      userId: json['user_id'] is int 
          ? json['user_id'] 
          : int.parse(json['user_id'].toString()),
      serviceName: json['service_name'] as String,
      serviceDuration: json['service_duration'] as int?,
      servicePrice: json['service_price'] as int?,
      masterName: json['master_name'] as String?,
      appointmentDateTime: DateTime.parse(json['appointment_datetime'] as String),
      status: json['status'] as String,
      notes: json['notes'] as String?,
      phone: json['phone'] as String?,
      cancelledAt: json['cancelled_at'] != null 
          ? DateTime.parse(json['cancelled_at'] as String)
          : null,
      cancelledReason: json['cancelled_reason'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'service_name': serviceName,
      'service_duration': serviceDuration,
      'service_price': servicePrice,
      'master_name': masterName,
      'appointment_datetime': appointmentDateTime.toIso8601String(),
      'status': status,
      'notes': notes,
      'phone': phone,
      'cancelled_at': cancelledAt?.toIso8601String(),
      'cancelled_reason': cancelledReason,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  Booking copyWith({
    int? id,
    int? userId,
    String? serviceName,
    int? serviceDuration,
    int? servicePrice,
    String? masterName,
    DateTime? appointmentDateTime,
    String? status,
    String? notes,
    String? phone,
    DateTime? cancelledAt,
    String? cancelledReason,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Booking(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      serviceName: serviceName ?? this.serviceName,
      serviceDuration: serviceDuration ?? this.serviceDuration,
      servicePrice: servicePrice ?? this.servicePrice,
      masterName: masterName ?? this.masterName,
      appointmentDateTime: appointmentDateTime ?? this.appointmentDateTime,
      status: status ?? this.status,
      notes: notes ?? this.notes,
      phone: phone ?? this.phone,
      cancelledAt: cancelledAt ?? this.cancelledAt,
      cancelledReason: cancelledReason ?? this.cancelledReason,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}

