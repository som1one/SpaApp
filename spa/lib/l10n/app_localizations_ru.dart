// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Russian (`ru`).
class AppLocalizationsRu extends AppLocalizations {
  AppLocalizationsRu([String locale = 'ru']) : super(locale);

  @override
  String get appTitle => 'SPA Salon';

  @override
  String get settings => 'Настройки';

  @override
  String get generalSettings => 'Общие настройки';

  @override
  String get notifications => 'Уведомления';

  @override
  String get support => 'Поддержка';

  @override
  String get contactUs => 'Свяжитесь с нами';

  @override
  String get appearance => 'Внешний вид';

  @override
  String get theme => 'Тема';

  @override
  String get light => 'Светлая';

  @override
  String get dark => 'Темная';

  @override
  String get language => 'Язык';

  @override
  String get appLanguage => 'Язык приложения';

  @override
  String get russian => 'Русский';

  @override
  String get english => 'English';

  @override
  String get security => 'Безопасность';

  @override
  String get biometricAuth => 'Биометрическая авторизация';

  @override
  String get biometricAuthSubtitle => 'Вход по отпечатку или Face ID';

  @override
  String get additional => 'Дополнительно';

  @override
  String get aboutApp => 'О приложении';

  @override
  String get privacyPolicy => 'Политика конфиденциальности';

  @override
  String get termsOfUse => 'Условия использования';

  @override
  String get clearCache => 'Очистить кэш';

  @override
  String get close => 'Закрыть';

  @override
  String get cancel => 'Отмена';

  @override
  String get clear => 'Очистить';

  @override
  String version(String version) {
    return 'Версия $version';
  }

  @override
  String get clearCacheConfirm => 'Вы уверены, что хотите очистить кэш?';

  @override
  String get cacheCleared => 'Кэш очищен';

  @override
  String get home => 'Главная';

  @override
  String get menu => 'Меню';

  @override
  String get bookings => 'Записи';

  @override
  String get profile => 'Профиль';

  @override
  String get loyalty => 'Лояльность';
}
