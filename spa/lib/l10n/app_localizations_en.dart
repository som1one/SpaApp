// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appTitle => 'SPA Salon';

  @override
  String get settings => 'Settings';

  @override
  String get generalSettings => 'General Settings';

  @override
  String get notifications => 'Notifications';

  @override
  String get support => 'Support';

  @override
  String get contactUs => 'Contact us';

  @override
  String get appearance => 'Appearance';

  @override
  String get theme => 'Theme';

  @override
  String get light => 'Light';

  @override
  String get dark => 'Dark';

  @override
  String get language => 'Language';

  @override
  String get appLanguage => 'App Language';

  @override
  String get russian => 'Русский';

  @override
  String get english => 'English';

  @override
  String get security => 'Security';

  @override
  String get biometricAuth => 'Biometric Authentication';

  @override
  String get biometricAuthSubtitle => 'Login with fingerprint or Face ID';

  @override
  String get additional => 'Additional';

  @override
  String get aboutApp => 'About App';

  @override
  String get privacyPolicy => 'Privacy Policy';

  @override
  String get termsOfUse => 'Terms of Use';

  @override
  String get clearCache => 'Clear Cache';

  @override
  String get close => 'Close';

  @override
  String get cancel => 'Cancel';

  @override
  String get clear => 'Clear';

  @override
  String version(String version) {
    return 'Version $version';
  }

  @override
  String get clearCacheConfirm => 'Are you sure you want to clear the cache?';

  @override
  String get cacheCleared => 'Cache cleared';

  @override
  String get home => 'Home';

  @override
  String get menu => 'Menu';

  @override
  String get bookings => 'Bookings';

  @override
  String get profile => 'Profile';

  @override
  String get loyalty => 'Loyalty';
}
