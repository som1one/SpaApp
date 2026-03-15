/// Модель временного слота
class TimeSlot {
  final String date;
  final String time;
  final String datetime;
  final bool available;

  TimeSlot({
    required this.date,
    required this.time,
    required this.datetime,
    this.available = true,
  });

  factory TimeSlot.fromJson(Map<String, dynamic> json) {
    return TimeSlot(
      date: json['date'] as String? ?? '',
      time: json['time'] as String? ?? '',
      datetime: json['datetime'] as String? ?? '',
      available: json['available'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'date': date,
      'time': time,
      'datetime': datetime,
      'available': available,
    };
  }
}

