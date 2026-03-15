import 'package:flutter/material.dart';
import 'route_names.dart';
import 'page_transitions.dart';
import '../screens/auth/registration_screen.dart';
// import '../screens/auth/verify_email_screen.dart'; // Экран верификации почты больше не используется
import '../screens/auth/name_registration_screen.dart';
import '../screens/home/home_screen.dart';
import '../screens/profile/profile_screen.dart';
import '../screens/settings/settings_screen.dart';
import '../screens/menu/menu_spa_screen.dart';
import '../screens/service/service_detail_screen.dart';
import '../screens/booking/booking_screen.dart';
import '../screens/booking/booking_details_screen.dart';
import '../screens/booking/yclients_booking_screen.dart';
import '../screens/booking/master_selection_screen.dart';
import '../screens/booking/time_selection_screen.dart';
import '../screens/booking/booking_confirm_screen.dart';
import '../screens/auth/password_screen.dart';
import '../screens/bookings/bookings_screen.dart';
import '../screens/bookings/past_bookings_screen.dart';
import '../screens/loyalty/loyalty_screen.dart';
import '../models/service.dart';

class AppRouter {
  static Route<dynamic>? generateRoute(RouteSettings settings) {
    switch (settings.name) {
      case RouteNames.home:
        return SlideRightRoute(
          page: const HomeScreen(),
        );

      case RouteNames.settings:
        return SlideRightRoute(
          page: const SettingsScreen(),
        );

      case RouteNames.menuSpa:
        return SlideRightRoute(
          page: const MenuSpaScreen(),
        );

      case RouteNames.serviceDetail:
        final args = settings.arguments as Map<String, dynamic>?;
        final serviceId = args?['serviceId'] as int?;
        if (serviceId == null || serviceId <= 0) {
          return FadeRoute(
            page: Scaffold(
              appBar: AppBar(title: const Text('Ошибка')),
              body: const Center(
                child: Text('ID услуги не указан или неверен'),
              ),
            ),
          );
        }
        return SlideRightRoute(
          page: ServiceDetailScreen(
            serviceId: serviceId,
          ),
        );

      case RouteNames.booking:
        final args = settings.arguments as Map<String, dynamic>?;
        final serviceId = args?['serviceId'] as int?;
        if (serviceId == null || serviceId <= 0) {
          return FadeRoute(
            page: Scaffold(
              appBar: AppBar(title: const Text('Ошибка')),
              body: const Center(
                child: Text('ID услуги не указан или неверен'),
              ),
            ),
          );
        }
        return SlideUpRoute(
          page: BookingScreen(
            serviceId: serviceId,
            service: args?['service'] as Service?,
          ),
        );

      case RouteNames.yclientsBooking:
        final args = settings.arguments as Map<String, dynamic>?;
        final serviceId = args?['serviceId'] as int?;
        if (serviceId == null || serviceId <= 0) {
          return FadeRoute(
            page: Scaffold(
              appBar: AppBar(title: const Text('Ошибка')),
              body: const Center(
                child: Text('ID услуги не указан или неверен'),
              ),
            ),
          );
        }
        return SlideRightRoute(
          page: YClientsBookingScreen(
            serviceId: serviceId,
            service: args?['service'] as Map<String, dynamic>?,
          ),
        );

      case RouteNames.bookingDetails:
        final args = settings.arguments as Map<String, dynamic>?;
        final serviceId = args?['serviceId'] as int?;
        if (serviceId == null || serviceId <= 0) {
          return FadeRoute(
            page: Scaffold(
              appBar: AppBar(title: const Text('Ошибка')),
              body: const Center(
                child: Text('ID услуги не указан или неверен'),
              ),
            ),
          );
        }
        final appointmentDateTime = args?['appointmentDateTime'] as DateTime?;
        if (appointmentDateTime == null) {
          return FadeRoute(
            page: Scaffold(
              appBar: AppBar(title: const Text('Ошибка')),
              body: const Center(
                child: Text('Дата и время записи не указаны'),
              ),
            ),
          );
        }
        return SlideRightRoute(
          page: BookingDetailsScreen(
            serviceId: serviceId,
            service: args?['service'] as Service?,
            appointmentDateTime: appointmentDateTime,
          ),
        );

      case RouteNames.password:
        final args = settings.arguments as Map<String, dynamic>?;
        return SlideRightRoute(
          page: PasswordScreen(
            email: args?['email'] as String? ?? '',
            phone: args?['phone'] as String?,
          ),
        );


      case RouteNames.profile:
        return SlideRightRoute(
          page: const ProfileScreen(),
        );

      case RouteNames.bookings:
        return FadeRoute(
          page: const BookingsScreen(),
        );

      case RouteNames.loyalty:
        return SlideRightRoute(
          page: const LoyaltyScreen(),
        );

      case RouteNames.pastBookings:
        return SlideRightRoute(
          page: const PastBookingsScreen(),
        );

      case RouteNames.masterSelection:
        final args = settings.arguments as Map<String, dynamic>?;
        final serviceId = args?['serviceId'] as int?;
        if (serviceId == null || serviceId <= 0) {
          return FadeRoute(
            page: Scaffold(
              appBar: AppBar(title: const Text('Ошибка')),
              body: const Center(child: Text('ID услуги не указан')),
            ),
          );
        }
        return SlideRightRoute(
          page: MasterSelectionScreen(
            serviceId: serviceId,
            service: args?['service'] as Service?,
          ),
        );

      case RouteNames.timeSelection:
        final args = settings.arguments as Map<String, dynamic>?;
        final serviceId = args?['serviceId'] as int?;
        final staffId = args?['staffId'] as int?;
        final staffName = args?['staffName'] as String?;
        if (serviceId == null || staffId == null || staffName == null) {
          return FadeRoute(
            page: Scaffold(
              appBar: AppBar(title: const Text('Ошибка')),
              body: const Center(child: Text('Недостаточно данных')),
            ),
          );
        }
        return SlideRightRoute(
          page: TimeSelectionScreen(
            serviceId: serviceId,
            service: args?['service'] as Service?,
            staffId: staffId,
            staffName: staffName,
          ),
        );

      case RouteNames.bookingConfirm:
        final args = settings.arguments as Map<String, dynamic>?;
        final serviceId = args?['serviceId'] as int?;
        final staffId = args?['staffId'] as int?;
        final staffName = args?['staffName'] as String?;
        final datetime = args?['datetime'] as String?;
        if (serviceId == null || staffId == null || staffName == null || datetime == null) {
          return FadeRoute(
            page: Scaffold(
              appBar: AppBar(title: const Text('Ошибка')),
              body: const Center(child: Text('Недостаточно данных')),
            ),
          );
        }
        return SlideRightRoute(
          page: BookingConfirmScreen(
            serviceId: serviceId,
            service: args?['service'] as Service?,
            staffId: staffId,
            staffName: staffName,
            datetime: datetime,
          ),
        );

      case RouteNames.registration:
        return FadeRoute(
          page: const RegistrationScreen(),
        );

      // Экран verifyEmail убран: верификация почты отключена, регистрация проходит без кода
      // case RouteNames.verifyEmail: ...

      case RouteNames.nameRegistration:
        final args = settings.arguments as Map<String, dynamic>?;
        final email = args?['email'] as String?;
        final password = args?['password'] as String?;
        final phone = args?['phone'] as String?;
        
        if (email == null || email.isEmpty || 
            password == null || password.isEmpty) {
          return FadeRoute(
            page: Scaffold(
              appBar: AppBar(title: const Text('Ошибка')),
              body: const Center(
                child: Text('Email и пароль обязательны для регистрации'),
              ),
            ),
          );
        }
        
        return SlideRightRoute(
          page: NameRegistrationScreen(
            email: email,
            password: password,
            phone: phone ?? '',
          ),
        );

      default:
        return FadeRoute(
          page: const Scaffold(
            body: Center(child: Text('Page not found')),
          ),
        );
    }
  }
}

